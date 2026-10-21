import os

from dotenv import load_dotenv


load_dotenv()


GROQ_API_KEY = os.getenv("YOUR_REAL_GROQ_KEY")


EMBEDDING_MODEL =os.getenv ("REAL_EMBEDDING_MODEL")

LLM_MODEL =os.getenv ("REAL_LLM_MODEL")


CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200


TOP_K = 3

VECTOR_DB_PATH = "vector_db/faiss_index"