# Backend API Project (Assessment Submission)

This is a backend-only FastAPI project for document ingestion and conversational RAG.

It supports:
- uploading `.pdf` and `.txt` files
- two chunking strategies (`fixed` and `sentence`)
- embedding generation + Pinecone storage
- Redis chat memory for multi-turn conversations
- interview booking extraction (name, email, date, time) using an LLM
- SQL storage for document metadata and booking records

## How This Matches the Task

### Document Ingestion API

- Endpoint: `POST /ingest/upload` (`api/ingestion.py`)
- Accepts `.pdf` and `.txt` files only
- Extracts text from uploaded file
- Applies selectable chunking strategy via form field `strategy`
- Generates embeddings (`services/embedder.py`)
- Stores vectors in Pinecone (`services/vector_store.py`)
- Saves document metadata in SQLAlchemy DB (`DocumentRecord`)

Chunking strategies implemented in `services/chunker.py`:
- `fixed` (fixed-size with overlap)
- `sentence` (sentence-based chunking)

### Conversational RAG API

- Endpoint: `POST /chat/message` (`api/conversation.py`)
- Custom RAG flow implemented in `services/rag_engine.py` (no `RetrievalQAChain`)
- Uses Redis for chat memory in `services/chat_memory.py`
- Includes previous conversation turns in the prompt for multi-turn handling

Interview booking support:
- Booking extraction logic in `services/booking.py`
- Uses an LLM prompt to extract `name`, `email`, `date`, and `time`
- Stores booking info in SQL via `BookingRecord` (`models/orm_models.py`)

### Constraints Followed

- No FAISS / Chroma (uses Pinecone)
- No UI (backend APIs only)
- No `RetrievalQAChain` (custom RAG pipeline)
- Modular structure with type hints across endpoints/services

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite (default local DB)
- Redis (chat memory)
- Pinecone (vector database)
- Gemini Embeddings (`gemini-embedding-001`)
- Groq (LLM for RAG response + booking extraction)

## Project Structure

- `main.py` - FastAPI app entrypoint
- `api/ingestion.py` - document ingestion endpoint
- `api/conversation.py` - chat + history endpoints
- `services/chunker.py` - fixed and sentence chunking
- `services/embedder.py` - Gemini embedding generation
- `services/vector_store.py` - Pinecone index creation/query/upsert
- `services/rag_engine.py` - custom RAG pipeline
- `services/chat_memory.py` - Redis chat memory
- `services/booking.py` - LLM booking extraction + DB save
- `models/orm_models.py` - SQLAlchemy models (`documents`, `bookings`)
- `core/config.py` - environment configuration via `BaseSettings`

## Environment Variables

Configuration is loaded from `.env` using `pydantic-settings` (`core/config.py`).
The sample file `.env.example` includes all required variables:

- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX`
- `REDIS_URL`
- `DATABASE_URL`

## Setup & Run

1. Create and activate a virtual environment
2. Install dependencies (`pip install -r requirements.txt`)
3. Copy `.env.example` to `.env` and fill in the keys/URLs
4. Start Redis
5. Run the API:

```bash
uvicorn main:app --reload
```

API docs:
- `http://127.0.0.1:8000/docs`

## Key Endpoints

- `POST /ingest/upload` - upload + chunk + embed + index + metadata save
- `POST /chat/message` - custom RAG chat + booking detection/persistence
- `GET /chat/history/{session_id}` - fetch Redis chat history
- `DELETE /chat/history/{session_id}` - clear Redis chat history
- `GET /health` - health check

## Example Requests

### Ingest a document

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/ingest/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@Leave application for 22th feb.pdf;type=application/pdf' \
  -F 'strategy=fixed'
```

`strategy` can be:
- `fixed`
- `sentence`

Example response:

```json
{
  "doc_id": "5e5a6c6b-7157-4f6d-8068-9725acb8ae9c",
  "filename": "Leave application for 22th feb.pdf",
  "chunks_created": 3,
  "strategy_used": "fixed"
}
```

### Chat (RAG)

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/chat/message' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_id": "test8",
  "message": "What is the document about?"
}'
```

Example response:

```json
{
  "session_id": "test8",
  "reply": "The document appears to be a formal application for leave due to bad health, submitted by Sampurna Poudyal to the Department of Computer Science at St. Xavier's College in Kathmandu.",
  "booking_detected": false
}
```

### Booking example (via chat)

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/chat/message' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_id": "test9",
  "message": "I want to book an interview. My name is Sampurna, email example@gmail.com, on 2026-02-23 at 10:00"
}'
```

If detected, the response includes:
- `booking_detected: true`

Example response:

```json
{
  "session_id": "test9",
  "reply": "Thank you for booking the interview. I have noted down the following details:\n\n- Name: Sampurna\n- Email: example@gmail.com\n- Date: 2026-02-23\n- Time: 10:00\n\nI will make sure to have everything ready for our interview on the scheduled date and time. If there are any changes or cancellations, please let me know as soon as possible.",
  "booking_detected": true
}
```

## Notes

- `.env` is ignored and not included in the repository
- `.env.example` is provided for setup
