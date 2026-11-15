#navigation
from collections import deque

directions = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

def initialize_costGrid(room ,goal) : # this creates a cost grid initialized to infinity, with the goal cell set to 0 
    rows = len(room)
    cols = len(room[0])
    infinite = float("inf")
    goal_cell_cost=0
    cost = []
    for row in range(rows):
        cost_row = []
        for col in range(cols):
            cost_row.append(infinite)
        cost.append(cost_row)
    goal_row, goal_col = goal

    cost[goal_row][goal_col] = goal_cell_cost
    return cost

def calculate_cost(room ,goal):
    costs = initialize_costGrid(room, goal)
    changed = True
    while changed:
        changed = False
        for row in range(len(room)):
            for col in range(len(room[0])):
                if not is_safe(room, row, col):
                    continue
                if costs[row][col] == 0:
                    continue
                for movement in directions.values(): # take all the movements in direction and calculate the cost of each neighboring cell
                    neighboring_row = row + movement[0]
                    neighboring_col = col + movement[1]
                    if is_safe(room, neighboring_row, neighboring_col): # check if the neighboring cell is safe
                        neighboring_cost = costs[neighboring_row][neighboring_col] + 1
                        if neighboring_cost < costs[row][col]:
                            costs[row][col] = neighboring_cost
                            changed = True


    return costs

def getNextPosition(room, position, costs):
    current_row, current_col = position 
    
    if costs[current_row][current_col] == 0:
        return None
    best_cost = float("inf")
    best_position = None
    for direction in directions:
        row_offset, col_offset = directions[direction]
        next_row = current_row + row_offset
        next_col = current_col + col_offset
        if is_safe(room, next_row, next_col):
            next_cost = costs[next_row][next_col]
            if next_cost < best_cost:
                best_cost =next_cost 
                best_position = (next_row, next_col)

    return best_position
 
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

def plan_path(room, start, goal, planner="bfs"):
    if planner == "bfs":
        return bfs(room, start, goal)
    elif planner == "dp": 
        costs = calculate_cost(room, goal) 
        path = []
        current_position = start
        while current_position is not None:
            path.append(current_position)
            nextPosition =getNextPosition(room,current_position,costs)
            current_position = nextPosition
        return path 

if __name__ == "__main__":
    from environment import room, goal

    costs = calculate_cost(room, goal)

    for cost in costs:
        print(cost)
        print(getNextPosition(room, (0, 0), costs))


       