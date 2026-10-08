
from rag.loader import load_document
from rag.splitter import split_documents
from rag.vectorstore import create_vectorstore


def build_vector_database(file_path):

    print("================================")
    print("BUILDING VECTOR DATABASE")
    print("FILE:", file_path)
    print("================================")

    documents = load_document(file_path)

    print("Loaded documents:", len(documents))

    chunks = split_documents(documents)

    print("Created chunks:", len(chunks))

    vectorstore = create_vectorstore(chunks)

    print("Vector database created successfully.")

    return vectorstore
