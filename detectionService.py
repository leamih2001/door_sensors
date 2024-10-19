from flask import Flask, request, jsonify
import cv2

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/facedetection', methods=['POST'])
def detect_faces():
    data = request.json
    image_path = data.get("image_path")

    image = cv2.imread(image_path)
    if image is None:
        return jsonify({"status": "error", "message": "Image not found"}), 400

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    cv2.imshow("Gray Image", gray)
    cv2.waitKey(0)
    
    if face_cascade.empty():
        return jsonify({"status": "error", "message": "Failed to load Haar Cascade XML file"}), 500

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))


    face_count = len(faces)
    faces_coords = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]

    return jsonify({"status": "success", "faces_detected": face_count, "faces": faces_coords}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)