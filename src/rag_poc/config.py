import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORAGE_DIR = PROJECT_ROOT / "storage"
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "models/gemini-3.6-flash"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4

INDEX_FILE = STORAGE_DIR / "index.faiss"
METADATA_FILE = STORAGE_DIR / "metadata.json"

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file")

def create_storage_folder():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
