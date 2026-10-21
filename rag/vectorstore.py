
import os
from functools import lru_cache

from langchain_community.vectorstores import FAISS

from config.config import VECTOR_DB_PATH
from rag.embeddings import get_embeddings


def create_vectorstore(chunks):
    if not chunks:
        raise ValueError("No document chunks were provided.")

    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings,
    )

    parent_dir = os.path.dirname(VECTOR_DB_PATH)

    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    vectorstore.save_local(VECTOR_DB_PATH)

    # Invalidate the cached vector database after saving the new index.
    load_vectorstore.cache_clear()

    return vectorstore


@lru_cache(maxsize=1)
def load_vectorstore():
    faiss_file = os.path.join(
        VECTOR_DB_PATH,
        "index.faiss",
    )

    pkl_file = os.path.join(
        VECTOR_DB_PATH,
        "index.pkl",
    )

    if not os.path.isfile(faiss_file):
        raise FileNotFoundError(
            f"FAISS index not found: {faiss_file}"
        )

    if not os.path.isfile(pkl_file):
        raise FileNotFoundError(
            f"FAISS metadata file not found: {pkl_file}"
        )

    return FAISS.load_local(
        VECTOR_DB_PATH,
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )
