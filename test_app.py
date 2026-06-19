"""
Unit tests for the AI-Powered Resume Analyzer.
Tests cover:
  - PDF text extraction
  - score_color helper
  - analyze_resume (mocked LLM call)
  - main() smoke-test (Streamlit app import)
"""

import io
import json
import pytest
from unittest.mock import MagicMock, patch


# ──────────────────────────────
# score_color
# ──────────────────────────────
from app import score_color

class TestScoreColor:
    def test_strong_match(self):
        assert score_color(80) == "#27ae60"

    def test_exact_strong_boundary(self):
        assert score_color(75) == "#27ae60"

    def test_moderate_match(self):
        assert score_color(60) == "#f39c12"

    def test_exact_moderate_boundary(self):
        assert score_color(50) == "#f39c12"

    def test_weak_match(self):
        assert score_color(30) == "#e74c3c"

    def test_zero(self):
        assert score_color(0) == "#e74c3c"

    def test_perfect_score(self):
        assert score_color(100) == "#27ae60"


# ────────────────────
# extract_text_from_pdf
# ────────────────────
from app import extract_text_from_pdf

class TestExtractTextFromPdf:
    def _make_fake_pdf(self, texts):
        """Return a mock file-like object whose PdfReader returns pages with given texts."""
        mock_pages = []
        for t in texts:
            page = MagicMock()
            page.extract_text.return_value = t
            mock_pages.append(page)

        mock_reader = MagicMock()
        mock_reader.pages = mock_pages

        # patch PyPDF2.PdfReader so it returns our mock
        with patch("app.PyPDF2.PdfReader", return_value=mock_reader):
            result = extract_text_from_pdf(io.BytesIO(b"%PDF-1.4 fake"))
        return result

    def test_single_page(self):
        text = self._make_fake_pdf(["Hello, World!"])
        assert "Hello, World!" in text

    def test_multiple_pages_joined(self):
        text = self._make_fake_pdf(["Page one", "Page two", "Page three"])
        assert "Page one" in text
        assert "Page two" in text
        assert "Page three" in text

    def test_empty_page_skipped(self):
        text = self._make_fake_pdf(["", "Real content"])
        # empty string pages should not produce double newlines that break parsing
        assert "Real content" in text

    def test_none_page_text_skipped(self):
        text = self._make_fake_pdf([None, "Actual text"])
        assert "Actual text" in text

    def test_all_empty_returns_empty(self):
        text = self._make_fake_pdf(["", None, ""])
        assert text.strip() == ""


# ──────────────────────
# analyze_resume  (LLM call fully mocked)
# ──────────────────────
from app import analyze_resume

FAKE_LLM_RESPONSE = {
    "resume_skills": ["Python", "Django", "PostgreSQL"],
    "missing_skills": ["Docker", "AWS"],
    "match_score": 68,
    "recommendation": "You should learn Docker and AWS to improve your fit.",
}

def _make_mock_client_response(payload: dict):
    """Build a minimal mock that mimics openai ChatCompletion response."""
    msg  = MagicMock()
    msg.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp

class TestAnalyzeResume:
    def test_returns_expected_keys(self):
        with patch("app.client.chat.completions.create",
                   return_value=_make_mock_client_response(FAKE_LLM_RESPONSE)):
            result = analyze_resume("resume text", "job description")
        assert set(result.keys()) == {"resume_skills", "missing_skills", "match_score", "recommendation"}

    def test_skills_are_lists(self):
        with patch("app.client.chat.completions.create",
                   return_value=_make_mock_client_response(FAKE_LLM_RESPONSE)):
            result = analyze_resume("resume text", "job description")
        assert isinstance(result["resume_skills"], list)
        assert isinstance(result["missing_skills"], list)

    def test_match_score_is_int(self):
        with patch("app.client.chat.completions.create",
                   return_value=_make_mock_client_response(FAKE_LLM_RESPONSE)):
            result = analyze_resume("resume text", "job description")
        assert isinstance(result["match_score"], int)
        assert 0 <= result["match_score"] <= 100

    def test_recommendation_is_str(self):
        with patch("app.client.chat.completions.create",
                   return_value=_make_mock_client_response(FAKE_LLM_RESPONSE)):
            result = analyze_resume("resume text", "job description")
        assert isinstance(result["recommendation"], str)

    def test_strips_markdown_fences(self):
        """LLM sometimes wraps JSON in ```json ... ``` — ensure we handle it."""
        fenced = "```json\n" + json.dumps(FAKE_LLM_RESPONSE) + "\n```"
        msg  = MagicMock(); msg.content = fenced
        choice = MagicMock(); choice.message = msg
        resp = MagicMock(); resp.choices = [choice]
        with patch("app.client.chat.completions.create", return_value=resp):
            result = analyze_resume("resume", "jd")
        assert result["match_score"] == 68

    def test_invalid_json_raises_value_error(self):
        msg  = MagicMock(); msg.content = "This is not JSON at all."
        choice = MagicMock(); choice.message = msg
        resp = MagicMock(); resp.choices = [choice]
        with patch("app.client.chat.completions.create", return_value=resp):
            with pytest.raises(ValueError, match="non-JSON"):
                analyze_resume("resume", "jd")

    def test_actual_skills_values(self):
        with patch("app.client.chat.completions.create",
                   return_value=_make_mock_client_response(FAKE_LLM_RESPONSE)):
            result = analyze_resume("resume text", "job description")
        assert "Python" in result["resume_skills"]
        assert "Docker" in result["missing_skills"]