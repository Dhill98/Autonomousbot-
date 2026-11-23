# Build step 5. Uses RoverControls to check status and Simulator to mark
# obstacles, then asks RouteExecutor to replan.

from __future__ import annotations

from typing import Optional

from .rover_controls import RoverControls
from .route_executor import RouteExecutor
from .simulator import Cell, Simulator


class ObstacleRecovery:
    simulator: Simulator
    controls: RoverControls
    executor: RouteExecutor
    blocked_cell: Optional[Cell]

    def detect_blocked_move(self, status: dict[str, str]) -> bool:
        pass

    def check_clearance(self, heading: str) -> Optional[float]:
        pass

    def mark_obstacle(self, cell: Cell) -> None:
        pass

    def request_replan(self) -> None:
        pass
