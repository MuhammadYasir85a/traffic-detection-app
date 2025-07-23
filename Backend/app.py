# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import tempfile
import os
from detection_utils import detect_vehicles, detect_vehicles_from_video

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

@app.route('/detect-image', methods=['POST'])
def detect_image():
    """
    Handle image upload and detection
    Returns: JSON with vehicle counts and processed image
    """
    try:
        if 'media' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        image_file = request.files['media']
        
        # Decode image from uploaded file
        image_np = cv2.imdecode(
            np.frombuffer(image_file.read(), np.uint8), 
            cv2.IMREAD_COLOR
        )
        
        if image_np is None:
            return jsonify({'error': 'Invalid image format'}), 400

        # Process the image using our detection function
        processed_frame, vehicle_count, count_by_type = detect_vehicles(image_np)

        # Encode processed image to base64 for frontend display
        _, buffer = cv2.imencode('.jpg', processed_frame)
        encoded_img = base64.b64encode(buffer).decode('utf-8')

        # Return results
        return jsonify({
            'success': True,
            'count': vehicle_count,
            'count_by_type': count_by_type,
            'processed_image': encoded_img,
            'message': f'Detected {vehicle_count} vehicles total'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Image processing failed: {str(e)}'
        }), 500

@app.route('/detect-video', methods=['POST'])
def detect_video():
    """
    Handle video upload and detection
    Returns: JSON with vehicle counts and processed final frame
    """
    try:
        if 'media' not in request.files:
            return jsonify({'error': 'No video uploaded'}), 400

        video_file = request.files['media']

        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(video_file.read())
            video_path = temp.name

        # Process the video using our detection function
        output_image, vehicle_count, count_by_type = detect_vehicles_from_video(video_path)

        # Clean up temporary file
        try:
            os.unlink(video_path)
        except:
            pass  # Ignore cleanup errors

        if output_image is None:
            return jsonify({'error': 'Video processing failed'}), 500

        # Encode final processed frame to base64
        _, buffer = cv2.imencode('.jpg', output_image)
        encoded_img = base64.b64encode(buffer).decode('utf-8')

        # Return results
        return jsonify({
            'success': True,
            'count': vehicle_count,
            'count_by_type': count_by_type,
            'processed_image': encoded_img,
            'message': f'Detected {vehicle_count} vehicles total in video'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Video processing failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Vehicle detection API is running',
        'available_endpoints': ['/detect-image', '/detect-video']
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Vehicle Detection API',
        'version': '2.0',
        'endpoints': {
            'POST /detect-image': 'Upload image for vehicle detection',
            'POST /detect-video': 'Upload video for vehicle detection',
            'GET /health': 'Health check'
        },
        'supported_formats': {
            'images': ['jpg', 'jpeg', 'png', 'bmp'],
            'videos': ['mp4', 'avi', 'mov', 'mkv']
        }
    })

if __name__ == '__main__':
    print("Starting Vehicle Detection API...")
    print("Available endpoints:")
    print("- POST /detect-image - Upload image for detection")
    print("- POST /detect-video - Upload video for detection") 
    print("- GET /health - Health check")
    print("- GET / - API information")
    
    app.run(host='0.0.0.0', port=5000, debug=True)