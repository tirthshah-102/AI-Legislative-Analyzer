# AI Legislative Analyzer

AI Legislative Analyzer is a full-stack legal intelligence application for simplifying complex legislative PDF documents into citizen-friendly outputs.

It supports:
- deep AI summarization in plain language,
- multilingual output,
- legal Q&A grounded in uploaded document content,
- compliance and citation extraction,
- visual risk/timeline/entity analytics,
- side-by-side bill comparison,
- downloadable PDF reports,
- text-to-speech audio summaries,
- OCR fallback for scanned PDF pages.

This repository includes two app entry points:
- Flask web app with a modern browser dashboard (`main.py` + `static/`).
- Streamlit dashboard (`app.py`) for quick local use.

## Table of Contents

1. [Core Features](#core-features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [How It Works](#how-it-works)
5. [Setup](#setup)
6. [Run the App](#run-the-app)
7. [API Reference (Flask)](#api-reference-flask)
8. [Language and OCR Notes](#language-and-ocr-notes)
9. [Testing and Verification](#testing-and-verification)
10. [Troubleshooting](#troubleshooting)
11. [Security and Environment Variables](#security-and-environment-variables)
12. [Known Constraints](#known-constraints)

## Core Features

### 1. Intelligent PDF Ingestion
- Extracts text from digital PDFs using `pdfplumber`.
- Automatically applies OCR via `pytesseract` for scanned/image-only pages.
- Handles multi-page legal documents and merges extracted text into a single analysis context.

### 2. AI Summary Engine
- Generates structured, highly detailed legal summaries in simple language.
- Uses prompt-driven sectioning for:
  - objectives,
  - key provisions,
  - public impact,
  - compliance and penalties,
  - key dates and timelines.
- Tracks token efficiency metrics (original tokens, compressed tokens, compression ratio).

### 3. Multilingual Output
- Supports `English`, `Hindi`, and `Gujarati`.
- Uses AI generation + translation fallback path for non-English output.
- Available across summary, glossary, comparison, timeline/entity labels, and Q&A responses.

### 4. Legal Q&A Assistant
- Users can ask natural-language questions after document upload.
- Answers are constrained to uploaded document content (document-grounded behavior by prompt design).
- Includes suggested starter questions in the web UI for faster onboarding.

### 5. Compliance Intelligence
- Generates actionable compliance checklist items.
- Splits obligations into immediate and ongoing actions (as requested in prompts).
- Helps transform legal prose into operational to-do items.

### 6. Citation and Entity Extraction
- Extracts references to other acts/laws and provides short contextual explanations.
- Builds relationship data for entity mapping (for example, government to citizens/businesses).

### 7. Visual Analytics Dashboard
- Risk/complexity radar chart:
  - complexity,
  - burden,
  - legal risk,
  - rights/protection score.
- Timeline view of key legislative dates/milestones.
- Entity relationship graph visualization.

### 8. Bill Comparison Engine
- Compares two document versions.
- Highlights added and removed provisions.
- Returns structured markdown analysis suitable for policy review workflows.

### 9. Export and Accessibility
- Download summary as PDF report (Unicode-aware font handling for Indic scripts).
- Listen to generated summary via text-to-speech (`gTTS`).
- Browser dashboard includes dynamic tabs, loader states, and dark mode support.

## Tech Stack

### Backend
- Python
- Flask + Flask-CORS
- Streamlit (alternative app shell)
- Requests
- python-dotenv

### AI / NLP / Translation
- ScaleDown API (context compression + LLM workflow)
- Model configured in code: `gpt-4o`
- deep-translator (`GoogleTranslator`)

### Document and Media
- pdfplumber
- pytesseract
- Pillow
- fpdf2
- gTTS

### Frontend (Flask app)
- Vanilla JavaScript
- Tailwind CSS (CDN)
- Marked (markdown rendering)
- Chart.js (risk radar chart)
- D3.js (entity graph)

## Project Structure

```text
.
├── main.py                          # Flask API + static web app host
├── app.py                           # Streamlit dashboard app
├── requirements.txt                 # Python dependencies
├── static/
│   ├── index.html                   # Main web UI
│   ├── script.js                    # Frontend workflow and API calls
│   ├── style.css                    # Additional styling
│   └── fonts/
├── src/
│   └── utils/
│       ├── analyzer.py              # AI analysis orchestration
│       ├── compressor.py            # ScaleDown API client
│       ├── pdf_handler.py           # PDF + OCR extraction
│       └── report_gen.py            # PDF report generation
├── tmp/                             # Runtime temp output (uploads, audio, PDFs)
├── test_*.py                        # Functional checks and feature scripts
└── verify_*.py                      # Project verification scripts
```

## How It Works

1. User uploads a legislative PDF.
2. Backend extracts text via `pdfplumber` and OCR fallback when required.
3. Extracted content is passed to ScaleDown with task-specific prompts.
4. Analyzer returns summary + metrics + derived artifacts (glossary, risk, compliance, etc.).
5. Frontend requests additional analysis endpoints in parallel for tabs and visuals.
6. User can ask questions, compare versions, play audio summary, and export PDF report.

## Setup

### Prerequisites
- Python 3.8+
- Internet access (required for ScaleDown API and translation services)
- Windows/macOS/Linux supported

Optional but recommended:
- Tesseract OCR installed for scanned PDFs
- Unicode font availability on system for robust Hindi/Gujarati PDF export

### 1) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment

Create a `.env` file in project root:

```env
SCALEDOWN_API_KEY=your_api_key_here
```

Without a valid key, AI analysis endpoints will fail.

## Run the App

### Option A: Flask Web Dashboard (recommended)

```bash
python main.py
```

Then open:
- `http://localhost:5000`

### Option B: Streamlit Dashboard

```bash
streamlit run app.py
```

## API Reference (Flask)

Base URL: `http://localhost:5000`

### `POST /upload`
Uploads PDF and returns extracted text.

Request:
- multipart form with `file`

Response:
- `{ "status": "success", "text": "..." }`

### `POST /analyze`
Generates summary, metrics, glossary, and risk scores.

Request JSON:
- `text` (string)
- `language` (`English` | `Hindi` | `Gujarati`)

Response includes:
- `summary`
- `metrics`
- `glossary`
- `risk_data`

### `POST /compliance`
Returns compliance checklist markdown.

### `POST /citations`
Returns extracted legal citations and context.

### `POST /timeline`
Returns timeline event list for visualization.

### `POST /entities`
Returns entity relationship graph data.

### `POST /compare`
Compares two document texts (`text1`, `text2`) and returns diff analysis.

### `POST /ask`
Returns answer for user question based on uploaded text.

### `POST /download`
Generates and returns downloadable summary PDF.

### `POST /tts`
Returns base64-encoded MP3 audio generated from summary text.

## Language and OCR Notes

### OCR behavior
- OCR triggers when a PDF page has no machine-readable text.
- OCR quality depends on scan quality and Tesseract installation/language data.

### Font behavior for PDF export
- Report generation tries common Windows fonts including Nirmala and fallback fonts.
- Indic text rendering quality depends on installed fonts.

## Testing and Verification

Repository contains feature-level scripts such as:
- `test_ask.py`
- `test_chat.py`
- `test_compare.py`
- `test_summary.py`
- `test_translation.py`
- `test_visuals.py`
- `verify_project.py`
- `verify_pro_features.py`

Run with:

```bash
python <script_name>.py
```

Use these scripts to validate endpoint behavior and premium feature flows.

## Troubleshooting

### API returns errors from analysis endpoints
- Confirm `.env` exists and `SCALEDOWN_API_KEY` is valid.
- Check internet connectivity.
- Review backend console logs for upstream API error text.

### Uploaded PDFs produce empty text
- Confirm file is not encrypted.
- For scanned files, install and verify Tesseract.
- Retry with better scan quality.

### Audio generation fails
- Very long text can fail in TTS pipelines.
- The backend truncates text for stability; retry with shorter content if needed.

### Hindi/Gujarati PDF output issues
- Install Unicode fonts (for example Nirmala UI on Windows).
- Ensure font files are accessible to the runtime.

## Security and Environment Variables

- Never hardcode API keys in source files.
- Store secrets only in `.env` and keep that file out of version control.
- Do not expose raw legal documents publicly if they contain sensitive content.

## Known Constraints

- Some analysis outputs are heuristic-based where strict JSON formatting is not preserved by upstream responses.
- Translation quality can vary for long legal text or mixed-language documents.
- Comparison uses sentence-level diffing and may not capture semantic equivalence perfectly.
- Q&A strictness depends on model compliance with prompt constraints.

## License

No explicit license file is currently included in this repository. Add a license before public distribution.
