from pinecone import Pinecone, ServerlessSpec
from core.config import settings

pc = Pinecone(api_key=settings.pinecone_api_key)

def get_index():
    index_name = settings.pinecone_index
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=3072,  # gemini-embedding-001 dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)


def upsert_to_pinecone(vectors: list[dict]) -> None:
    """Insert vectors (id, values, metadata) into Pinecone."""
    index = get_index()
    index.upsert(vectors=vectors)


def query_pinecone(
    query_vector: list[float],
    top_k: int = 5
) -> list[dict]:
    """Retrieve top-k similar chunks from Pinecone."""
    index = get_index()
    result = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return [
        {"text": match["metadata"]["text"], "score": match["score"]}
        for match in result["matches"]
    ]