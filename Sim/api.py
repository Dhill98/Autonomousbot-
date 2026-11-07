from flask import Flask, jsonify,request, render_template
from rover_state import command_queue
import logging
from pathlib import Path

log_directory = Path(__file__).parent / "logs"
log_directory.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_directory / "api.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)

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
    command_queue.put({"type": "start"})
    return jsonify({"status": "Rover started"}), 200
    
@app.route("/stop", methods=["POST"])
def stop_rover():
    command_queue.put({"type": "stop"})
    return jsonify({"status": "Rover stopped"}), 200
