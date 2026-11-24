#include <WiFi.h>
#include <WebServer.h>
#include <esp_system.h>
#include <esp_camera.h>

const char* ssid = "";
const char* password = "";

WebServer server(80);

const int trigPin = 12;
const int echoPin = 13;
const int bootLedPin = 33;  // AI Thinker ESP32-CAM red LED, active LOW.

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
const unsigned long diagnosticInterval = 2000;
unsigned long lastDiagnostic = 0;
const char* sensorState = "waiting";
float lastDistance = 0;
bool wifiWasConnected = false;
bool networkInitialized = false;
#define CAMERA_MODEL_AI_THINKER
//CAMERA CONFIG
#if defined(CAMERA_MODEL_AI_THINKER)
#define PWDN_GPIO_NUM    32
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27

#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      21
#define Y4_GPIO_NUM      19
#define Y3_GPIO_NUM      18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    5
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

#else
#error "Camera model not selected"
#endif

void handleStatus() { //straight chat function lol 
  char body[256];
  snprintf(body, sizeof(body),
           "uptime_ms=%lu\nreset_reason=%d\nbrownout=%s\nwifi_rssi_dbm=%ld\n"
           "drive_enabled=%s\nmotors_commanded=%s\nsensor=%s\ndistance_cm=%.1f\nclear_readings=%d/%d\n",
           millis(), static_cast<int>(esp_reset_reason()),
           esp_reset_reason() == ESP_RST_BROWNOUT ? "yes" : "no",
           static_cast<long>(WiFi.RSSI()), driveEnabled ? "yes" : "no",
           movementActive ? "yes" : "no", sensorState, lastDistance,
           clearReadings, requiredClearReadings);
  server.send(200, "text/plain", body);
}

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
  if(distance ==0){
    return false;
  }
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
  Serial.printf("[drive] Queued %s, clear readings %d/%d\n",
                command.c_str(), clearReadings, requiredClearReadings);
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
    Serial.println("[drive] Disabled; motor outputs stopped");
    server.send(200, "text/plain", "Command accepted: STOP");
    return;
  }

  if (command == "START") {
    driveEnabled = true;
    Serial.println("[drive] Enabled");
    server.send(200, "text/plain", "Command accepted: START");
    return;
  }

  if (!driveEnabled) {
    Serial.println("[drive] Rejected; send START first");
    server.send(409, "text/plain", "Press Play first.");
    return;
  }

  handleMovement(command);
}

void connectToWiFi() {
  if (ssid[0] == '\0') {
    Serial.println("[wifi] SSID is blank; set it locally before flashing");
    return;
  }
  if (!WiFi.mode(WIFI_STA)) {
    Serial.println("[wifi] Could not initialize station mode");
    return;
  }
  networkInitialized = true;
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");
  unsigned long startTime = millis();

  while (WiFi.status() != WL_CONNECTED &&
         millis() - startTime < 20000) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();

  wifiWasConnected = WiFi.status() == WL_CONNECTED;
  if (wifiWasConnected) {
    Serial.print("Connected. ESP32 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.printf("[wifi] RSSI %ld dBm\n", static_cast<long>(WiFi.RSSI()));
  } else {
    Serial.printf("[wifi] Connection timed out; status=%d\n", WiFi.status());
  }
}

void initializedCamera(){
//setting pins and config
  camera_config_t config = {};
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset =RESET_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_pclk =PCLK_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
//speed ,size ,format and quality
    config.xclk_freq_hz = 20000000;
    config.ledc_timer = LEDC_TIMER_0;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.pixel_format =PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  esp_err_t result =esp_camera_init(&config); // take all your cam configs and pass to the built in func

  if(result != ESP_OK){
    Serial.println(" Camera is initialized fail");
    Serial.println(esp_err_to_name(result));
    return;
  }
  Serial.println(" Camera is initialized Success");
  camera_fb_t* frame = esp_camera_fb_get();
  if (frame != nullptr) {
    Serial.println(" the frame size is :");
    Serial.println(frame->len);//reads in byte count
   esp_camera_fb_return(frame);
} else{
  Serial.println("Camera capture failed");
}
}

void setup() {

  pinMode(bootLedPin, OUTPUT);
  digitalWrite(bootLedPin, LOW);


  Serial.begin(115200);
  esp_reset_reason_t resetReason = esp_reset_reason();
  Serial.printf("[boot] Reset reason %d%s\n", static_cast<int>(resetReason),
                resetReason == ESP_RST_BROWNOUT ? " (brownout)" : "");

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  digitalWrite(trigPin, LOW);

  pinMode(motorIN1, OUTPUT);
  pinMode(motorIN2, OUTPUT);
  pinMode(motorIN3, OUTPUT);
  pinMode(motorIN4, OUTPUT);
  stopMotors();

  connectToWiFi();
  if(networkInitialized){
    initializedCamera();
  }

  if (networkInitialized) {
    server.on("/move", HTTP_GET, handleStartandStopCommand);
    server.on("/status", HTTP_GET, handleStatus);
    server.begin();
    Serial.println("Rover command server started.");
  }
}

void loop() {
  if (networkInitialized) {
    server.handleClient();
  }

  bool wifiConnected = networkInitialized && WiFi.status() == WL_CONNECTED;
  if (wifiConnected != wifiWasConnected) {
    wifiWasConnected = wifiConnected;
    if (wifiConnected) {
      Serial.print("[wifi] Connected. IP: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("[wifi] Disconnected");
    }
  }

  if (movementActive && millis() - movementStarted >= movementDuration) {
    cancelMovement();
    Serial.println("STOP: Movement timer expired");
  }

  if (requestedCommand.length() != 0 && !wifiConnected) {
    cancelMovement();
    Serial.println("STOP: Wi-Fi disconnected");
  }

  if (millis() - lastSensorRead < sensorInterval) {
    return;
  }
  lastSensorRead = millis();

  triggerSensor();
  unsigned long duration = readEchoTime();
  bool logReading = millis() - lastDiagnostic >= diagnosticInterval;
  if (logReading) {
    lastDiagnostic = millis();
  }

  if (duration == 0) {
    sensorState = "clear";
    lastDistance = 0;
    bool interruptedMove = requestedCommand.length() != 0;
    if (logReading) {
      Serial.println("[sensor] No echo within 30 ms; clear");
    }
  } else{

  float objdistance = calculateDistance(duration);
  lastDistance = objdistance;

  if (shouldStop(objdistance)) {
    sensorState = "obstacle";
    clearReadings = 0;
    bool interruptedMove = requestedCommand.length() != 0;
    cancelMovement();
    if (logReading || interruptedMove) {
      Serial.printf("[sensor] Obstacle at %.1f cm; motors stopped\n", objdistance);
    }
    return;
  }
  }

  if (clearReadings < requiredClearReadings) {
    clearReadings++;
  }
  sensorState = clearReadings < requiredClearReadings ? "checking" : "clear";
  if (logReading) {
    Serial.printf("[sensor] %.1f cm; clear readings %d/%d\n",
                   clearReadings, requiredClearReadings);
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
  Serial.printf("[drive] Motor outputs set for %s for up to %lu ms\n",
                requestedCommand.c_str(), movementDuration);
}
