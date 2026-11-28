# Autonomousbot

An ESP32-CAM rover with a browser controller, an ultrasonic obstacle sensor, and a Python distance-classification demo.

## Project status

| Feature | Status |
| --- | --- |
| Manual driving | Tested on the physical rover. The browser controller sends commands through Flask. |
| Autonomous circle | Implemented for ClassDemo. The rover slows its right motor to circle, stops when it detects an obstacle within 20 cm, and resumes after three clear readings. Pause ends the run. Circle radius and stop/resume still need a hardware test. |
| Camera uploads | Implemented. The ESP32 can upload a JPEG every three seconds, and Flask serves the latest received image at `/camera`. Set the upload URL before flashing and verify the full path on the rover. |
| Machine learning | The decision tree classifies distances as `STOP`, `CAUTION`, or `PASS`. It passed 9 of 9 held-out synthetic examples. Live polling was checked with mocked rover responses and still needs a hardware test. The model reports predictions in the terminal while firmware handles motor control. |

## Run the class demo

Flash `Rover/Rover.ino` to the ESP32-CAM, then run this from the repository root:

```bash
python3 Sim/ClassDemo/runDemo.py --lan
```

Open [the rover controller](http://127.0.0.1:5001/) and choose Manual or Autonomous before pressing Play. ClassDemo runs independently of Pygame. To run the simulator, use `python3 Sim/run.py` in place of ClassDemo.

For camera uploads, set `cameraUploadUrl` in the sketch to `http://<computer-wifi-ip>:5001/camera` before flashing. Open [the latest photo](http://127.0.0.1:5001/camera) after the first upload arrives.

## Run the distance classifier

```bash
python3 Sim/ml_navigation.py
python3 Sim/ml_navigation.py --live http://<rover-ip>
python3 Sim/run.py 

```

The first command evaluates the model offline. For the second, replace `<rover-ip>` with the ESP32 address printed in Serial Monitor. Live mode reads `/status` and prints the measured distance, prediction, and rover sensor state.

## Next milestone

Verify the complete demo on the physical rover. Obstacle-triggered photo collection and image-based object identification are future work.
