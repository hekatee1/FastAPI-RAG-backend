import uuid
import io
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import pypdf

from services.chunker import chunk_text, ChunkStrategy
from services.embedder import generate_embeddings
from services.vector_store import upsert_to_pinecone
from models.database import get_db
from models.orm_models import DocumentRecord

router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])


def extract_text_from_file(file: UploadFile) -> str:
    """Extract raw text from .pdf or .txt files."""
    content = file.file.read()

    if file.filename.endswith(".txt"):
        return content.decode("utf-8")

    elif file.filename.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )
    else:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt supported")


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF or TXT file")],
    strategy: Annotated[ChunkStrategy, Form()] = "fixed",
    db: Session = Depends(get_db),
):
    """
    Upload a document, chunk it, embed it, and store in Pinecone + DB.
    """
    # 1. Extract text
    text = extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    # 2. Chunk
    chunks = chunk_text(text, strategy=strategy)

    # 3. Generate embeddings
    embeddings = await generate_embeddings(chunks)

    # 4. Create unique IDs for each chunk
    doc_id = str(uuid.uuid4())
    vectors = [
        {
            "id": f"{doc_id}-chunk-{i}",
            "values": embedding,
            "metadata": {
                "doc_id": doc_id,
                "filename": file.filename,
                "chunk_index": i,
                "text": chunk,
                "strategy": strategy,
            }
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    # 5. Upsert to Pinecone
    upsert_to_pinecone(vectors)

    # 6. Save metadata to SQL DB
    record = DocumentRecord(
        id=doc_id,
        filename=file.filename,
        strategy=strategy,
        chunk_count=len(chunks),
    )
    db.add(record)
    db.commit()

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks_created": len(chunks),
        "strategy_used": strategy,
    }