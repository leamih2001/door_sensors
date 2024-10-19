#include <ArduinoWebsockets.h>
#include <WiFi.h>

// Networkdata
const char* ssid = "Cocktail_Mixer";
const char* password = "process_hubby"; 

// Pins for the lightsensors
// Input for the first light barrier (ENTRY, bottom)
const int SENSOR_1_PIN = 16; 
// Input for the second light barrier (EXIT, bottom)
const int SENSOR_2_PIN = 17; 
// Input for the third light barrier (ENTRY, top)
const int SENSOR_3_PIN = 18; 
// Input for the forth light barrier (EXIT, top)
const int SENSOR_4_PIN = 19; 

// Status variables for the logic implementation of the infrared light barriers
bool entryDetectedBottom = false;
bool exitDetectedBottom = false;
bool entryDetectedTop = false;
bool exitDetectedTop = false;

// Time stamp for deactivation
// Variable for the lower sensors
unsigned long disableTimeBottom = 0;
// Variable for the upper sensors
unsigned long disableTimeTop = 0;  
// 2 second “pause” after breaking through the beam of a light barrier
const unsigned long disableDuration = 2000;

using namespace websockets;

WebsocketsServer server;
WebsocketsClient connectedClient; 

void setup() {
    Serial.begin(115200);
    Serial.println("Connect to WiFi...");

    // Connect to WiFi
    WiFi.begin(ssid, password);
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 15) {
        Serial.print(".");
        delay(1000);
        retries++;
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("\nMistake: No WiFi connection");
        while (true) {
            // The system waits 5 seconds and then repeats the error message
            delay(5000);  
        }
    } else {
        Serial.println("\nWiFi connected");
        Serial.println("IP-Adress: ");
        Serial.println(WiFi.localIP());

        // Starting WebSocket-Server
        server.listen(80);

        // Defining the Pin-Modes
        pinMode(SENSOR_1_PIN, INPUT);
        pinMode(SENSOR_2_PIN, INPUT);
        pinMode(SENSOR_3_PIN, INPUT);
        pinMode(SENSOR_4_PIN, INPUT);
    }
}

void loop() {
    // Accepting the WebSocket connections
    while (!connectedClient.available()) {
        Serial.println("Waiting for Client connections");
        connectedClient = server.accept();

        if (connectedClient.available()) {
            Serial.println("Client connected");
        }
    }

    // Sensor logic only executed when the client is connected
    if (connectedClient.available()) {
        checkSensors();
    } else {
        Serial.println("No Client connected. Sensors deactivated.");
    }
}

void checkSensors() {
    unsigned long currentTime = millis();

    // Querying the individual statuses of the light barriers
    int Sensor1State = digitalRead(SENSOR_1_PIN);
    int Sensor2State = digitalRead(SENSOR_2_PIN);
    int Sensor3State = digitalRead(SENSOR_3_PIN);
    int Sensor4State = digitalRead(SENSOR_4_PIN);

    // Logic for lower sensors (only active if the upper sensors are not deactivated)
    if (currentTime - disableTimeBottom >= disableDuration) {
        if (Sensor1State == LOW && !entryDetectedBottom) { 
            entryDetectedBottom = true;
            Serial.println("Person enters the room (bottom).");
            logAccess("ENTRY (bottom)");
            sendMessageToClient("ENTRY");
            // Upper light barriers deactivated for 2 seconds
            disableTimeTop = currentTime;
            // Lower light barriers deactivated for 2 seconds
            disableTimeBottom = currentTime;
        } 
        else if (Sensor2State == LOW && !exitDetectedBottom) {
            exitDetectedBottom = true;
            Serial.println("Person leaves the room (bottom).");
            logAccess("EXIT (borrom)");
            sendMessageToClient("EXIT");
            // Upper light barriers deactivated for 2 seconds
            disableTimeTop = currentTime; 
            // Lower light barriers deactivated for 2 seconds
            disableTimeBottom = currentTime;
        }
    }

    // Logic for upper sensors (only active if the lower sensors are not deactivated)
    if (currentTime - disableTimeTop >= disableDuration) {
        if (Sensor3State == LOW && !entryDetectedTop) {
            entryDetectedTop = true;
            Serial.println("Person enters the room (top).");
            logAccess("ENTRY (top)");
            sendMessageToClient("ENTRY");
            // Lower light barriers deactivated for 2 seconds
            disableTimeBottom = currentTime; 
            // Upper light barriers deactivated for 2 seconds
            disableTimeTop = currentTime;  
        } 
        else if (Sensor4State == LOW && !exitDetectedTop) {
            exitDetectedTop = true;
            Serial.println("Person leaves the room (top).");
            logAccess("EXIT (top)");
            sendMessageToClient("EXIT");
            // Lower light barriers deactivated for 2 seconds
            disableTimeBottom = currentTime;
            // Upper light barriers deactivated for 2 seconds
            disableTimeTop = currentTime;
        }
    }

    // Reset the status variables when the light barriers are no longer blocked
    if (Sensor1State == HIGH) entryDetectedBottom = false;
    if (Sensor2State == HIGH) exitDetectedBottom = false;
    if (Sensor3State == HIGH) entryDetectedTop = false;
    if (Sensor4State == HIGH) exitDetectedTop = false;
}

// Sends message (if connection is established) to connected WebSocket client
void sendMessageToClient(String message) {
    if (connectedClient.available()) {
        bool success = connectedClient.send(message);
        if (!success) {
            Serial.println("Connection lost. Message could not be sent.");
            // Close due to loss of connection
            connectedClient.close();
        } else {
            Serial.println("Message sent: " + message);
        }
    } else {
        Serial.println("No client connected. Message not sent: " + message);
    }
}

// Logs the transferred access process on the console
void logAccess(String action) {
    Serial.println("Logging access: " + action);
}

