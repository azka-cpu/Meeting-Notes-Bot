from datetime import datetime
from pydantic import BaseModel

class MeetingResponse(BaseModel):
    id: int
    filename: str
    language: str | None
    transcript: str | None
    summary: str | None
    action_items: str | None
    key_decisions: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class MeetingListItem(BaseModel):
    id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str