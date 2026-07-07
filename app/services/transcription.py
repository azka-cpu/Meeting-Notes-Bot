from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def transcribe_audio(file_path: str, language: str | None = None) -> tuple[str, str]:
    with open(file_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            language=language,
            response_format="verbose_json",
        )
    return result.text.strip(), getattr(result, "language", None) or "unknown"