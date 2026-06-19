# 📄 AI-Powered Resume Analyzer

A **Streamlit** web application that helps job seekers understand how well their resume matches a given job description using an OpenAI-compatible Large Language Model (LLM).

---

## 📌 Table of Contents
1. [What the Project Does](#what-the-project-does)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [How to Run](#how-to-run)
5. [How It Works (Step-by-Step)](#how-it-works-step-by-step)
6. [Viva Q&A Guide](#viva-qa-guide)

---

## What the Project Does

| Feature | Details |
|---|---|
| **Resume Upload** | Accepts a PDF resume from the user |
| **Text Extraction** | Uses **PyPDF2** to pull raw text out of the PDF |
| **JD Input** | User pastes the target Job Description |
| **LLM Analysis** | Sends both to GPT-4o via a structured prompt |
| **Results Display** | Shows matched skills, missing skills, a match score (0–100), and a recommendation |

---

## Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | Build the interactive web UI without writing HTML/CSS/JS |
| `PyPDF2` | Extract text from PDF files in Python |
| `openai` | Python SDK to call the OpenAI-compatible LLM API |

---

## Project Structure

```
resume-analyzer-v2/
│
├── app.py             ← Main Streamlit application
├── requirements.txt   ← Python dependency list
└── README.md          ← This file
```

---

## How to Run

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### Step 1 — Clone / Download the project
```bash
git clone <repo-url>
cd resume-analyzer-v2
```

### Step 2 — Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

Streamlit will open the app automatically in your default browser at **http://localhost:8501**.

---

## How It Works (Step-by-Step)

```
┌───────────────┐     ┌─────────────┐     ┌───────────────────┐     ┌───────📄 AI-Powered Resume Analyzer
│  User uploads│ --> │  PyPDF2     │ --> │  LLM API         │ --> │  Streamlit UI  │
│  PDF Resume  │     │  extracts   │     │  (GPT-4o)        │ --> │  shows results │
│  + pastes JD │     │  text       │     │  returns JSON    │     │  in columns    │
└───────────────┘     └─────────────┘     └───────────────────┘     └────────────────┘

### Detailed Flow

1. **Upload PDF** — `st.file_uploader()` accepts a `.pdf` file from the browser.
2. **Extract Text** — `PyPDF2.PdfReader` iterates over every page and calls `page.extract_text()`. All page text is joined into one string.
3. **Input JD** — `st.text_area()` captures the job description from the user.
4. **LLM Prompt** — The app constructs two messages for the chat model:
   - **System message**: Instructs the model to act as a technical recruiter and return *only* valid JSON.
   - **User message**: Contains the extracted resume text and the job description.
5. **Parse JSON** — The raw LLM response is parsed with `json.loads()` to extract four fields:
   - `resume_skills` — list of skills found in the resume
   - `missing_skills` — skills required by the JD but absent from the resume
   - `match_score` — integer 0–100
   - `recommendation` — textual advice for the candidate
6. **Display Results** — Streamlit renders the data using columns, colour-coded skill badges, and metric cards.

---

## Viva Q&A Guide

### Q1: Why did you choose Streamlit?
> Streamlit lets you build fully interactive data/ML web apps in pure Python — no front-end knowledge (HTML/CSS/JS) required. A single `streamlit run app.py` command serves the app, making it ideal for rapid prototyping and academic projects.

### Q2: What is PyPDF2 and why is it used?
> PyPDF2 is a Python library for reading and manipulating PDF files. Since the LLM works on plain text, we need to first convert the binary PDF into a readable string. PyPDF2's `PdfReader` class iterates over each page and extracts the underlying text layer.

### Q3: What happens if the PDF is a scanned image?
> PyPDF2 can only extract *text-layer* content. A scanned PDF (which is essentially an image) has no text layer, so `extract_text()` returns an empty string. To handle such cases, an OCR library like **pytesseract** would be needed to convert images to text first.

### Q4: How does the LLM analysis work?
> We use the `openai` Python SDK to call an OpenAI-compatible chat endpoint. We send a **system prompt** that defines the output contract (return JSON with specific keys) and a **user prompt** that contains the resume + JD. Setting `temperature=0.2` makes the model more deterministic and consistent.

### Q5: Why do you use a JSON response from the LLM?
> JSON is machine-readable, so we can reliably parse the model's output into a Python dictionary and display each field separately in the UI (e.g., skills as badges, score as a metric). Free-form text would be much harder to parse programmatically.

### Q6: What is the match score based on?
> The match score (0–100) is a holistic assessment by the LLM that considers: skill overlap between the resume and JD, relevant experience, domain knowledge, and any explicitly stated requirements. It is a qualitative judgment, not a simple keyword count.

### Q7: What are potential improvements?
> - Support for DOCX resumes using `python-docx` 
> - OCR support for scanned PDFs with `pytesseract` 
> - Saving analysis history to a database (SQLite / PostgreSQL)
> - Exporting results as a downloadable PDF report
> - Comparing multiple resumes against one JD (batch mode)

### Q8: How is the API key managed?
> In this prototype the key is hardcoded for simplicity. In a production application you should always store secrets in environment variables (`.env` file + `python-dotenv`) and never commit them to version control.

---

> **Tip for viva**: Walk the examiner through the `extract_text_from_pdf()` function, the `analyze_resume()` function (especially the prompt engineering), and the `main()` function's result rendering section. These three are the heart of the application.