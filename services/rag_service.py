
import os
import shutil

from werkzeug.utils import secure_filename

from rag.pipeline import build_vector_database
from rag.pdf_to_markdown import pdf_to_markdown
from rag.chains import generate_summary, generate_questions
from config.config import VECTOR_DB_PATH


UPLOAD_FOLDER = "data/documents"


def delete_old_files():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)


def delete_old_vector_database():
    vector_db_folder = os.path.dirname(VECTOR_DB_PATH)

    if os.path.exists(vector_db_folder):
        shutil.rmtree(vector_db_folder)


def upload_pdf(file):
    if not file:
        return {
            "success": False,
            "error": "No file uploaded"
        }

    if not file.filename:
        return {
            "success": False,
            "error": "No file selected"
        }

    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "error": "Only PDF files are allowed"
        }

    filename = secure_filename(file.filename)

    if not filename:
        return {
            "success": False,
            "error": "Invalid filename"
        }

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Delete the previous document and vector database.
    delete_old_files()
    delete_old_vector_database()

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    print("\n==============================")
    print("NEW PDF UPLOADED")
    print("==============================")
    print("Filename:", filename)
    print("Path:", file_path)

    try:
        # Convert PDF to Markdown.
        markdown_path = pdf_to_markdown(file_path)

        if not markdown_path or not os.path.isfile(markdown_path):
            raise RuntimeError(
                "PDF conversion did not produce a Markdown file."
            )

        print("Markdown:", markdown_path)

        # Build the existing FAISS database.
        build_vector_database(markdown_path)

        print("\n==============================")
        print("NEW VECTOR DATABASE READY")
        print("==============================")

        return {
            "success": True,
            "message": (
                "PDF uploaded and processed successfully. "
                "You can now generate a summary and questions."
            ),
            "filename": filename,
            "markdown_file": os.path.basename(markdown_path)
        }

    except Exception as exc:
        print("UPLOAD PROCESSING ERROR:", str(exc))

        # Remove partial files if processing fails.
        delete_old_files()
        delete_old_vector_database()

        return {
            "success": False,
            "error": "Failed to process the PDF.",
            "details": str(exc)
        }


def generate_study_material():
    """
    Generate a summary and questions from the latest
    converted Markdown document.
    """

    if not os.path.isdir(UPLOAD_FOLDER):
        raise ValueError(
            "Please upload and process a PDF before generating study material."
        )

    markdown_files = [
        os.path.join(UPLOAD_FOLDER, filename)
        for filename in os.listdir(UPLOAD_FOLDER)
        if filename.lower().endswith(".md")
        and os.path.isfile(os.path.join(UPLOAD_FOLDER, filename))
    ]

    if not markdown_files:
        raise ValueError(
            "No processed Markdown document was found. Please upload the PDF again."
        )

    # Use the most recently modified Markdown document.
    markdown_path = max(
        markdown_files,
        key=os.path.getmtime
    )

    print("\n==============================")
    print("GENERATING STUDY MATERIAL")
    print("==============================")
    print("Markdown:", markdown_path)

    # Generate the summary and questions.
    summary = generate_summary(markdown_path)

    questions = generate_questions(markdown_path)

    return {
        "success": True,
        "summary": summary,
        "questions": questions
    }


def ask_question(question):
    from rag.chains import sequential_rag

    result = sequential_rag(question)

    return result
