from flask import Flask, jsonify
import cv2
from datetime import datetime
import os

app = Flask(__name__)

image_folder = "captured_images"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

#Neu
cam = cv2.VideoCapture(0)
    
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

for _ in range(5):
    cam.read()

@app.route('/capture', methods=['POST'])
def capture_image():
    #cam = cv2.VideoCapture(0)

    #cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    #cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    ret,frame =cam.read()

    if not ret:
        return jsonify({"status": "error", "message": "Failed to capture image"}), 500

   
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = os.path.join(image_folder, f"snapshot_{now}.jpg")
    cv2.imwrite(image_path, frame)
    cam.release()

    return jsonify({"status": "success", "image_path": image_path}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
