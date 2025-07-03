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

###

def dijkstraSolver(initial_node, desired_node, constraints, grid_size):

    cost_grid = create_heatmaps((grid_size, grid_size), (initial_node[0], initial_node[1]), [(desired_node[0], desired_node[1])], constraints)[0][0]

    cost_grid[initial_node[0], initial_node[1]] = np.inf
    cost_grid = csr_matrix(cost_adjacency_matrix(cost_grid))

    initial_node = toIndex(*initial_node)
    desired_node = toIndex(*desired_node)

    _, predecessors = dijkstra(csgraph=cost_grid, directed=False, indices=initial_node, return_predecessors=True)
    path = [toPair(i) for i in extract_path(predecessors, desired_node)]

    visited = np.zeros([grid_size, grid_size])
    for node in path:  visited[node[0], node[1]] = 1

    return cost_grid, visited, path