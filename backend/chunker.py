"""
Placement Reality Check — Text chunking with overlap for semantic retrieval.
"""

from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
   
    chunk_size = chunk_size or CHUNK_SIZE
    overlap = overlap or CHUNK_OVERLAP

    words = text.split()
    chunks = []
    step = max(chunk_size - overlap, 1)

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks
