import json
from groq import Groq
from sqlalchemy.orm import Session
from models.orm_models import BookingRecord
from core.config import settings

client = Groq(api_key=settings.groq_api_key)

BOOKING_EXTRACTION_PROMPT = """
Extract interview booking info from this message if present.
Message: "{message}"

If booking info is present respond ONLY with JSON:
{{"name": "John", "email": "john@example.com", "date": "2025-03-15", "time": "10:00"}}

If not a booking request respond ONLY with:
{{"booking": false}}

JSON only, no extra text.
"""


async def detect_and_save_booking(
    message: str,
    session_id: str,
    db: Session
) -> dict | None:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": BOOKING_EXTRACTION_PROMPT.format(message=message)
        }],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if data.get("booking") is False:
        return None

    if all(k in data for k in ["name", "email", "date", "time"]):
        record = BookingRecord(
            session_id=session_id,
            name=data["name"],
            email=data["email"],
            date=data["date"],
            time=data["time"],
        )
        db.add(record)
        db.commit()
        return data

    return None