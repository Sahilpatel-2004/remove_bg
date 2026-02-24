from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

# IMPORTANT FIX: Load the "pocket" version of the model (u2netp)
# This is much smaller and prevents the 502 Out-Of-Memory error on Render
bg_session = new_session("u2netp")

@app.route("/")
def home():
    return "Background Remover API Running"

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image"}), 400

        file = request.files["image"]
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Read the image directly into memory (NO saving to disk)
        input_image = Image.open(file.stream).convert("RGBA")
        
        # Remove background using the memory-friendly session
        output_image = remove(input_image, session=bg_session)
        
        # Save output image to a memory buffer to send it straight back
        img_buffer = io.BytesIO()
        output_image.save(img_buffer, format='PNG')
        img_buffer.seek(0) # Reset buffer position

        return send_file(img_buffer, mimetype="image/png")

    except Exception as e:
        print(f"Error Processing Image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
