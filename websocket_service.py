import cv2
from websockets.sync.client import connect
from datetime import datetime
import threading

from flask import Flask, request, jsonify

sensorStatus = "None"

app = Flask(__name__)

sensorStatus = "None"

@app.route('/checkSensor', methods=['POST'])
def process_event():
    global sensorStatus
    print(f"Returning status: {sensorStatus}")
    return jsonify({"sensorStatus": "success", "result": tempsensorStatus}), 200
       
def websocket_connect():
    global sensorStatus
    print ("Connecting to the websocket...")

    with connect("ws://192.168.0.103:80") as websocket:
        print("Connected to websocket")
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

threading.Thread(target=websocket_connect, daemon=True).start()

