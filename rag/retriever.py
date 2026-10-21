from functools import lru_cache

from config.config import TOP_K
from rag.vectorstore import load_vectorstore


@lru_cache(maxsize=1)
def get_retriever():
    vectorstore = load_vectorstore()

    return vectorstore.as_retriever(
        search_kwargs={"k": TOP_K}
    )