# RoverNavagation System project
#V1.0 grid based

room = [
    [0,0,0,0],
    [0,1,1,0],
    [0,0,0,0],
    [0,0,0,0],
]


start =(0,0)
goal = (3,3)

print("Rover starting is :", start)
print("Rover goal is :", goal)

def is_safe(room,row,col):
    rows = len(room)
    cols = len(room[0])
    