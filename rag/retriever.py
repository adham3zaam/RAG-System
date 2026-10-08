from config.config import TOP_K
from rag.vectorstore import load_vectorstore


def get_retriever():

    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": TOP_K
        }
    )

    return retriever