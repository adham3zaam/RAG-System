
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader


def load_document(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    # ==============================
    # PDF
    # ==============================

    if extension == ".pdf":

        loader = PyPDFLoader(file_path)

        documents = loader.load()

        return documents


    # ==============================
    # Markdown
    # ==============================

    elif extension == ".md":

        loader = TextLoader(
            file_path,
            encoding="utf-8"
        )

        documents = loader.load()

        return documents


    # ==============================
    # Unsupported file
    # ==============================

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )
