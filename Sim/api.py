from flask import Flask, Response, jsonify, request, render_template
from rover_state import command_queue
import logging
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


log_directory = Path(__file__).parent / "logs"
log_directory.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_directory / "api.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)

ESP32_BASE_URL = "http://192.168.1.88"
MAX_CAMERA_FRAME_BYTES = 512 * 1024
latest_camera_frame = None

ESP32_COMMANDS = {
    "up": "FORWARD",
    "down": "BACKWARD",
    "left": "LEFT",
    "right": "RIGHT",
}
def send_esp32_commands(command):
    query = urlencode({"cmd":command})
    url =f"{ESP32_BASE_URL}/move?{query}"
    app.logger.info("Sending ESP32 command %s", command)
    with urlopen(url, timeout=5) as response:
        reply = response.read().decode("utf-8")
        app.logger.info("ESP32 %s returned HTTP %s: %s", command, response.status, reply)
        return reply

def log_esp32_status():
    url = f"{ESP32_BASE_URL}/status"
    try:
        with urlopen(url, timeout = 5) as response:
            status_txt = response.read().decode("utf-8")
            app.logger.info("ESP32 Status Success%s", status_txt.strip())
    except OSError as error:
        app.logger.warning(" ESP32 Status fail : The status is messed up %s", status_txt.srtrip())
        
@app.route("/")
def home():
    return render_template("controller.html") # show the rover controller HTML page when you use api

@app.route("/camera", methods=["POST"])
def receive_camera_frame():
    global latest_camera_frame

    if request.mimetype != "image/jpeg":
        return jsonify({"error": "Expected image/jpeg"}), 415

    if request.content_length is not None and request.content_length > MAX_CAMERA_FRAME_BYTES:
        return jsonify({"error": "Camera frame is too large"}), 413

    frame = request.stream.read(MAX_CAMERA_FRAME_BYTES + 1)
    if len(frame) > MAX_CAMERA_FRAME_BYTES:
        return jsonify({"error": "Camera frame is too large"}), 413

    if len(frame) < 4 or not frame.startswith(b"\xff\xd8") or not frame.endswith(b"\xff\xd9"):
        return jsonify({"error": "Missing JPEG frame markers"}), 400

    latest_camera_frame = frame
    return "", 204


@app.route("/camera", methods=["GET"])
def get_camera_frame():
    frame = latest_camera_frame
    if frame is None:
        return jsonify({"error": "No camera frame received yet"}), 404

    return Response(frame, mimetype="image/jpeg", headers={"Cache-Control": "no-store"})


@app.route("/move", methods=["POST"])
def move():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    direction = data.get("direction")
    if not isinstance(direction, str) or direction not in ESP32_COMMANDS:
        return jsonify({"error": "Invalid move direction"}), 400

    try:
        esp32_reply = send_esp32_commands(ESP32_COMMANDS[direction])
    except OSError as error:
        app.logger.error("ESP32 move failed: %s", error)
        return jsonify({"error": "ESP32 did not confirm movement"}), 502

    if not app.config.get("CLASS_DEMO"):
        command_queue.put({"type": "move", "direction": direction})
    return jsonify({
        "status": f"Move command received: {direction}",
        "esp32_reply": esp32_reply,
    }), 200

@app.route("/status", methods=["GET"])
def status():

    return jsonify({"rover controller status": "Controller is online",
                    "mode": "None",
                    "rover_status": "False",
                    "position": [0, 0,]
                    })

@app.route("/mode", methods=["POST"])
def set_mode():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400
    mode = data.get("mode")
    if app.config.get("CLASS_DEMO"):
        if mode not in ("manual", "autonomous"):
            return jsonify({"error": "Invalid mode"}), 400
        return stop_rover()
    if mode =="manual":
        command_queue.put({"type": "mode", "mode": mode}) # add the mode of whats selected to the queue 
        return jsonify({"mode": "Mode set to manual"}), 200
    elif mode =="autonomous":
          command_queue.put({"type": "mode", "mode": mode})
          return jsonify({"status": "Mode set to autonomous"}), 200
    else:
        return jsonify({"error": "Invalid mode"}), 400

@app.route("/start", methods=["POST"])
def start_rover():
    class_demo = app.config.get("CLASS_DEMO")
    command = "START"
    if class_demo:
        data = request.get_json(silent=True)
        mode = data.get("mode") if isinstance(data, dict) else None
        if mode not in ("manual", "autonomous"):
            return jsonify({"error": "Select a drive mode"}), 400
        if mode == "autonomous":
            command = "START_CIRCLE"

    try:
        send_esp32_commands(command)
    except OSError as error:
        app.logger.warning("ESP32 start failure: %s", error)
        return jsonify({"error": "ESP32 did not confirm start"}), 502
    
    if not class_demo:
        command_queue.put({"type": "start"})
    else:
        print("Rover started", flush=True)
    return jsonify({"status": "Rover started"}), 200
    
@app.route("/stop", methods=["POST"])
def stop_rover():
    if not app.config.get("CLASS_DEMO"):
        command_queue.put({"type": "stop"})
    try:
        esp32_reply = send_esp32_commands("STOP")
    except OSError as error:
        app.logger.warning("ESP32 stop failure: %s", error)
        return jsonify({"error": "ESP32 did not confirm stop "}), 502

    if app.config.get("CLASS_DEMO"):
        print("Rover stopped", flush=True)
    return jsonify({"status": "Rover stopped"}), 200
