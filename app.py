from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

# ==============================
# CONFIGURATION
# ==============================

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_IMAGE_SIZE = (1500, 1500)  # Resize large images

# Load lightweight model (important for Render free plan)
bg_session = new_session("u2netp")


# ==============================
# HELPER FUNCTION
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
        # Check file present
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]

        # Check empty filename
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Open image in memory
        input_image = Image.open(file.stream).convert("RGBA")

        # Resize if too large (memory safety)
        input_image.thumbnail(MAX_IMAGE_SIZE)

        # Remove background
        output_image = remove(input_image, session=bg_session)

        # Save result to memory buffer
        img_buffer = io.BytesIO()
        output_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        return send_file(
            img_buffer,
            mimetype="image/png",
            as_attachment=False
        )

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Processing failed"}), 500


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
