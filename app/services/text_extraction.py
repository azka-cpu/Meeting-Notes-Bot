import os

import docx
from pypdf import PdfReader


def extract_text_from_file(file_path: str, filename: str) -> str:
    extension = os.path.splitext(filename)[1].lower()

    if extension == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    if extension == ".docx":
        document = docx.Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    if extension == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()

    raise ValueError(f"Unsupported transcript file format: {extension}")