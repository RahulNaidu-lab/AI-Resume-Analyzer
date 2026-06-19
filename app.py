"""
AI-Powered Resume Analyzer
----------------------------
A Streamlit application that analyzes a candidate's resume against a job description
using an OpenAI-compatible LLM API.

Workflow:
  1. User uploads a PDF resume.
  2. PyPDF2 extracts the raw text from the PDF.
  3. User pastes a Job Description (JD).
  4. The extracted text + JD are sent to the LLM with a structured prompt.
  5. The LLM returns:
       - Skills found in the resume
       - Skills required by the JD but MISSING from the resume
       - An overall match score (0–100)
       - A brief recommendation paragraph
  6. Results are displayed with visual indicators.
"""

import json
import streamlit as st
import PyPDF2
from openai import OpenAI

# ─────────────────────────────────────────────────────────────
# Configuration – LLM client setup
# ─────────────────────────────────────────────────────────────
LLM_API_KEY  = "sk-emergent-cEd7cF42b271cC04fE"
LLM_BASE_URL = "https://integrations.emergentagent.com/llm"
LLM_MODEL    = "gpt-4o"

client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


# ──────────────────────────────────
# Helper: Extract text from a PDF file object
# ──────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    """
    Read every page of the uploaded PDF and concatenate the text.

    Args:
        uploaded_file: Streamlit UploadedFile (file-like object).

    Returns:
        A single string containing all extracted text, or an empty
        string if no text could be extracted.
    """
    reader = PyPDF2.PdfReader(uploaded_file)
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)
    return "\n".join(pages_text)


# ──────────────────────────────────
def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Ask the LLM to compare the resume against the job description.

    The prompt explicitly requests a JSON response so we can parse it
    reliably and display each section separately in the UI.

    Args:
        resume_text:      Plain text extracted from the resume PDF.
        job_description:  The job description provided by the user.

    Returns:
        A dictionary with keys:
            - resume_skills   (list[str])
            - missing_skills  (list[str])
            - match_score     (int, 0–100)
            - recommendation  (str)

    Raises:
        ValueError: If the LLM response cannot be parsed as valid JSON.
    """

    # System prompt: defines the role and output contract
    system_prompt = """You are an expert technical recruiter and career coach.
Your job is to rigorously compare a candidate's resume against a job description and
return structured, honest feedback.

Always respond with ONLY valid JSON — no markdown fences, no extra text.
Use exactly this structure:
{
  "resume_skills": ["skill1", "skill2", ...],
  "missing_skills": ["skill_a", "skill_b", ...],
  "match_score": <integer between 0 and 100>,
  "recommendation": "<two to three sentence paragraph>"
}

Guidelines:
- resume_skills  : All technical skills, tools, frameworks, and domain knowledge found in the resume.
- missing_skills : Skills explicitly or implicitly required by the JD that are absent from the resume.
- match_score    : A holistic percentage (0–100) of how well the resume fits the JD.
- recommendation : Actionable advice for the candidate to improve their profile for this role.
"""

    # User prompt: contains the actual data to analyse
    user_prompt = f"""--- RESUME ---
{resume_text}

--- JOB DESCRIPTION ---
{job_description}

Analyse the resume against the job description and return the JSON response."""

    # Call the LLM
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,   # Low temperature → more deterministic output
        max_tokens=1500,
    )

    raw_content = response.choices[0].message.content.strip()

    # Strip any accidental markdown code fences the model may add
    if raw_content.startswith("```"):
        raw_content = raw_content.split("```")[1]
        if raw_content.startswith("json"):
            raw_content = raw_content[4:]
        raw_content = raw_content.strip()

    # Parse JSON → Python dict
    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned non-JSON content. Raw response:\n{raw_content}"
        ) from exc

    return result


# ────────────────────────────
def score_color(score: int) -> str:
    """Return a CSS-friendly colour hex based on the match score."""
    if score >= 75:
        return "#27ae60"   # green  – strong match
    elif score >= 50:
        return "#f39c12"   # amber  – partial match
    else:
        return "#e74c3c"   # red    – weak match


# ──────────────────────
def main():
    # ── Page config ────────────
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide",
    )

    # ── Header ───
    st.markdown(
        """
        <h1 style='text-align:center; color:#2c3e50;'>
            📄 AI-Powered Resume Analyzer
        </h1>
        <p style='text-align:center; color:#7f8c8d; font-size:17px;'>
            Upload your resume and paste a job description to get instant,
            AI-driven feedback on your fit for the role.
        </p>
        <hr style='border:1px solid #ecf0f1;'>
        """,
        unsafe_allow_html=True,
    )

    # ── Two-column input layout ───
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("📎 Upload Resume (PDF)")
        uploaded_file = st.file_uploader(
            "Drag and drop your PDF resume here, or click to browse.",
            type=["pdf"],
            help="Only PDF files are supported.",
        )

        # Preview extracted text (collapsed by default)
        if uploaded_file is not None:
            with st.spinner("Extracting text from PDF…"):
                resume_text = extract_text_from_pdf(uploaded_file)

            if resume_text.strip():
                st.success(f"✅ Text extracted — {len(resume_text):,} characters across {uploaded_file.name}")
                with st.expander("👁️ Preview extracted resume text"):
                    st.text_area(
                        label="Extracted Text",
                        value=resume_text,
                        height=300,
                        disabled=True,
                    )
            else:
                st.error(
                    "⚠️ Could not extract text from this PDF. "
                    "It may be a scanned image. Please use a text-based PDF."
                )
                resume_text = ""
        else:
            resume_text = ""

    with col_right:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste the full job description here:",
            placeholder=(
                "e.g.\n"
                "We are looking for a Backend Engineer with 3+ years of experience in Python, "
                "Django, REST APIs, PostgreSQL, Docker, and AWS…"
            ),
            height=300,
        )

    # ── Analyze button ───
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button(
        "🔍  Analyze Resume",
        use_container_width=True,
        type="primary",
        disabled=(not uploaded_file or not job_description.strip()),
    )

    # ── Results section ───
    if analyze_btn:
        if not resume_text.strip():
            st.error("No text could be extracted from the uploaded PDF. Please upload a valid text-based PDF.")
            return
        if not job_description.strip():
            st.warning("Please paste a job description before analyzing.")
            return

        with st.spinner("🤖 Consulting the AI… this may take a few seconds…"): 
            try:
                results = analyze_resume(resume_text, job_description)
            except ValueError as exc:
                st.error(f"Analysis failed: {exc}")
                return
            except Exception as exc:
                st.error(f"An unexpected error occurred: {exc}")
                return

        # ── Score banner ───
        score     = int(results.get("match_score", 0))
        color     = score_color(score)
        label     = "Strong Match 🎉" if score >= 75 else ("Moderate Match 🤔" if score >= 50 else "Weak Match 😟")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='text-align:center; padding:20px; border-radius:12px;
                        background:{color}22; border:2px solid {color};'>
                <h2 style='color:{color}; margin:0;'>Match Score: {score} / 100</h2>
                <p style='color:{color}; font-size:18px; margin:4px 0 0;'>{label}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Three result columns ───
        r1, r2, r3 = st.columns([1, 1, 1], gap="large")

        with r1:
            st.markdown("### ✅ Skills Found in Resume")
            resume_skills = results.get("resume_skills", [])
            if resume_skills:
                for skill in resume_skills:
                    st.markdown(
                        f"<span style='display:inline-block;background:#d5f5e3;"
                        f"color:#1e8449;padding:4px 10px;border-radius:20px;"
                        f"margin:3px;font-size:14px;'>{skill}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No specific skills identified.")

        with r2:
            st.markdown("### ❌ Missing Skills")
            missing_skills = results.get("missing_skills", [])
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(
                        f"<span style='display:inline-block;background:#fadbd8;"
                        f"color:#922b21;padding:4px 10px;border-radius:20px;"
                        f"margin:3px;font-size:14px;'>{skill}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.success("No critical missing skills — great match!")

        with r3:
            st.markdown("### 💡 AI Recommendation")
            recommendation = results.get("recommendation", "No recommendation provided.")
            st.info(recommendation)

        # ── Summary metrics row ───
        st.markdown("<br><hr>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("📌 Skills in Resume", len(results.get("resume_skills", [])))
        m2.metric("⚠️ Missing Skills",   len(results.get("missing_skills", [])))
        m3.metric("🎯 Match Score",       f"{score}%")

    # ── Footer ───
    st.markdown(
        """
        <hr>
        <p style='text-align:center; color:#95a5a6; font-size:13px;'>
            Built with ❤️ using Streamlit · PyPDF2 · OpenAI GPT-4o
        </p>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()