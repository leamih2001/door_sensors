from flask import Flask, jsonify
import cv2
from datetime import datetime
import os

app = Flask(__name__)

image_folder = "captured_images"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

cam = cv2.VideoCapture(0) 
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cam.isOpened():
    print("Could not open webcam.")
else: 
    print("Webcam successfully opened")

ret, frame = cam.read()

@app.route('/capture', methods=['POST'])
def capture_image():
    ret,frame =cam.read()

    if not ret:
        return jsonify({"status": "error", "message": "Failed to capture image"}), 500

   
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = os.path.join(image_folder, f"snapshot_{now}.jpg")
    cv2.imwrite(image_path, frame)

    return jsonify({"status": "success", "image_path": image_path}), 200
