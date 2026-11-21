from flask import Flask, jsonify,request, render_template
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

ESP32_COMMANDS = {
    "up": "FORWARD",
    "down": "BACKWARD",
    "left": "LEFT",
    "right": "RIGHT",
}
def send_esp32_commands(command):
    query = urlencode({"cmd":command})
    url =f"{ESP32_BASE_URL}/move?{query}"

    with urlopen(url,timeout=2) as response:
        return response.read().decode("utf-8")

@app.route("/")
def home():
    return render_template("controller.html") # show the rover controller HTML page when you use api

@app.route("/move", methods=["POST"])# end ppoints
def move():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    direction = data.get("direction")
    valid_moves = {"up", "down", "left", "right"}

    if direction not in valid_moves:
        return jsonify({"error": "Invalid move direction"}), 400
    
    if direction in valid_moves:
        command_queue.put({"type": "move", "direction": direction})
        return jsonify({"status": f"Move command received: {direction}"}), 200

    if direction in ESP32_COMMANDS:
        command = ESP32_COMMANDS[direction] #checked if direction was in our commands then saved it to a new varible command that will take the direction in 
        try:
            esp32_reply = send_esp32_commands(command)
        except OSError as error:
            app.logger.error("COMMAND Failed %s" , error)
            return jsonify({"error": "ESP32 cant get commands"}),502
        return jsonify({" Succes":esp32_reply}),200

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
    mode=data.get("mode")
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
    try:
        esp32_reply = send_esp32_commands("START")
    except OSError as error:
        app.logger.warning("ESP32 start failure:  ", error)
        return jsonify({"error": "ESP32 did not confirm start"}), 502
    
    command_queue.put({"type": "start"})
    return jsonify({"status": "Rover started"}), 200
    
@app.route("/stop", methods=["POST"])
def stop_rover():
    command_queue.put({"type": "stop"})
    try:
        esp32_reply = send_esp32_commands("STOP")
    except OSError as error:
        app.logger.warning("ESP32 stop failure: ", error)
        return jsonify({"error": "ESP32 did not confirm stop "}), 502
    
    return jsonify({"status": "Rover stopped"}), 200
