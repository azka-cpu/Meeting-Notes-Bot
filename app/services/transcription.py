import whisper

from app.core.config import settings

_model = whisper.load_model(settings.WHISPER_MODEL)


def transcribe_audio(file_path: str, language: str | None = None) -> tuple[str, str]:
    result = _model.transcribe(file_path, language=language)
    return result["text"].strip(), result.get("language", "unknown")