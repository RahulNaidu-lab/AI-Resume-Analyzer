# 📄 AI-Powered Resume Analyzer

A professional **Streamlit** web application that helps job seekers optimize their resumes by matching them against specific job descriptions using Large Language Models (LLM).

---

## 🚀 Key Features

| Feature | Details |
|---|---|
| **Resume Upload** | Securely accepts and parses PDF resumes |
| **NLP Text Extraction** | Uses **PyPDF2** for robust text extraction from PDF layers |
| **Intelligent Matching** | Leverages GPT-4o to analyze skill overlap and semantic relevance |
| **Actionable Insights** | Provides a match score (0–100%), identifies missing keywords, and gives specific optimization advice |

---

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit (Python-based web framework)
- **PDF Processing:** PyPDF2
- **AI/NLP:** OpenAI GPT-4o API
- **Testing:** Pytest (19 unit tests for core logic)

---

## 📦 Project Structure

```
AI-Resume-Analyzer/
│
├── app.py             ← Main application logic & UI
├── requirements.txt   ← Dependency management
├── test_app.py        ← Unit testing suite
└── README.md          ← Documentation
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- OpenAI-compatible API Key

### Step 1 — Clone the project
```bash
git clone https://github.com/RahulNaidu-lab/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### Step 2 — Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3 — Run Application
```bash
streamlit run app.py
```

---

## 🧠 System Architecture

The application follows a modular pipeline:
1. **Data Ingestion:** Uploaded binary PDF data is converted to plain text.
2. **Contextual Analysis:** Resume text and Job Descriptions are passed to the LLM with a structured system prompt.
3. **Structured Output:** The LLM returns a JSON payload to ensure reliable data rendering.
4. **Visualization:** Data is visualized using metric cards and color-coded skill badges for high readability.

---

Built with ❤️ for better career opportunities.