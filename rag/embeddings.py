
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from config.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    if not EMBEDDING_MODEL:
        raise ValueError(
            "EMBEDDING_MODEL is missing from the .env file."
        )

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
