import numpy as np
import matplotlib.pyplot as plt

###

getNodeNorth = lambda node: (node[0]-1, node[1])
getNodeSouth = lambda node: (node[0]+1, node[1])
getNodeWest  = lambda node: (node[0], node[1]-1)
getNodeEast  = lambda node: (node[0], node[1]+1)

isValidNode = lambda node, grid_size: not (node[0] < 0 or node[0] >= grid_size) and not (node[1] < 0 or node[1] >= grid_size)

###

def dijkstra(initial_node, desired_node, grid_size):
    
    path = [initial_node]

    directions = [getNodeNorth, getNodeSouth, getNodeWest, getNodeEast]
    directionsdx = np.linspace(start=0, stop=len(directions), endpoint=False, dtype=np.uint16)

    visited = np.zeros([grid_size, grid_size])
    visited[initial_node[0], initial_node[1]] = 1

    distance_grid = np.zeros([grid_size, grid_size])
    for idx in range(0, grid_size):
        for jdx in range(0, grid_size):
            distance_grid[idx][jdx] = max(abs(desired_node[0] - idx), abs(desired_node[1] - jdx))
    distance_grid[initial_node[0], initial_node[1]] = np.inf

    current_node = [initial_node[0], initial_node[1]]
    while True:
        best_potential_node = current_node
        np.random.shuffle(directionsdx)
        for directiondx in directionsdx:
            direction = directions[directiondx]
            potential_node = direction(current_node)

            if isValidNode(potential_node, grid_size):
                if not visited[potential_node[0], potential_node[1]]:
                    if distance_grid[potential_node[0],potential_node[1]] <= distance_grid[best_potential_node[0], best_potential_node[1]]:
                        best_potential_node = potential_node 

        visited[best_potential_node[0], best_potential_node[1]] = 1
        current_node = [best_potential_node[0], best_potential_node[1]]
        path.append(current_node)

        if current_node[0] == desired_node[0] and current_node[1]==desired_node[1]:  break

    return distance_grid, visited, path