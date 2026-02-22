from groq import Groq
from services.embedder import embed_query
from services.vector_store import query_pinecone
from services.chat_memory import get_chat_history, save_message
from core.config import settings

client = Groq(api_key=settings.groq_api_key)


async def run_rag_query(session_id: str, user_message: str) -> str:
    query_embedding = await embed_query(user_message)
    retrieved = query_pinecone(query_embedding, top_k=5)
    context = "\n\n".join([r["text"] for r in retrieved])
    history = get_chat_history(session_id)

    history_text = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are a helpful AI assistant. Answer using the context below.
If the user wants to book an interview, collect name, email, date and time.

Context:
{context}

Conversation so far:
{history_text}
User: {user_message}
Assistant:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    assistant_reply = response.choices[0].message.content

    save_message(session_id, "user", user_message)
    save_message(session_id, "assistant", assistant_reply)

    return assistant_reply