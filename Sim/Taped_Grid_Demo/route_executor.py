# Build step 4. Uses Simulator for the grid and position, PathPlanner for
# routes, and RoverControls to send each physical move.
# ObstacleRecovery imports RouteExecutor to request replanning.

from __future__ import annotations

from .path_planner import PathPlanner
from .rover_controls import RoverControls
from .simulator import Cell, Simulator


class RouteExecutor:
    simulator: Simulator
    planner: PathPlanner
    controls: RoverControls
    confirmed_cell: Cell
    heading: str
    route: list[Cell]
    next_step_index: int

    def commands_for_step(self, next_cell: Cell) -> list[str]:
        pass

    def execute_next_step(self) -> None:
        pass

    def confirm_step(self, cell: Cell, heading: str) -> None:
        pass

    def replan(self) -> None:
        pass
