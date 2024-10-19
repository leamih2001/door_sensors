# door_sensors (Documentation for Access Control System)
1. Introduction
The aim of the implemented system is to monitor entry and exit into a room, in this case the laboratory, using infrared light barriers, whereby photos are taken and facial recognition is then carried out. In this case, there are three main services that are orchestrated by the process engine. Communication between the services does not take place directly, but is coordinated by the CPEE, whereby the CPEE server calls scripts on the PC via http, which ensures, among other things, loose coupling and reusability.

2. Overview components
The hardware components are as follows:
Infrared light barriers (LEFRIKO E18-D80NK), development board (ESP32-WROOM-32E) & webcam (Logitech Streamcam).
The ESP32 monitors the infrared light barriers and sends events to a central WebSocket client. There are three Flask-based services, which are:
Sensor Data Retrieval, Image Capture and Face Recognition.

3. Hardware-Setup
The ESP32 monitors four infrared light barriers, each of which detects people entering or leaving the laboratory. Two of them are mounted higher up, the other two lower down on the door frame to counteract the physical restrictions. The two brackets in which the sensors are located were produced using 3D printing, whereby there is a small opening underneath next to the two holes for the light barriers in which the ESP can be attached. The Arduino code regulates the behavior of the sensors and a small time delay was implemented to avoid overdetection. As soon as a sensor is triggered by a person entering or leaving the room, this event is sent to a websocket client via a message (“ENTRY” or “EXIT”).

4. Software architecture
The process engine generally queries the sensor data service to determine whether an entry or exit has been detected. Based on this information, it triggers the services to perform the corresponding actions.

4.1. Sensor data service: This receives the events from the ESP via a web socket client and provides a REST endpoint /checkSensor to query the current sensor data status
4.2. Image capture service: Here, the image is captured with the webcam when an entry or exit is detected. In addition, OpenCV is used here to achieve better quality for the subsequent face detection. The images are saved in a local directory and the REST endpoint /capture is used to trigger the image capture.
4.3. Face recognition service: For this service, OpenCV and a pre-trained hair cascade model are used to recognize faces. The REST endpoint /face detection is used to transmit the image for recognition

5. Procedure
5.1. Access detection: A person enters (or leaves) the laboratory and thus breaks through the light barrier. This event is registered in the ESP32 and sent to the sensor data service via a WebSocket.
5.2. Image capture: If “ENTRY” or “EXIT” is detected, the image capture service is called to capture an image of the person
5.3. Face recognition: The captured image is forwarded to the face recognition service, which checks whether there are faces and, if so, where and how many there are on the captured image.
The process engine coordinates the interactions between the services by querying events and initiating the next steps based on them

6. Implementation details
6.1. Arduino code: This establishes a WLAN connection and starts a new web socket server. In addition, the statuses of the infrared light barriers are read out and their logic is implemented. Depending on which light barrier (outer or inner) is broken through first, an entry or exit can be distinguished. At the end, the detected events are sent to the websocket client.
6.2. Python services
6.2.1. Sensor data service: Implements communication via websockets with the ESP32 and provides a REST interface to query the sensor status
6.2.2. Image acquisition service: Uses OpenCV to capture images and store them in the local file system
6.2.3. Face Recognition Service: Processes the captured images and performs face recognition
6.3. Threading: The Flask web server runs in parallel with the other processes that respond to sensor events and send the data to CPEE. By starting this Flask web server in a separate thread, the service can react asynchronously to the incoming sensor events and process requests in parallel
