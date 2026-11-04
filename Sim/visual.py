#visual
import pygame
from environment import room, start, goal
from navigation import move_rover ,bfs

CELL_SIZE = 150

FREE_COLOR = (220, 220, 220)
OBSTACLE_COLOR = (100, 100, 100)
ROVER_COLOR = (0, 180, 0)
GOAL_COLOR = (0, 100, 255)


print("Visualizer loaded environment:", len(room), "rows")
pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Rover Navigation Simulator")

rover_position = start
bfs(room, start, goal)
path= bfs(room, start, goal)
print("rover:",path )
path_index = 0 
if path_index == 0:
  rover_position = path[path_index] # updates the rovers position using list indexing ..path has the sequence of positions to follow we are accessing the index in the path list
  path_index += 1 #increment to next index , dont use a for loop becuase pygame will go thru it to fast and only give us the end destination 
running = True

move_delay =500
last_move_time = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            direction = None

            if event.key == pygame.K_RIGHT:
                direction = "right"

            elif event.key == pygame.K_LEFT:
                direction = "left"

            elif event.key == pygame.K_UP:
                direction = "up"

            elif event.key == pygame.K_DOWN:
                 direction = "down"

            if direction is not None:
                old_position = rover_position
                rover_position = move_rover(room, rover_position, direction)

                if rover_position == old_position:
                    print(f"Rover did not move {direction} .. check for obsticle or maybe be out of bounds")

                print(f"{direction.capitalize()} pressed")
                print("current position", rover_position)

    current_time = pygame.time.get_ticks()
    if current_time - last_move_time >= move_delay:
        if path_index < len(path):
            rover_position = path[path_index]
            path_index += 1
        last_move_time = current_time
        
            # if event.key == pygame.K_RIGHT:
            #     old_position = rover_position
            #     rover_position = move_rover(room,rover_position, "right")

            #     if rover_position == old_position:
            #         print("Rover did not move right .. check for obsticle or maybe be out of bounds")
            #     print("Right pressed")
            #     print("current position", rover_position)

            # elif event.key == pygame.K_LEFT:
            #     old_position = rover_position
            #     rover_position = move_rover(room,rover_position, "left")
            #     if rover_position == old_position:
            #         print("Rover did not move left .. check for obsticle or maybe be out of bounds")
            #     print("Left pressed")
            #     print("current position", rover_position)

            # elif event.key == pygame.K_UP:
            #     old_position = rover_position
            #     rover_position = move_rover(room,rover_position, "up")
            #     if rover_position == old_position:
            #         print("Rover did not move up .. check for obsticle or maybe be out of bounds")
            #     print("Up pressed")
            #     print("current position", rover_position)

            # elif event.key == pygame.K_DOWN:
            #     old_position = rover_position
            #     rover_position = move_rover(room,rover_position, "down")
            #     if rover_position == old_position:
            #         print("Rover did not move down .. check for obsticle or maybe be out of bounds")
            #     print("Down pressed")
            #     print("current position", rover_position)   

    screen.fill((30, 30, 30))

    for row in range(len(room)):
        for col in range(len(room[0])):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            color = FREE_COLOR if room[row][col] == 0 else OBSTACLE_COLOR

            pygame.draw.rect(
                screen,
                color,
                (x, y, CELL_SIZE, CELL_SIZE)
            )
            pygame.draw.rect(
                screen,
                (40,40,40),
                (x, y, CELL_SIZE, CELL_SIZE),
                2
            )

    center_x = rover_position[1] * CELL_SIZE + CELL_SIZE // 2
    center_y = rover_position[0] * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(
        screen,
        ROVER_COLOR,
        (center_x, center_y),
        30
    )

    goal_x = goal[1] * CELL_SIZE + CELL_SIZE // 2
    goal_y = goal[0] * CELL_SIZE + CELL_SIZE // 2
    
    pygame.draw.circle(
        screen,
        GOAL_COLOR,
        (goal_x, goal_y),
        30
        )
    

    pygame.display.flip()

pygame.quit()