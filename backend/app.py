from flask import Flask, request, jsonify
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from rapidfuzz import process
import torch
import os
import cv2
import numpy as np

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

    # Read and preprocess image
    file = request.files['image']
    in_memory_file = file.read()
    np_img = np.frombuffer(in_memory_file, np.uint8)
    cv_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur
    blurred = cv2.medianBlur(gray, 3)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )

    # Convert processed image to PIL
    pil_image = Image.fromarray(thresh).convert("RGB")

    # OCR with TrOCR
    pixel_values = processor(images=pil_image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Fuzzy match with known medicines
    best_match = process.extractOne(generated_text, known_medicines)

    return jsonify({
        'medicine': best_match[0] if best_match else 'Unknown',
        'confidence': best_match[1] if best_match else 0,
        'raw_text': generated_text
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
