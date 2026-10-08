import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.config import CHUNK_SIZE, CHUNK_OVERLAP


def clean_documents(documents):

    for doc in documents:

        doc.page_content = re.sub(
            r"\s+",
            " ",
            doc.page_content
        ).strip()

    return documents


def split_documents(documents):

    documents = clean_documents(documents)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_documents(documents)

    return chunks