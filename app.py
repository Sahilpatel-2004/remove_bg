from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io
import os
import uuid

app = Flask(__name__)
CORS(app)

# ==============================
# CONFIGURATION
# ==============================

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
UPLOAD_FOLDER = "static/outputs"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_IMAGE_SIZE = (1500, 1500)

API_KEY = "YOUR_SECRET_API_KEY"   # Change this

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lightweight model (best for Render free plan)
bg_session = new_session("u2netp")


# ==============================
# HELPER
# ==============================

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==============================
# ROUTES
# ==============================

@app.route("/")
def home():
    return jsonify({
        "message": "Background Remover API Running",
        "status": "success"
    })


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:
        # API KEY CHECK
        client_key = request.headers.get("x-api-key")
        if client_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Open image
        input_image = Image.open(file.stream).convert("RGBA")
        input_image.thumbnail(MAX_IMAGE_SIZE)

        # Remove background
        output_image = remove(input_image, session=bg_session)

        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save file
        output_image.save(output_path, format="PNG")

        # Generate full public URL
        image_url = request.host_url + f"static/outputs/{filename}"

        return jsonify({
            "status": "success",
            "image_url": image_url
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Processing failed"}), 500


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
