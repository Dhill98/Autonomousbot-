# RoverNavagation System project
#V1.0 grid based

from environment import room, start, goal
from navigation import move_rover,bfs

print("Rover starting is :", start)
print("Rover goal is :", goal)

position = start

position = move_rover(room, position, "right")
print("After moving right:", position)

position = move_rover(room, position, "down")
print("After moving down:", position)

position = move_rover(room, position, "left")
print("After moving left:", position)

position = move_rover(room, position, "up")
print("After moving up:", position)

path_to_follow = bfs(room, start, goal)
print("calculated path:", path_to_follow)
