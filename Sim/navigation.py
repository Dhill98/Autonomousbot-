#navigation
from collections import deque

directions = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

def is_safe(room,row,col):
    rows = len(room)
    cols = len(room[0])

    if(0<= row < rows and 0<= col < cols): # Check if the row and column exist 
        return room[row][col] == 0 
    return False

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


def bfs(room,start,goal):
    queue =deque([start]) # need to be a tuple so we have one complete location
    visited = {start} # creates a set and has start in it ..will give both cordinates this way 
    parent = {} # empty hash/dictionary
    
    while queue:
        current_position = queue.popleft() # this will update the queue with the next position to explore
        if current_position == goal:
            path = [] # use a empty list becuase we wont know the size of the path beforehand and we need it ordered to know it got to its destination
            path.append(current_position)
            while current_position != start:
                current_position = parent.get(current_position)
                path.append(current_position)# path comes in backword so we rever it ..its built it 
            path.reverse()
            print("Path found:", path)
            return path
        
        for movement in directions.values():
            row, col = current_position 

            new_row = row + movement[0]
            new_col = col + movement[1]
            new_position = (new_row, new_col)
            if is_safe(room, new_row, new_col) and new_position not in visited: # Check if the new position is safe and not visited sees old spots as new for each update

                queue.append(new_position)
                visited.add(new_position)

                parent[new_position] = current_position # adds the parent location and new location to the hash so it can grow on its own
          
    return False

       