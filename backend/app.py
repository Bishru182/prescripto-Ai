import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

# Roboflow API details
ROBOFLOW_API_URL = "https://serverless.roboflow.com/amoxicillin-detection/1?api_key=v5s0KND3F1yrMERWtXnE"

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    img_bytes = file.read()

    response = requests.post(
        ROBOFLOW_API_URL,
        files={"file": img_bytes},
        data={"name": file.filename}
    )

    data = response.json()
    
    prediction = data.get('predictions', [])
    if prediction:
        label = prediction[0]['class']
        confidence = prediction[0]['confidence']
        confidence_percent = confidence * 100
        # Set your threshold here
        CONFIDENCE_THRESHOLD = 50.0

        if confidence_percent < CONFIDENCE_THRESHOLD:
            label = "Unknown"
    else:
        label = "Unknown"
        confidence_percent = 0

    return jsonify({
        'medicine': label,
        'confidence': round(confidence_percent, 2)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
