# ResumeIQ — Python Backend

## Overview

This is the **Python backend** for ResumeIQ. It mirrors all functionality from the JavaScript frontend (`js/nlp.js`, `js/jobs.js`, `js/chat.js`, `js/app.js`) in Python, and adds **ML-ready hooks** for future integration with scikit-learn, NLTK, and more.

> **⚠️ This does NOT replace `server.js`.** The existing Node.js server continues to work as before. This Python backend runs alongside it on **port 5000** (Node.js runs on port 3000).

---

## File Structure

```
backend/
├── server.py          ★ Flask API server (runs on port 5000)
├── nlp_engine.py      ★ All NLP functions (mirrors js/nlp.js)
├── job_profiles.py      Job description profiles (mirrors js/jobs.js)
├── chat_handler.py      AI chat integration (mirrors js/chat.js)
├── doc_extractor.py     PDF/DOCX/TXT text extraction
├── ml_pipeline.py     ★ ML-ready functions (scikit-learn, NLTK)
├── requirements.txt     Python dependencies
├── __init__.py          Package init
└── README.md            ← This file
```

---

## Quick Start

```bash
# 1. Navigate to the backend directory
cd resumeiq/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python server.py
```

The server starts at **http://localhost:5000**.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/analyze` | Full NLP analysis pipeline |
| `POST` | `/api/chat` | AI chat (Groq / Llama 3.3 70B) |
| `POST` | `/api/extract` | Document text extraction |
| `POST` | `/api/ml/analyze` | scikit-learn TF-IDF analysis |
| `GET` | `/api/jobs` | List all job profiles |
| `GET` | `/api/jobs/<role>` | Get specific job profile |
| `GET` | `/app` | Serve frontend (standalone mode) |

### Example: Analyze a Resume

```bash
# With JSON
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python machine learning TensorFlow deep learning...",
    "job_role": "ML Engineer"
  }'

# With file upload
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@resume.pdf" \
  -F "job_role=ML Engineer"
```

### Example: Chat

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What should I improve first?",
    "session_id": "user123"
  }'
```

---

## JS ↔ Python Mapping

| JavaScript File | Python File | What It Does |
|-----------------|-------------|--------------|
| `js/nlp.js` | `nlp_engine.py` | Tokenize, stem, TF-IDF, cosine similarity, keyword overlap |
| `js/jobs.js` | `job_profiles.py` | Job profiles, fuzzy matching, aliases |
| `js/chat.js` | `chat_handler.py` | System context, Groq API, suggestions |
| `js/app.js` | `server.py` | Orchestration (pipeline + API routes) |
| `js/ui.js` | *(frontend only)* | DOM rendering stays in JavaScript |

---

## ML Hooks (Future Use)

Every file contains `[ML-HOOK]` comments showing where to swap in ML libraries. Key upgrade paths:

### 1. scikit-learn TF-IDF (in `ml_pipeline.py`)
```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)
```

### 2. NLTK Lemmatization (in `ml_pipeline.py`)
```python
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
```

### 3. Resume Scoring Classifier (in `ml_pipeline.py`)
```python
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)
```

### 4. Sentence Embeddings (in `ml_pipeline.py`)
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### 5. Named Entity Recognition (in `ml_pipeline.py`)
```python
import spacy
nlp = spacy.load('en_core_web_sm')
```

---

## Running Both Servers

```bash
# Terminal 1: Node.js (existing)
cd resumeiq
npm start                  # → http://localhost:3000

# Terminal 2: Python (new)
cd resumeiq/backend
python server.py           # → http://localhost:5000
```

The frontend on port 3000 can optionally be configured to talk to the Python backend on port 5000 for ML features.

---

## Self-Testing

Each module can be run independently to verify it works:

```bash
python nlp_engine.py       # Tests tokenize, stem, TF-IDF, cosine
python doc_extractor.py    # Tests document extraction
python ml_pipeline.py      # Tests sklearn pipeline
```
