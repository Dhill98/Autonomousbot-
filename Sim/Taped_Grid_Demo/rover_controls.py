# Build step 3. Sends commands and reads status from Rover.ino over HTTP.
# No project imports needed. For HTTP, see urlopen in api.py.
# RouteExecutor and ObstacleRecovery import RoverControls.

from __future__ import annotations


class RoverControls:
    base_url: str
    timeout_seconds: float

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def send_command(self, command: str) -> str:
        pass

    def read_status(self) -> dict[str, str]:
        pass
