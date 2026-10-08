import os

from langchain_community.vectorstores import FAISS

from config.config import VECTOR_DB_PATH
from rag.embeddings import get_embeddings


def create_vectorstore(chunks):

    embeddings = get_embeddings()

    print("================================")
    print("CREATING NEW FAISS DATABASE")
    print("================================")

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    os.makedirs(
        os.path.dirname(VECTOR_DB_PATH),
        exist_ok=True
    )

    vectorstore.save_local(
        VECTOR_DB_PATH
    )

    print("FAISS saved at:")
    print(VECTOR_DB_PATH)

    return vectorstore


def load_vectorstore():

    embeddings = get_embeddings()

    print("================================")
    print("LOADING FAISS DATABASE")
    print("================================")

    print("FAISS path:")
    print(VECTOR_DB_PATH)

    faiss_file = os.path.join(
        VECTOR_DB_PATH,
        "index.faiss"
    )

    pkl_file = os.path.join(
        VECTOR_DB_PATH,
        "index.pkl"
    )

    print("FAISS file:", faiss_file)
    print("FAISS exists:", os.path.exists(faiss_file))

    print("PKL file:", pkl_file)
    print("PKL exists:", os.path.exists(pkl_file))

    if not os.path.exists(faiss_file):
        raise FileNotFoundError(
            "No FAISS database found. Please upload a PDF first."
        )

    vectorstore = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("FAISS database loaded successfully.")

    return vectorstore