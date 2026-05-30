# T&C Analyzer

AI-powered Terms & Conditions analyzer for PDFs, links, and document photos.

It extracts the text, chunks it for retrieval, scores risky clauses, answers follow-up questions with citations, exports a PDF report, and stores each analysis so it can be reopened later by document ID.

## Features

- Multi-input analysis:
  - PDF upload
  - webpage or PDF link
  - photos of printed documents
- RAG-based Q&A with cited source chunks
- Clause classification and risk scoring
- Risk overview dashboard + deep-dive review
- Downloadable PDF analysis report
- Reopen saved analyses later using the stored document ID

## Stack

- Backend: FastAPI
- Frontend: Streamlit
- Retrieval: FAISS
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- LLM:
  - Primary: Gemini 2.5 Flash
  - Fallback: FLAN-T5 small
- Storage: SQLite

## Project Structure

```text
app/
  db/                  sqlite + faiss helpers
  models/              request/response schemas
  services/            rag, parsing, persistence, reports
  main.py              FastAPI app
frontend/
  app.py               Streamlit UI
data/
  uploads/             uploaded files
  tnc_analyzer.db      SQLite database
```

## Local Setup

1. Use Python 3.12 and create a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy the env template.

```powershell
Copy-Item .env.example .env
```

3. Fill in at least:

- `GEMINI_API_KEY`
- `BACKEND_BASE_URL`
- `API_BASE_URL`
- `USE_GEMINI`
- `ENABLE_LOCAL_FALLBACK`

Optional storage settings:

- `DATA_DIR`
- `DATABASE_PATH`
- `UPLOAD_DIR`

## Run Locally

Backend:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
streamlit run frontend/app.py
```

Smoke tests:

```powershell
python -m unittest tests.test_public_mvp
```

Default local URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:8501`

## Important Environment Variables

```env
GEMINI_API_KEY=...
USE_GEMINI=true
ENABLE_LOCAL_FALLBACK=true
DATA_DIR=data
DATABASE_PATH=data/tnc_analyzer.db
UPLOAD_DIR=data/uploads
BACKEND_BASE_URL=http://127.0.0.1:8000
FRONTEND_BASE_URL=http://localhost:8501
API_BASE_URL=http://127.0.0.1:8000
```

## Deployment Notes

Recommended free-first split:

- Backend: Render or Railway
- Frontend: Streamlit Community Cloud

This repo includes:

- `render.yaml` for the backend service
- `requirements-backend.txt` for backend-only installs
- `frontend/requirements.txt` for Streamlit Community Cloud
- `.python-version` pinned to `3.12`

### Backend

Use:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set backend env vars:

- `GEMINI_API_KEY`
- `BACKEND_BASE_URL`
- `USE_GEMINI`
- `ENABLE_LOCAL_FALLBACK`
- `FRONTEND_BASE_URL`
- `API_BASE_URL`

Recommended production-ish values:

- `USE_GEMINI=true`
- `ENABLE_LOCAL_FALLBACK=false`

Render notes:

- Free web services have an ephemeral filesystem, so uploaded files and the local SQLite database are lost on restart or redeploy.
- If you want saved analyses to persist on Render, use a paid service with a persistent disk and point `DATA_DIR`, `DATABASE_PATH`, and `UPLOAD_DIR` at the mounted disk, or move the database to Postgres/object storage.
- `healthCheckPath` is set to `/health` in `render.yaml`.

### Frontend

Set frontend env vars:

- `BACKEND_BASE_URL`

Example:

- `BACKEND_BASE_URL=https://your-backend-domain`

Streamlit Community Cloud setup:

- Repository path / entrypoint: `frontend/app.py`
- Python version: `3.12`
- Dependencies: `frontend/requirements.txt`

## Current Limitations

- SQLite is good for prototyping, but Postgres is better for larger-scale production.
- The local fallback model is small and may be less accurate than Gemini.
- Image text extraction currently depends on Gemini.
- Saved analysis reopening currently uses document IDs rather than user accounts.

## Deployment Recommendation

For a lighter free-tier deployment:

- keep `USE_GEMINI=true`
- consider `ENABLE_LOCAL_FALLBACK=false`

That avoids loading the FLAN-T5 fallback model unless you explicitly want it.

## Resume-Friendly Summary

Built an AI-powered Terms & Conditions Analyzer using FastAPI, Streamlit, FAISS, and transformer embeddings. Implemented clause-level risk scoring, citation-grounded RAG Q&A, PDF report export, and multi-input document analysis across PDFs, links, and document photos.
