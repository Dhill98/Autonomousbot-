FQBN ?= esp32:esp32:esp32cam
PYTHON ?= python3
BUILD_DIR ?= build

# Arduino IDE bundles the CLI on macOS even when it is absent from PATH.
ARDUINO_IDE_CLI := /Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli
ARDUINO_CLI ?= $(shell command -v arduino-cli || { test -x "$(ARDUINO_IDE_CLI)" && printf '%s\n' "$(ARDUINO_IDE_CLI)"; } || printf '%s\n' arduino-cli)

.PHONY: all check firmware test python
.DEFAULT_GOAL := all

TEST_SOURCES := tests/test_obstacle_detection.cpp Rover/ObstacleDetection.cpp

all:
	@printf '%s\n' '[all] Starting build and checks'
	@$(MAKE) --no-print-directory check
	@printf '%s\n' '[all] Build and checks passed'

check: firmware test python

firmware:
	@printf '[firmware] Compiling for %s. Sketch sources and headers:\n' "$(FQBN)"
	@find Rover -type f \( -name '*.ino' -o -name '*.c' -o -name '*.cpp' -o -name '*.cxx' -o -name '*.S' -o -name '*.h' -o -name '*.hpp' \) -print
	@"$(ARDUINO_CLI)" compile --fqbn "$(FQBN)" --build-path "$(abspath $(BUILD_DIR))/firmware/$(subst :,-,$(FQBN))" Rover/
	@printf '%s\n' '[firmware] Passed'

test:
	@printf '[test] Compiling %s\n' $(TEST_SOURCES)
	@mkdir -p "$(BUILD_DIR)"
	@$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(TEST_SOURCES) -o "$(BUILD_DIR)/test_obstacle_detection"
	@printf '[test] Running %s\n' "$(BUILD_DIR)/test_obstacle_detection"
	@"$(BUILD_DIR)/test_obstacle_detection"
	@printf '%s\n' '[test] Passed'

python:
	@printf '%s\n' '[python] Compiling Python files under Sim/'
	@PYTHONPYCACHEPREFIX="$(abspath $(BUILD_DIR))/python-cache" "$(PYTHON)" -m compileall -f Sim
	@printf '%s\n' '[python] Passed'
