# door_sensors (Documentation for Access Control System)

1. Introduction
   The aim of the implemented system is to monitor entry and exit into a room, in this case the laboratory, using infrared
   light barriers, whereby photos are taken and facial recognition is then carried out. In this case, there are three main
   services that are orchestrated by the process engine. Communication between the services does not take place directly,
   but is coordinated by the CPEE, whereby the CPEE server calls scripts on the PC via http(s), which ensures, among other
   things, loose coupling and reusability.

2. Overview components
   The hardware components are as follows:
   - Infrared light barriers (LEFRIKO E18-D80NK)
   - Development board (ESP32-WROOM-32E)
   - Webcam (Logitech Streamcam)
   The ESP32 monitors the infrared light barriers and sends events to a central WebSocket client. There are three Flask-based
   services, which are:
   - Sensor Data Retrieval
   - Image Capture
   - Face Recognition

3. Hardware setup: Infrared light barrier and ESP32
   The ESP32 monitors four infrared light barriers, each of which detects people entering or leaving the laboratory. Two are
   mounted further up and the other two further down on the door frame to counteract the physical restrictions. The two
   brackets in which the sensors are located were produced using 3D printing, whereby there is a small opening underneath
   next to the two holes for the light barriers in which the ESP can be attached. The Arduino code regulates the behavior of
   the sensors and a small time delay was implemented to avoid overdetection. As soon as a sensor is triggered by a person
   entering or leaving the room, this event is sent to a websocket client via a message (“ENTRY” or “EXIT”).

4. Software architecture
   The process engine generally queries the sensor data service to determine whether an entry or exit has been detected.
   Based on this information, it triggers the services to perform the corresponding actions.
   
   4.1. Sensor data service
        This receives the events from the ESP via a websocket client and provides a REST endpoint /checkSensor to query the
        current sensor data status.
   
   4.2. Image capture service
        Here, the image is captured with the webcam when an entry or exit is detected. In addition, OpenCV is used here to
        achieve better quality for the subsequent face detection. The images are saved in a local directory and the REST
        endpoint /capture is used to trigger the image capture. The camera buffer is also emptied so that images are not
        simply overwritten.
   
   4.3. Face detection service
        For this service, OpenCV and a pre-trained hair cascade model are used to recognize faces. The REST endpoint /face
        detection is used to transmit the image for recognition.

5. Process
   - Access detection: A person enters (or leaves) the laboratory and thus breaks through the light barrier
     -> This event is registered in the ESP32 and sent to the sensor data service via a WebSocket.
   - Image capture: If “ENTRY” or “EXIT” is detected, the image capture service is called to capture an image of the person.
   - Face recognition: The captured image is forwarded to the face recognition service, which checks whether there are faces
     and, if so, where and how many there are on the captured image.
   - Process Engine: Coordinates the interactions between the services by querying events and initiating the next steps
     based on them.

6. Implementation details
   
   6.1. Arduino (ESP32)
        A WLAN connection is established and a new websocket server is started. In addition, the states of the infrared
        light barriers are read out and their logic is implemented. Depending on which light barrier (outer or inner) is
        broken through first, an entry or exit can be distinguished. At the end, the detected events are sent to the web
        socket client.

   6.2. Pyhonservices
        - Sensor data service: Implements communication via websockets with the ESP32. The service contains a websocket
          client that connects to the websocket server on the ESP and is notified via this connection when a light barrier
          is triggered. Threading is also used to process multiple messages in real time and thus reliably update the sensor
          status.
        - Image acquisition service: Uses OpenCV to capture images and store them in the local file system. A few
          optimizations, such as rotation(s) and resolution settings, have been made to ensure clearer images for face
          recognition.
        - Face recognition service: Processes the captured images and performs face recognition. Here, the recognition
          parameters have also been optimized to achieve better accuracy and consistency of face recognition.
