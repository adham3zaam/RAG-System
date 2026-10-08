import os

from dotenv import load_dotenv


load_dotenv()


# =========================
# Groq
# =========================

GROQ_API_KEY = os.getenv("YOUR_REAL_GROQ_KEY")


# =========================
# Models
# =========================

EMBEDDING_MODEL =os.getenv ("REAL_EMBEDDING_MODEL")

LLM_MODEL =os.getenv ("REAL_LLM_MODEL")


# =========================
# Text Splitting
# =========================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200


# =========================
# Retrieval
# =========================

TOP_K = 3


# =========================
# Vector Database
# =========================

VECTOR_DB_PATH = "vector_db/faiss_index"