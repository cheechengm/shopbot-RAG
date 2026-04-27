import os
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from rag_engine import RAGEngine

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

rag = RAGEngine()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
  return render_template("index.html", role="customer")

# Secret Admin View (Change 'manage-shop-admin-99' to whatever you want)
@app.route("/manage-shop-admin-99")
def admin_panel():
    return render_template("index.html", role="admin")

@app.route("/upload", methods=["POST"])
def upload_file():
    # Only allow uploads if they come from your secret URL
    if "manage-shop-admin-99" not in request.referrer:
        return jsonify({"error": "Unauthorized"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use PDF, TXT, or DOCX."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        chunk_count = rag.ingest_document(filepath, filename)
        return jsonify({
            "success": True,
            "message": f"✅ '{filename}' ingested successfully — {chunk_count} passages indexed.",
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = data.get("history", [])

    try:
        result = rag.query(user_message, history)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/documents", methods=["GET"])
def list_documents():
    docs = rag.list_documents()
    return jsonify({"documents": docs})


@app.route("/clear", methods=["POST"])
def clear_documents():
    if "manage-shop-admin-99" not in request.referrer:
        return jsonify({"error": "Unauthorized"}), 403
    
    rag.clear_all()
    return jsonify({"success": True})

@app.route("/load-sample", methods=["POST"])
def load_sample():
    """Load sample e-commerce data for demo purposes."""
    sample_path = "data_samples/sample_store_data.txt"
    if not os.path.exists(sample_path):
        return jsonify({"error": "Sample data not found"}), 404
    try:
        chunk_count = rag.ingest_document(sample_path, "sample_store_data.txt")
        return jsonify({
            "success": True,
            "message": f"✅ Sample store data loaded — {chunk_count} passages indexed."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    print("🚀 RAG Chatbot running at http://localhost:5000")
    app.run(debug=True, port=5000)
