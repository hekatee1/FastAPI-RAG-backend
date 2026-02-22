from typing import Literal
import re

ChunkStrategy = Literal["fixed", "sentence"]


def chunk_by_fixed_size(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:
    """
    Strategy 1: Fixed-size chunking with overlap.
    Splits text every N characters, with some overlap to preserve context.
    Simple and fast. Good for uniform documents.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap  # move forward, keeping overlap
    return chunks


def chunk_by_sentence(
    text: str,
    max_sentences_per_chunk: int = 5
) -> list[str]:
    """
    Strategy 2: Sentence-based chunking.
    Splits on sentence boundaries. Better for preserving meaning.
    Good for QA and conversational use cases.
    """
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    for i in range(0, len(sentences), max_sentences_per_chunk):
        chunk = " ".join(sentences[i:i + max_sentences_per_chunk])
        if chunk:
            chunks.append(chunk)
    return chunks


def chunk_text(
    text: str,
    strategy: ChunkStrategy = "fixed",
    **kwargs
) -> list[str]:
    """Main entry point - selects strategy based on parameter."""
    if strategy == "fixed":
        return chunk_by_fixed_size(text, **kwargs)
    elif strategy == "sentence":
        return chunk_by_sentence(text, **kwargs)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")