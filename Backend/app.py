# app.py code 
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import tempfile
from detection_utils import detect_vehicles, detect_vehicles_from_video

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

@app.route('/detect-image', methods=['POST'])
def detect_image():
    if 'media' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['media']
    image_np = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

    processed_frame, vehicle_count, count_by_type = detect_vehicles(image_np)

    _, buffer = cv2.imencode('.jpg', processed_frame)
    encoded_img = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        'count': vehicle_count,
        'count_by_type': count_by_type,
        'processed_image': encoded_img
    })

@app.route('/detect-video', methods=['POST'])
def detect_video():
    if 'media' not in request.files:
        return jsonify({'error': 'No video uploaded'}), 400

    video_file = request.files['media']

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        temp.write(video_file.read())
        video_path = temp.name

    output_image, vehicle_count, count_by_type = detect_vehicles_from_video(video_path)

    _, buffer = cv2.imencode('.jpg', output_image)
    encoded_img = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        'count': vehicle_count,
        'count_by_type': count_by_type,
        'processed_image': encoded_img
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

