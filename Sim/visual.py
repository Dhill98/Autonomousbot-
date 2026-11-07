
# visual.py

import re

import pygame
import config
from environment import room, start, goal
from navigation import move_rover, bfs
from queue import Empty
from rover_state import command_queue


# Configuration
CELL_SIZE = config.CELL_SIZE
FREE_COLOR = config.FREE_COLOR
OBSTACLE_COLOR = config.OBSTACLE_COLOR
ROVER_COLOR = config.ROVER_COLOR
GOAL_COLOR = config.GOAL_COLOR
MOVE_DELAY = config.MOVE_DELAY

MANUAL_MODE = "manual"
AUTO_MODE = "autonomous"

def get_remote_command():
    try:
        direction = command_queue.get_nowait()
        return direction
    except Empty:
        return None
    
def main():
# Initialize Pygame
    pygame.init()

    print("Visualizer loaded environment:", len(room), "rows")

    screen = pygame.display.set_mode(
        (len(room[0]) * CELL_SIZE, len(room) * CELL_SIZE)
    )
    pygame.display.set_caption("Rover Navigation Simulator")

    # Initial rover state
    rover_position = start
    rover_mode = None
    rover_running = False
    running = True

    # Autonomous navigation state
    path = []
    path_index = 0
    last_move_time = pygame.time.get_ticks()

    print("Select Manual (M) or Autonomous (A) mode.")
    print("Press S to start, X to stop.")


    while running:
        remote_direction = get_remote_command()

        if (remote_direction is not None and rover_running and rover_mode == MANUAL_MODE):
            rover_position = move_rover(room, rover_position, remote_direction)
            print(f"Remote command received: {remote_direction}")

        # Handle user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                direction = None

                # Select manual mode
                if event.key == pygame.K_m:
                    rover_mode = MANUAL_MODE
                    rover_running = False
                    print("Manual mode selected. Press S to start.")

                # Select autonomous mode
                elif event.key == pygame.K_a:
                    rover_mode = AUTO_MODE
                    rover_running = False
                    print("Autonomous mode selected. Press S to start.")

                # Start rover
                elif event.key == pygame.K_s:

                    if rover_mode is None:
                        print("Select Manual (M) or Autonomous (A) first.")

                    elif rover_running:
                        print("Rover is already running.")

                    elif rover_mode == MANUAL_MODE:
                        rover_running = True
                        print("Manual rover started.")

                    elif rover_mode == AUTO_MODE:
                        # Calculate a new path from current position
                        new_path = bfs(room, rover_position, goal)

                        if new_path:
                            path = new_path
                            path_index = 0

                            # Skip current position if included in path
                            if path[0] == rover_position:
                                path_index = 1

                            last_move_time = pygame.time.get_ticks()
                            rover_running = True
                            print("Autonomous rover started.")
                            print("Calculated path:", path)

                        else:
                            print("No path to destination found.")

                # Stop rover without closing window
                elif event.key == pygame.K_x:
                    rover_running = False
                    print("Rover stopped.")

                # Manual arrow-key controls
                elif rover_running and rover_mode == MANUAL_MODE:

                    if event.key == pygame.K_RIGHT:
                        direction = "right"

                    elif event.key == pygame.K_LEFT:
                        direction = "left"

                    elif event.key == pygame.K_UP:
                        direction = "up"

                    elif event.key == pygame.K_DOWN:
                        direction = "down"

                # Execute manual movement
                if direction is not None:
                    old_position = rover_position

                    rover_position = move_rover(
                        room,
                        rover_position,
                        direction
                    )

                    if rover_position == old_position:
                        print(
                            f"Rover did not move {direction}. "
                            "Check for an obstacle or boundary."
                        )
                    else:
                        print(f"{direction.capitalize()} pressed.")
                        print("Current position:", rover_position)

        # Autonomous movement
        current_time = pygame.time.get_ticks()

        if (
            rover_running
            and rover_mode == AUTO_MODE
            and current_time - last_move_time >= MOVE_DELAY
        ):

            if path_index < len(path):
                rover_position = path[path_index]
                path_index += 1

                print("Autonomous position:", rover_position)

                if rover_position == goal:
                    rover_running = False
                    print("Destination reached!")

            else:
                rover_running = False
                print("Autonomous navigation completed.")

            last_move_time = current_time

        # Draw simulation background
        screen.fill((30, 30, 30))

        # Draw environment grid
        for row in range(len(room)):
            for col in range(len(room[0])):

                x = col * CELL_SIZE
                y = row * CELL_SIZE

                color = (
                    FREE_COLOR
                    if room[row][col] == 0
                    else OBSTACLE_COLOR
                )

                pygame.draw.rect(
                    screen,
                    color,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

                pygame.draw.rect(
                    screen,
                    (40, 40, 40),
                    (x, y, CELL_SIZE, CELL_SIZE),
                    2
                )

        # Draw rover
        center_x = rover_position[1] * CELL_SIZE + CELL_SIZE // 2
        center_y = rover_position[0] * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.circle(
            screen,
            ROVER_COLOR,
            (center_x, center_y),
            30
        )

        # Draw destination
        goal_x = goal[1] * CELL_SIZE + CELL_SIZE // 2
        goal_y = goal[0] * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.circle(
            screen,
            GOAL_COLOR,
            (goal_x, goal_y),
            30
        )

        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()