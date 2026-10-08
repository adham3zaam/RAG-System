from rag.pipeline import build_vector_database


PDF_PATH = "data/documents/Horizon_Tours_Complete_Knowledge_Base_2025.pdf"


build_vector_database(PDF_PATH)