import json
import redis
from core.config import settings

# Connect to Redis
r = redis.from_url(settings.redis_url, decode_responses=True)

MAX_HISTORY = 10  # keep last 10 turns


def get_chat_history(session_id: str) -> list[dict]:
    """Retrieve conversation history for a session."""
    raw = r.get(f"chat:{session_id}")
    if not raw:
        return []
    return json.loads(raw)


def save_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the session history and trim to MAX_HISTORY."""
    history = get_chat_history(session_id)
    history.append({"role": role, "content": content})
    # Keep only last N turns
    history = history[-MAX_HISTORY * 2:]  # each turn = user + assistant
    r.set(f"chat:{session_id}", json.dumps(history), ex=3600)  # 1hr expiry


def clear_history(session_id: str) -> None:
    r.delete(f"chat:{session_id}")