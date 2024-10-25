import cv2
from websockets.sync.client import connect
from datetime import datetime
import threading
import time

from flask import Flask, request, jsonify

sensorStatus = "None"
status_lock = threading.Lock()

app = Flask(__name__)

@app.route('/checkSensor', methods=['POST'])
def process_event():
    global sensorStatus
    with status_lock:
        current_status = sensorStatus
        sensorStatus = "None"

    print(f"Returning status: {current_status}")
    return jsonify({"sensorStatus": "success", "result": current_status}), 200
       
def websocket_connect():
    global sensorStatus
    print ("Connecting to the websocket...")

    with connect("ws://192.168.0.103:80") as websocket:
        print("Connected to websocket")
        while True:
            websocket.send("Hello world!")
            while True:
                try:
                    message = websocket.recv()
                    if message:
                        print(f"Received: {message}")
                        with status_lock:
                            sensorStatus = message
                        print(f"Sensorstatus updated to: {message}")
                    else:
                        print("Nothing received")

                except TimeoutError:
                    if cv2.waitKey(1) == ord('q'):
                        break
                    continue
                break

                with status_lock:
                    print(f"Sensorstatus: {sensorstatus}")

                time.sleep(2)

        # Receiving the message
        # Possible sent values from ESP: "ENTRY" or "EXIT"
        print(f"Received: {message}")
        sensorStatus = message

threading.Thread(target=websocket_connect, daemon=True).start()
