from flask import Flask, request, jsonify
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from rapidfuzz import process
import torch
import os

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from React

# Load model and processor once
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Known medicine list
known_medicines = [
    "Paracetamol", "Amoxicillin", "Ibuprofen", "Cetirizine",
    "Metformin", "Aspirin", "Loratadine", "Omeprazole", "Doxycycline"
]

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = Image.open(request.files['image']).convert("RGB")

    # TrOCR
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Fuzzy match
    best_match = process.extractOne(generated_text, known_medicines)

    return jsonify({
        'medicine': best_match[0] if best_match else 'Unknown',
        'confidence': best_match[1] if best_match else 0
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
