import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.meeting import ChatRequest, ChatResponse, MeetingListItem, MeetingResponse
from app.services.pdf_export import generate_meeting_pdf
from app.services.summarization import ask_about_meeting, summarize_transcript
from app.services.text_extraction import extract_text_from_file
from app.services.transcription import transcribe_audio

router = APIRouter()

@router.post("/upload", response_model=MeetingResponse)
def upload_meeting(
    file: UploadFile,
    language: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith((".mp3", ".wav")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")

    upload_dir = "/tmp" if os.environ.get("VERCEL") else settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    transcript, detected_language = transcribe_audio(file_path, language=language)
    result = summarize_transcript(transcript)

    meeting = Meeting(
        user_id=current_user.id,
        filename=file.filename,
        language=detected_language,
        transcript=transcript,
        summary=result.summary,
        action_items=result.action_items,
        key_decisions=result.key_decisions,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    os.remove(file_path)
    return meeting

@router.post("/upload-transcript", response_model=MeetingResponse)
def upload_transcript(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith((".txt", ".docx", ".pdf")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")

    upload_dir = "/tmp" if os.environ.get("VERCEL") else settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    transcript = extract_text_from_file(file_path, file.filename)
    result = summarize_transcript(transcript)
    meeting = Meeting(
        user_id=current_user.id,
        filename=file.filename,
        transcript=transcript,
        summary=result.summary,
        action_items=result.action_items,
        key_decisions=result.key_decisions,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    os.remove(file_path)
    return meeting

@router.get("/search", response_model=list[MeetingListItem])
def search_meetings(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pattern = f"%{q}%"
    meetings = db.exec(
        select(Meeting).where(
            Meeting.user_id == current_user.id,
            (Meeting.transcript.ilike(pattern)) | (Meeting.summary.ilike(pattern)),
        )
    ).all()
    return meetings

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = db.get(Meeting, meeting_id)
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting

@router.post("/{meeting_id}/chat", response_model=ChatResponse)
def chat_about_meeting(
    meeting_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = db.get(Meeting, meeting_id)
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    answer = ask_about_meeting(meeting.transcript or "", payload.question)
    return ChatResponse(answer=answer)

@router.get("/{meeting_id}/pdf")
def get_meeting_pdf(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = db.get(Meeting, meeting_id)
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    pdf_path = generate_meeting_pdf(meeting)
    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))

@router.get("/", response_model=list[MeetingListItem])
def list_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meetings = db.exec(select(Meeting).where(Meeting.user_id == current_user.id)).all()
    return meetings