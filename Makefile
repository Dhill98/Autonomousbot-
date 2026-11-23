FQBN ?= esp32:esp32:esp32cam
PYTHON ?= python3
BUILD_DIR ?= build

# Arduino IDE bundles the CLI on macOS even when it is absent from PATH.
ARDUINO_IDE_CLI := /Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli
ARDUINO_CLI ?= $(shell command -v arduino-cli || { test -x "$(ARDUINO_IDE_CLI)" && printf '%s\n' "$(ARDUINO_IDE_CLI)"; } || printf '%s\n' arduino-cli)

.PHONY: check firmware test python

check: firmware test python

firmware:
	"$(ARDUINO_CLI)" compile --fqbn "$(FQBN)" --build-path "$(abspath $(BUILD_DIR))/firmware/$(subst :,-,$(FQBN))" Rover/

test:
	mkdir -p "$(BUILD_DIR)"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) tests/test_obstacle_detection.cpp Rover/ObstacleDetection.cpp -o "$(BUILD_DIR)/test_obstacle_detection"
	"$(BUILD_DIR)/test_obstacle_detection"

python:
	PYTHONPYCACHEPREFIX="$(abspath $(BUILD_DIR))/python-cache" "$(PYTHON)" -m compileall -q Sim
