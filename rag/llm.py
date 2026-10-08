from langchain_groq import ChatGroq

from config.config import GROQ_API_KEY, LLM_MODEL


def get_llm():

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0
    )

    return llm