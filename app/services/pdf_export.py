import os

from fpdf import FPDF

from app.core.config import settings
from app.models.meeting import Meeting


def generate_meeting_pdf(meeting: Meeting) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, meeting.filename, ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, meeting.summary or "")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Action Items", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, meeting.action_items or "")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Key Decisions", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, meeting.key_decisions or "")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    output_path = os.path.join(settings.UPLOAD_DIR, f"meeting_{meeting.id}.pdf")
    pdf.output(output_path)
    return output_path