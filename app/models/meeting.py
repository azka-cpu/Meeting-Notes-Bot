from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Meeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    filename: str
    language: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[str] = None
    key_decisions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)