from flask import Blueprint, request, jsonify

from services.rag_service import upload_pdf, ask_question


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

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result), 200


@rag_routes.route("/ask", methods=["POST"])
def ask():

    print("\n==============================")
    print("ASK REQUEST RECEIVED")
    print("==============================")

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    print("Question:", question)

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    try:

        result = ask_question(question)

        return jsonify(result), 200

    except Exception as e:

        print("ASK ERROR:", str(e))

        return jsonify({
            "error": "Failed to process question",
            "details": str(e)
        }), 500