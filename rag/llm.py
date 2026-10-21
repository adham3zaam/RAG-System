
from functools import lru_cache

from langchain_groq import ChatGroq
from config.config import GROQ_API_KEY, LLM_MODEL


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    if not LLM_MODEL:
        raise ValueError(
            "LLM_MODEL is missing from the .env file."
        )

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0,
    )
