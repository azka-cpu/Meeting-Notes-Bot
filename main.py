from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, meetings
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])

@app.get("/health")
def health_check():
    return {"status": "ok"}