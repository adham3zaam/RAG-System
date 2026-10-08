
import os
import shutil

from werkzeug.utils import secure_filename

from rag.pipeline import build_vector_database
from rag.pdf_to_markdown import pdf_to_markdown
from config.config import VECTOR_DB_PATH


UPLOAD_FOLDER = "data/documents"


def delete_old_files():

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    for filename in os.listdir(UPLOAD_FOLDER):

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if os.path.isfile(file_path):
            os.remove(file_path)


def delete_old_vector_database():

    vector_db_folder = os.path.dirname(
        VECTOR_DB_PATH
    )

    if os.path.exists(vector_db_folder):

        shutil.rmtree(
            vector_db_folder
        )


def upload_pdf(file):

    if not file:

        return {
            "success": False,
            "error": "No file uploaded"
        }


    if file.filename == "":

        return {
            "success": False,
            "error": "No file selected"
        }


    if not file.filename.lower().endswith(".pdf"):

        return {
            "success": False,
            "error": "Only PDF files are allowed"
        }


    filename = secure_filename(
        file.filename
    )


    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    # ==================================
    # 1. Delete old PDF / Markdown
    # ==================================

    delete_old_files()


    # ==================================
    # 2. Delete old FAISS database
    # ==================================

    delete_old_vector_database()


    # ==================================
    # 3. Save NEW PDF
    # ==================================

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(file_path)


    print("\n==============================")
    print("NEW PDF UPLOADED")
    print("==============================")

    print("Filename:", filename)
    print("Path:", file_path)


    # ==================================
    # 4. Convert PDF → Markdown
    # ==================================

    markdown_path = pdf_to_markdown(
        file_path
    )


    print("\n==============================")
    print("PDF CONVERTED TO MARKDOWN")
    print("==============================")

    print("Markdown:", markdown_path)


    # ==================================
    # 5. Build NEW FAISS database
    # ==================================

    build_vector_database(
        markdown_path
    )


    print("\n==============================")
    print("NEW VECTOR DATABASE READY")
    print("==============================")


    return {

        "success": True,

        "message":
            "PDF uploaded, converted to Markdown, and processed successfully",

        "filename":
            filename,

        "markdown_file":
            os.path.basename(markdown_path)
    }


def ask_question(question):

    from rag.chains import sequential_rag

    result = sequential_rag(
        question
    )

    return result
