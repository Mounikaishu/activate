
import os
import warnings
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    warnings.warn(
        "⚠️ GEMINI_API_KEY not found! Set it in backend/.env file."
    )

# --- Model Configuration ---
MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.0-flash",
    "gemini-2.0-pro",
]

MAX_RETRIES = 2
RETRY_DELAY = 2  # seconds (doubles each retry)

# --- Chunking Configuration ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# --- ChromaDB ---
CHROMA_PERSIST_DIR = "./chroma_db"
