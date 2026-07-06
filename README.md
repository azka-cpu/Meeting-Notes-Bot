# Meeting-Notes-Bot
AI-powered meeting notes and summarization bot built with FastAPI, Whisper, and Groq.
# AI Meeting Notes & Summarization Bot
An AI-powered application that turns meeting audio or transcripts into structured, searchable notes. Upload a recording or a written transcript, and the system transcribes it (if needed), summarizes it, extracts key decisions and action items, stores everything, and lets you ask follow-up questions about any past meeting.
## Overview
Meetings generate a lot of unstructured audio and text that rarely gets revisited. This project automates the pipeline — from raw upload to a clean, searchable, chat-able summary — using Whisper for transcription and Groq's hosted LLM for summarization and Q&A.
## Project Flow
```
User uploads meeting audio (.mp3/.wav)
      or a written transcript (.txt/.docx/.pdf)
              ↓
          FastAPI API
              ↓
   Speech-to-Text (Whisper)        [audio only]
   or direct text extraction       [transcript files]
              ↓
          Transcript
              ↓
      AI Summarization (Groq)
              ↓
Summary + Action Items + Key Decisions
              ↓
        Store in PostgreSQL
              ↓
  Search, chat about it, or export to PDF
```
## Tech Stack
| Layer | Technology |
|---|---|
| Backend Framework | FastAPI |
| Speech-to-Text | Whisper |
| AI Summarization & Chat | Groq (hosted LLM) |
| Database | PostgreSQL (Supabase) |
| ORM | SQLModel |
| Validation | Pydantic |
| Authentication | JWT |
| File Uploads | FastAPI `UploadFile` |
| Frontend | Plain HTML/CSS/JS (`index.html`) |
## Core Features
- **Audio upload** — transcribes `.mp3`/`.wav` meeting recordings with Whisper, auto-detecting the spoken language (or forceable via `?language=xx`)
- **Transcript upload** — accepts pre-written `.txt`, `.docx`, `.pdf` transcripts, skipping transcription entirely
- **AI summarization** — generates a summary, action items, and key decisions via Groq
- **Meeting chat** — ask follow-up questions about any past meeting, answered from its transcript
- **Search** — find past meetings by matching text in their transcript or summary
- **PDF export** — download a formatted summary of any meeting
- **JWT authentication** — every meeting is scoped to its owner
- **Dashboard UI** — a 3-column interface (`index.html`) for uploading, browsing, and chatting with meetings
## Project Structure
```
MeetingNotesBot/
├── main.py
├── index.html
├── requirements.txt
├── .env
├── uploads/
│   └── .gitkeep
└── app/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── config.py
    │   └── security.py
    ├── db/
    │   ├── __init__.py
    │   └── session.py
    ├── models/
    │   ├── __init__.py
    │   ├── user.py
    │   └── meeting.py
    ├── schemas/
    │   ├── __init__.py
    │   ├── user.py
    │   └── meeting.py
    ├── api/
    │   ├── __init__.py
    │   ├── deps.py
    │   ├── auth.py
    │   └── meetings.py
    └── services/
        ├── __init__.py
        ├── transcription.py
        ├── summarization.py
        ├── text_extraction.py
        └── pdf_export.py
```
## File Reference
### `main.py`
Application entrypoint. Creates the `FastAPI` instance, attaches CORS middleware, registers a startup hook that calls `init_db()` to create database tables, and mounts the `auth` and `meetings` routers. Exposes `/health` for a quick status check.
### `index.html`
A standalone frontend — no build step, no framework. Handles login/register, uploading audio or transcripts, browsing meetings grouped by date, viewing a meeting's transcript and summary, asking follow-up questions, and downloading PDFs. Talks directly to the FastAPI backend via `fetch`.

### `app/core/config.py`
Defines the `Settings` class (Pydantic `BaseSettings`) that loads configuration from `.env`: `DATABASE_URL`, `JWT_SECRET_KEY`, `GROQ_API_KEY`, `GROQ_MODEL`, `WHISPER_MODEL`, `UPLOAD_DIR`.
### `app/core/security.py`
Password hashing (`hash_password`, `verify_password` via Passlib/bcrypt) and JWT handling (`create_access_token`, `decode_access_token`).
### `app/db/session.py`
Sets up the SQLModel database engine. `init_db()` creates all tables on startup. `get_session()` yields a per-request database session.
### `app/models/user.py`
SQLModel table for `User`: `id`, `email`, `hashed_password`, `is_active`.
### `app/models/meeting.py`
SQLModel table for `Meeting`: linked to `user_id`, stores `filename`, `transcript`, `summary`, `action_items`, `key_decisions`, and `created_at`.
### `app/schemas/user.py`
Pydantic request/response shapes for auth: `UserCreate`, `UserLogin`, `Token`.
### `app/schemas/meeting.py`
Pydantic response shapes: `MeetingResponse` (full detail), `MeetingListItem` (list view), `ChatRequest`/`ChatResponse` (meeting chat).
### `app/api/deps.py`
Shared dependencies: `get_db` (database session) and `get_current_user` (decodes the JWT and loads the current `User`).
### `app/api/auth.py`
- `POST /auth/register` — creates a user, returns a JWT
- `POST /auth/login` — verifies credentials, returns a JWT
### `app/api/meetings.py`
All routes protected by `get_current_user`:
- `POST /meetings/upload` — audio upload → Whisper → Groq → stored
- `POST /meetings/upload-transcript` — pre-written transcript upload → Groq → stored
- `GET /meetings/search?q=...` — search transcripts/summaries
- `GET /meetings/{id}` — fetch one meeting
- `POST /meetings/{id}/chat` — ask a question about a meeting
- `GET /meetings/{id}/pdf` — download a PDF summary
- `GET /meetings/` — list all meetings
### `app/services/transcription.py`
Wraps Whisper. `transcribe_audio(file_path)` returns the plain-text transcript of an audio file.
### `app/services/text_extraction.py`
Extracts plain text from `.txt`, `.docx` (via `python-docx`), and `.pdf` (via `pypdf`) transcript uploads.
### `app/services/summarization.py`
Wraps the Groq chat completions API.
- `summarize_transcript` — returns a `SummaryResult` with `summary`, `action_items`, `key_decisions`
- `ask_about_meeting` — answers a follow-up question using a meeting's transcript as context
### `app/services/pdf_export.py`
Generates a PDF (via `fpdf2`) containing a meeting's filename, summary, action items, and key decisions.
### Prerequisites
- Python 3.11
- A PostgreSQL database (e.g. a free Supabase project)
- A [Groq](https://console.groq.com) API key
- `ffmpeg` installed and on PATH (required by Whisper)
### Installation
```bash
git clone https://github.com/azka-cpu/Meeting-Notes-Bot.git
cd Meeting-Notes-Bot
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```
### Environment Variables
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile or any
WHISPER_MODEL=base
UPLOAD_DIR=uploads
```
### Run Locally
```bash
uvicorn main:app --reload
```
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: open `index.html` directly in a browser (it points at `http://127.0.0.1:8000` by default, editable from the UI)
## License
MIT
