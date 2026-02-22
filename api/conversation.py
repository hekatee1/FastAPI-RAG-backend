from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.rag_engine import run_rag_query
from services.booking import detect_and_save_booking
from services.chat_memory import clear_history, get_chat_history
from models.database import get_db

router = APIRouter(prefix="/chat", tags=["Conversational RAG"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    booking_detected: bool = False


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message. The system:
    - Retrieves relevant docs via RAG
    - Maintains conversation history via Redis
    - Detects interview booking intent and saves it
    """
    # Run RAG
    reply = await run_rag_query(request.session_id, request.message)

    # Check for booking
    booking = await detect_and_save_booking(request.message, request.session_id, db)

    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        booking_detected=booking is not None
    )


@router.get("/history/{session_id}")
def get_history(session_id: str):
    """Retrieve chat history for a session."""
    return {"session_id": session_id, "history": get_chat_history(session_id)}


@router.delete("/history/{session_id}")
def delete_history(session_id: str):
    """Clear chat history for a session."""
    clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}