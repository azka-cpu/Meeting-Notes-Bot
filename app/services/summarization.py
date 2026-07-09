import json
from dataclasses import dataclass
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are an assistant that summarizes meeting transcripts. "
    "Respond only with a JSON object containing exactly these keys: "
    "summary, action_items, key_decisions."
)
@dataclass
class SummaryResult:
    summary: str
    action_items: str
    key_decisions: str

def summarize_transcript(transcript: str) -> SummaryResult:
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        response_format={"type": "json_object"},
    )
    raw_output = response.choices[0].message.content
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        data = {"summary": raw_output, "action_items": "", "key_decisions": ""}
    return SummaryResult(
        summary=data.get("summary", ""),
        action_items=data.get("action_items", ""),
        key_decisions=data.get("key_decisions", ""),
    )
def ask_about_meeting(transcript: str, question: str) -> str:
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant answering questions about a specific meeting. "
                    "Use only the transcript below to answer. If the answer isn't in the "
                    "transcript, say so.\n\nTranscript:\n" + transcript
                ),
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content.strip()