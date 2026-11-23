# Build step 2. Plans on the simulator's grid.
# Import Cell and Grid from simulator. To reuse the existing algorithm
# when you fill this in, import plan_path from navigation.
# RouteExecutor imports PathPlanner to ask for a route.

from __future__ import annotations

from typing import Optional

from .simulator import Cell, Grid


class PathPlanner:
    def plan_path(
        self, grid: Grid, start: Cell, goal: Cell, planner: str = "bfs"
    ) -> Optional[list[Cell]]:
        pass
