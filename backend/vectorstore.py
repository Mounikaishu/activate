"""
Placement Reality Check — ChromaDB vectorstore for session-based resume/JD storage.
"""

import chromadb
from config import CHROMA_PERSIST_DIR

client = chromadb.Client()


def _collection_name(session_id: str, doc_type: str) -> str:
    """Generate a collection name for a session + document type."""
    safe_id = session_id.replace("-", "_")[:32]
    return f"{doc_type}_{safe_id}"


def store_chunks(session_id: str, chunks: list[str], doc_type: str = "resume"):
    """
    Store document chunks in a session-specific ChromaDB collection.
    doc_type: 'resume' or 'jd'
    """
    coll_name = _collection_name(session_id, doc_type)

    # Delete existing collection if present
    try:
        client.delete_collection(coll_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(coll_name)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{doc_type}_{i}"]
        )

    print(f"✅ Stored {len(chunks)} {doc_type} chunks for session {session_id[:8]}...")


def retrieve_chunks(session_id: str, query: str, doc_type: str = "resume", k: int = 5) -> list[str]:
    """Retrieve most relevant chunks for a query from a session collection."""
    coll_name = _collection_name(session_id, doc_type)

    try:
        collection = client.get_or_create_collection(coll_name)
        count = collection.count()
        if count == 0:
            return []
        results = collection.query(
            query_texts=[query],
            n_results=min(k, count)
        )
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        print(f"⚠️ Retrieval error for {coll_name}: {e}")
        return []


def clear_session(session_id: str):
    """Delete all collections for a session."""
    for doc_type in ["resume", "jd"]:
        coll_name = _collection_name(session_id, doc_type)
        try:
            client.delete_collection(coll_name)
        except Exception:
            pass
    print(f"🧹 Cleared session {session_id[:8]}...")
