import numpy as np
from utils import *

from scipy.sparse.csgraph import dijkstra
from graph.cost import create_heatmaps
from scipy.sparse import csr_matrix

###

toIndex = lambda row, column: row * grid_columns + column
toPair  = lambda index: divmod(index, grid_columns)

def extract_path(predecessors, target):
    path = []
    i = target
    while i != -9999:
        path.append(i)
        i = predecessors[i]
    return path[::-1]  # reverse

def cost_adjacency_matrix(cost_grid):
    rows, cols = cost_grid.shape
    N = rows * cols
    adj_matrix = np.zeros((N, N), dtype=np.float32)

    def idx(r, c):
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            from_idx = idx(r, c)

            neighbors = []
            if r > 0:           neighbors.append((r - 1, c))  # Up
            if r < rows - 1:    neighbors.append((r + 1, c))  # Down
            if c > 0:           neighbors.append((r, c - 1))  # Left
            if c < cols - 1:    neighbors.append((r, c + 1))  # Right

            for nr, nc in neighbors:
                to_idx = idx(nr, nc)
                adj_matrix[from_idx][to_idx] = cost_grid[nr][nc]

    return adj_matrix


def linearPath(matrix_shape, initial, desired, cost=np.array([])):
    cost = np.ones(matrix_shape) * np.inf if len(cost) == 0 else cost

    if initial[0] == desired[0]:
        row = desired[0]
        sign = 1 if desired[1] > initial[1] else -1
        for col in range(initial[1] + sign, desired[1], sign):
            cost[row, col] = 1

    elif initial[1] == desired[1]:
        col = desired[1]
        sign = 1 if desired[0] > initial[0] else -1
        for row in range(initial[0] + sign, desired[0], sign):
            cost[row, col] = 1

    return cost


def parabolicPath(matrix_shape, initial, desired, cost=np.array([])):
    cost = np.ones(matrix_shape) * np.inf if len(cost) == 0 else cost

    if initial[0] == desired[0]:
        row = desired[0]
        sign = 1 if desired[1] > initial[1] else -1
        
        distance = abs(desired[1] - initial[1]) - 1
        if distance%2 == 0:
            level = 1;  top = 0; parabolic_sign = 1;  check = lambda level: level <= (distance-2)//2
            for col in range(initial[1] + sign, desired[1], sign):
                if check(level):  # Escalate
                    cost[max(row - level, 0), col] = 1
                    cost[min(row + level, matrix_shape[0]-1), col] = 1
                    level += parabolic_sign
                else: # Retain
                    cost[max(row - level, 0), col] = 1
                    cost[min(row + level, matrix_shape[0]-1), col] = 1
                    top += 1

                    if top == 2:
                        level -= 1;  parabolic_sign = -1;  check = lambda level: level > 0
        else:
            level = 1;  parabolic_sign = 1;  check = lambda level: level <= distance//2
            for col in range(initial[1] + sign, desired[1], sign):
                if check(level) :  # Escalate
                    cost[max(row - level, 0), col] = 1
                    cost[min(row + level, matrix_shape[0]-1), col] = 1
                    level += parabolic_sign
                else: # Retain
                    cost[max(row - level, 0), col] = 1
                    cost[min(row + level, matrix_shape[0]-1), col] = 1
                    level -= 1;  parabolic_sign = -1;  check = lambda level: level > 0

    elif initial[1] == desired[1]:
        col = desired[1]
        sign = 1 if desired[0] > initial[0] else -1

        distance = abs(desired[0] - initial[0]) - 1
        if distance%2 == 0:
            level = 1;  top = 0; parabolic_sign = 1;  check = lambda level: level <= (distance-2)//2
            for row in range(initial[0] + sign, desired[0], sign):
                if check(level):  # Escalate
                    cost[row, max(col - level, 0)] = 1
                    cost[row, min(col + level, matrix_shape[0]-1)] = 1
                    level += parabolic_sign
                else: # Retain
                    cost[row, max(col - level, 0)] = 1
                    cost[row, min(col + level, matrix_shape[0]-1)] = 1
                    top += 1
                    if top == 2:
                        level -= 1;  parabolic_sign = -1;  check = lambda level: level > 0
        else:
            level = 1;  parabolic_sign = 1;  check = lambda level: level <= distance//2
            for row in range(initial[0] + sign, desired[0], sign):
                if check(level) :  # Escalate
                    cost[row, max(col - level, 0)] = 1
                    cost[row, min(col + level, matrix_shape[0]-1)] = 1
                    level += parabolic_sign
                else: # Retain
                    cost[row, max(col - level, 0)] = 1
                    cost[row, min(col + level, matrix_shape[0]-1)] = 1
                    level -= 1;  parabolic_sign = -1;  check = lambda level: level > 0

    return cost


def sinePath(matrix_shape, initial, desired, cost=np.array([])):
    cost = np.ones(matrix_shape) * np.inf if len(cost) == 0 else cost

    if initial[0] == desired[0]:
        row = desired[0]
        sign = 1 if desired[1] > initial[1] else -1

        for col in range(initial[1] + sign, desired[1], sign):
            if abs((initial[1] + sign) - col)%2 != 0:  # Odd
                cost[row, col] = 1
            else: # Even
                cost[max(row - 1, 0), col] = 1
                cost[min(row + 1, matrix_shape[0]-1), col] = 1
    elif initial[1] == desired[1]:
        col = desired[1]
        sign = 1 if desired[0] > initial[0] else -1

        for row in range(initial[0] + sign, desired[0], sign):
            if abs((initial[0] + sign) - row)%2 != 0:  # Odd
                cost[row, col] = 1
            else: # Even
                cost[row, max(col - 1, 0)] = 1
                cost[row, min(col + 1, matrix_shape[0]-1)] = 1

    return cost

###

def dijkstraSolver(initial_node, desired_node, grid_size):

    cost_grid = np.array([])

    if topology['generation_topology'] == 'linear':      cost_grid = linearPath((grid_size, grid_size), (initial_node[0], initial_node[1]), (desired_node[0], desired_node[1]), cost_grid)
    if topology['generation_topology'] == 'parabolic':   cost_grid = parabolicPath((grid_size, grid_size), (initial_node[0], initial_node[1]), (desired_node[0], desired_node[1]), cost_grid)
    if topology['generation_topology'] == 'sine':        cost_grid = sinePath((grid_size, grid_size), (initial_node[0], initial_node[1]), (desired_node[0], desired_node[1]), cost_grid)

    cost_grid[initial_node[0], initial_node[1]] = np.inf
    cost_grid[desired_node[0], desired_node[1]] = np.inf

    cost_grid = csr_matrix(cost_adjacency_matrix(cost_grid))

    initial_node = toIndex(*initial_node)
    desired_node = toIndex(*desired_node)

    _, predecessors = dijkstra(csgraph=cost_grid, directed=False, indices=initial_node, return_predecessors=True)
    path = [toPair(i) for i in extract_path(predecessors, desired_node)]

    visited = np.zeros([grid_size, grid_size])
    for node in path:  visited[node[0], node[1]] = 1

    return cost_grid, visited, path