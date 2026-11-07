from flask import Flask, jsonify,request
from rover_state import command_queue

app = Flask(__name__)

@app.route("/")
def home():
    return "Rover API is running!"

@app.route("/move", methods=["POST"])
def move():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    direction = data.get("direction")
    valid_moves = {"up", "down", "left", "right"}

    if direction not in valid_moves:
        return jsonify({"error": "Invalid move direction"}), 400

    command_queue.put(direction)

    return jsonify({f"status": "Move command received: {direction}"}), 200

@app.route("/status")
def status():
    return jsonify({"rover controller status": "Controller is online",
                    "mode": "None",
                    "rover_status": "False",
                    "position": [0, 0,]
                    })

@app.route("/mode", methods=["POST"])
def set_mode():
    data =request.get_json(silent=True)
    if isinstance(data, dict):
        mode=data.get("mode")
    if mode =="manual":
        return jsonify({"status": "Mode set to manual"}), 200
    elif mode =="autonomous":
          return jsonify({"status": "Mode set to autonomous"}), 200
    else:
        return jsonify({"error": "Invalid mode"}), 400
    