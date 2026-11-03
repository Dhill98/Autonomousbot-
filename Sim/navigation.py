#navigation
def move_rover(room, position, direction):
    if direction not in directions:
        print(f"Invalid direction: {direction}")
        return position
    
    row, col = position
    movement = directions[direction]

    new_row = row + movement[0]
    new_col = col + movement[1]

    if is_safe(room, new_row, new_col):
        return (new_row, new_col)
    return position


def is_safe(room,row,col):
    rows = len(room)
    cols = len(room[0])

    if(0<= row < rows and 0<= col < cols): # Check if the row and column exist 
        return room[row][col] == 0 
    return False


directions = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}
