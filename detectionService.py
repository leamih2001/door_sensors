from flask import Flask, request, jsonify
import cv2
import os
import urllib.parse

image_folder = "captured_images"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/facedetection', methods=['POST'])
def detect_faces():
    image_path = urllib.parse.unquote(request.get_data().decode("utf-8")).replace("data=", "")

    image = cv2.imread(image_path)
    if image is None:
        return jsonify({"status": "error", "message": "Image not found"}), 400

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if face_cascade.empty():
        return jsonify({"status": "error", "message": "Failed to load Haar Cascade XML file"}), 500

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(40, 40), maxSize=(200, 200))

    for (x, y, w, h) in faces:
        start_point = (x, y)
        end_point = (x+w, y+h)
        color = (255, 0, 0)
        thickness = 2

        image = cv2.rectangle(image, start_point, end_point, color, thickness)

    image_path = image_path[:-4] + "_detectedFaces.jpg"
    cv2.imwrite(image_path, image)
    
    face_count = len(faces)
    faces_coords = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]

    return jsonify({"status": "success", "faces_detected": face_count, "faces_coords": faces_coords}), 200
