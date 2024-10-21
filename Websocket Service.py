import cv2
from websockets.sync.client import connect
from datetime import datetime
import threading

from flask import Flask, request, jsonify

sensorStatus = "None"

app = Flask(__name__)

@app.route('/checkSensor', methods=['POST'])
def process_event():
    global sensorStatus
    tempsensorStatus=sensorStatus
    sensorStatus = "None"
    return jsonify({"sensorStatus": "success", "result": tempsensorStatus}), 200
       
flaskThread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
flaskThread.start()

with connect("ws://192.168.0.103:80") as websocket:
    while True:
        websocket.send("Hello world!")
        while True:
            try:
                message = websocket.recv(timeout=1)
            except TimeoutError:
                if cv2.waitKey(1) == ord('q'):
                    break
                continue
            break

        # Receiving the message
        # Possible sent values from ESP: "ENTRY" or "EXIT"
        print(f"Received: {message}")
        sensorStatus = message

        # Exit with 'q'/ STRG+C
        if cv2.waitKey(1) == ord('q'):
            break

