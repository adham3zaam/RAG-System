from langchain_huggingface import HuggingFaceEmbeddings

from config.config import EMBEDDING_MODEL


def get_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    return embeddings