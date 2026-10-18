
from flask import Blueprint, request, jsonify

from services.rag_service import (
    upload_pdf,
    ask_question,
    generate_study_material
)

rag_routes = Blueprint("rag", __name__)


@rag_routes.route("/upload", methods=["POST"])
def upload():
    print("\n==============================")
    print("UPLOAD REQUEST RECEIVED")
    print("==============================")

    file = request.files.get("file")

    if file:
        print("Uploaded filename:", file.filename)
    else:
        print("NO FILE RECEIVED")

    result = upload_pdf(file)

    print("Upload result:", result)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@rag_routes.route("/generate-study-material", methods=["POST"])
def generate_material():
    print("\n==============================")
    print("GENERATE STUDY MATERIAL REQUEST")
    print("==============================")

    try:
        result = generate_study_material()
        return jsonify(result), 200

    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400

    except Exception as exc:
        print("STUDY MATERIAL ERROR:", str(exc))

        return jsonify({
            "error": "Failed to generate study material.",
            "details": str(exc)
        }), 500


@rag_routes.route("/ask", methods=["POST"])
def ask():
    print("\n==============================")
    print("ASK REQUEST RECEIVED")
    print("==============================")

    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    try:
        result = ask_question(question)
        return jsonify(result), 200

    except Exception as exc:
        print("ASK ERROR:", str(exc))

        return jsonify({
            "error": "Failed to process question",
            "details": str(exc)
        }), 500
