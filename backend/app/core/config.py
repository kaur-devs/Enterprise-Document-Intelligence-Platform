import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./knowledgehub.db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.72"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
MAX_UPLOAD_SIZE_MB = float(os.getenv("MAX_UPLOAD_SIZE_MB", "10.0"))
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
CHAT_LATENCY_BUDGET_MS = int(os.getenv("CHAT_LATENCY_BUDGET_MS", "5000"))
SEARCH_LATENCY_BUDGET_MS = int(os.getenv("SEARCH_LATENCY_BUDGET_MS", "1000"))