# Build step 1. Stores the grid and the displayed rover position.
# No project imports needed. PathPlanner uses its Cell and Grid types,
# and RouteExecutor and ObstacleRecovery use the Simulator class.

from __future__ import annotations


Cell = tuple[int, int]
Grid = list[list[int]]


class Simulator:
    grid: Grid
    start: Cell
    goal: Cell
    rover_position: Cell

    def set_obstacle(self, cell: Cell, blocked: bool) -> None:
        pass

    def update_rover_position(self, cell: Cell) -> None:
        pass
