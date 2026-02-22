from google import genai
from google.genai import types
from core.config import settings

client = genai.Client(
    api_key=settings.gemini_api_key,
    http_options={"api_version": "v1beta"}
)

EMBEDDING_MODEL = "gemini-embedding-001"


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        embeddings.append(result.embeddings[0].values)
    return embeddings


async def embed_query(text: str) -> list[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return result.embeddings[0].values
