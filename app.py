from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "Background Remover API Running"


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    file = request.files["image"]

    unique_name = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, unique_name + ".png")
    output_path = os.path.join(OUTPUT_FOLDER, unique_name + ".png")

    file.save(input_path)

    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_path)

    return send_file(output_path, mimetype="image/png")


# ✅ Render Port Binding Fix
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
