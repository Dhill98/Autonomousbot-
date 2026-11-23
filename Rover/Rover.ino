#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "";
const char* password = "";

WebServer server(80);

const int trigPin = 12;
const int echoPin = 13;

// L298N motor pins — provisional ESP32-CAM assignments
const int motorIN1 = 14;
const int motorIN2 = 15;
const int motorIN3 = 2;
const int motorIN4 = 4;

const int requiredClearReadings = 3;
int clearReadings = 0;

String requestedCommand;
const unsigned long movementDuration = 300;
unsigned long movementStarted = 0;
bool movementActive = false;
bool driveEnabled = false;

const unsigned long sensorInterval = 100;
unsigned long lastSensorRead = 0;

void stopMotors() {
  digitalWrite(motorIN1, LOW);
  digitalWrite(motorIN2, LOW);
  digitalWrite(motorIN3, LOW);
  digitalWrite(motorIN4, LOW);
}

void cancelMovement() {
  stopMotors();
  requestedCommand = "";
  movementActive = false;
}

void moveForward() {
  digitalWrite(motorIN1, HIGH);
  digitalWrite(motorIN2, LOW);
  digitalWrite(motorIN3, HIGH);
  digitalWrite(motorIN4, LOW);
}

void moveBackward() {
  digitalWrite(motorIN1, LOW);
  digitalWrite(motorIN2, HIGH);
  digitalWrite(motorIN3, LOW);
  digitalWrite(motorIN4, HIGH);
}

void turnLeft() {
  digitalWrite(motorIN1, LOW);
  digitalWrite(motorIN2, HIGH);
  digitalWrite(motorIN3, HIGH);
  digitalWrite(motorIN4, LOW);
}

void turnRight() {
  digitalWrite(motorIN1, HIGH);
  digitalWrite(motorIN2, LOW);
  digitalWrite(motorIN3, LOW);
  digitalWrite(motorIN4, HIGH);
}

bool shouldStop(float distance) {
  return distance <= 20.0f;
}

void triggerSensor() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
}

unsigned long readEchoTime() {
  return pulseIn(echoPin, HIGH, 30000);
}

float calculateDistance(unsigned long duration) {
  return (duration * 0.0343f) / 2;
}

void handleMovement(const String& command) {
  if (command != "FORWARD" && command != "BACKWARD" &&
      command != "LEFT" && command != "RIGHT") {
    server.send(400, "text/plain", "Unknown movement command.");
    return;
  }

  cancelMovement();
  requestedCommand = command;
  server.send(200, "text/plain", "Command accepted: " + command);
}

void handleStartandStopCommand() {
  String command = server.arg("cmd");
  command.trim();
  command.toUpperCase();

  Serial.print("Incoming cmd: [");
  Serial.print(command);
  Serial.println("]");

  if (command == "STOP") {
    driveEnabled = false;
    cancelMovement();
    server.send(200, "text/plain", "Command accepted: STOP");
    return;
  }

  if (command == "START") {
    driveEnabled = true;
    server.send(200, "text/plain", "Command accepted: START");
    return;
  }

  if (!driveEnabled) {
    server.send(409, "text/plain", "Press Play first.");
    return;
  }

  handleMovement(command);
}

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");
  unsigned long startTime = millis();

  while (WiFi.status() != WL_CONNECTED &&
         millis() - startTime < 20000) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected. ESP32 IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi connection failed. Check the network name and password.");
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  digitalWrite(trigPin, LOW);

  pinMode(motorIN1, OUTPUT);
  pinMode(motorIN2, OUTPUT);
  pinMode(motorIN3, OUTPUT);
  pinMode(motorIN4, OUTPUT);
  stopMotors();

  connectToWiFi();

  server.on("/move", HTTP_GET, handleStartandStopCommand);
  server.begin();

  Serial.println("Rover command server started.");
}

void loop() {
  server.handleClient();

  if (movementActive && millis() - movementStarted >= movementDuration) {
    cancelMovement();
    Serial.println("STOP: Movement timer expired");
  }

  if (requestedCommand.length() != 0 && WiFi.status() != WL_CONNECTED) {
    cancelMovement();
    Serial.println("STOP: Wi-Fi disconnected");
  }

  if (millis() - lastSensorRead < sensorInterval) {
    return;
  }
  lastSensorRead = millis();

  triggerSensor();
  unsigned long duration = readEchoTime();

  if (duration == 0) {
    clearReadings = 0;
    cancelMovement();
    return;
  }

  float objdistance = calculateDistance(duration);

  Serial.print("Distance: ");
  Serial.print(objdistance);
  Serial.println(" cm");

  if (shouldStop(objdistance)) {
    clearReadings = 0;
    cancelMovement();
    Serial.println("STOP: Obstacle detected");
    return;
  }

  if (clearReadings < requiredClearReadings) {
    clearReadings++;
  }

  if (clearReadings < requiredClearReadings ||
      movementActive || requestedCommand.length() == 0) {
    return;
  }

  if (requestedCommand == "FORWARD") {
    moveForward();
  } else if (requestedCommand == "BACKWARD") {
    moveBackward();
  } else if (requestedCommand == "LEFT") {
    turnLeft();
  } else if (requestedCommand == "RIGHT") {
    turnRight();
  }

  movementStarted = millis();
  movementActive = true;
}
