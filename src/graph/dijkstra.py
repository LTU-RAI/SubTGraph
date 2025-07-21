import numpy as np
from utils import *

from scipy.sparse.csgraph import dijkstra
from scipy.sparse import csr_matrix

###

toIndex = lambda row, column: row * grid_columns + column
toPair  = lambda index: divmod(index, grid_columns)

def harmonic_signal_matrix(start, end, nodes, grid_shape):
    """
    Create a matrix with a harmonic signal from start to end point.
    
    Parameters:
    - start: tuple (x0, y0)
    - end: tuple (x1, y1)
    - nodes: int, number of nodes (zero crossings)
    - grid_shape: tuple (height, width) of the matrix
    
    Returns:
    - matrix: 2D numpy array with 1s on the harmonic path
    """
    x0, y0 = start
    x1, y1 = end

    # Number of samples along the path
    num_points = int(np.hypot(x1 - x0, y1 - y0) * 4)  # Increase for smoother curves
    
    # Linear path (t from 0 to 1)
    t = np.linspace(0, 1, num_points)
    x = x0 + (x1 - x0) * t
    y = y0 + (y1 - y0) * t

    # Direction perpendicular to the path
    dx = x1 - x0
    dy = y1 - y0
    length = np.hypot(dx, dy)
    if length == 0:
        raise ValueError("Start and end points cannot be the same")
    perp_dx = -dy / length
    perp_dy = dx / length

    # Apply sine wave offset (amplitude scales with distance for visibility)
    amplitude = min(grid_shape) / 20  # You can adjust this
    frequency = nodes * np.pi  # Full sine cycles across the path
    offset = amplitude * np.sin(frequency * t)

    x_wave = x + offset * perp_dx
    y_wave = y + offset * perp_dy

    # Initialize grid
    matrix = np.ones(grid_shape) * np.inf # np.zeros(grid_shape, dtype=int)

    # Map wave to grid
    for xi, yi in zip(x_wave, y_wave):
        ix, iy = int(round(xi)), int(round(yi))
        if 0 <= ix < grid_shape[1] and 0 <= iy < grid_shape[0]:
            matrix[iy, ix] = 1

    return matrix

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

def dijkstraSolver(initial_node, desired_node, grid_size):

    cost_grid = harmonic_signal_matrix((initial_node[1], initial_node[0]), (desired_node[1], desired_node[0]), 0, (grid_size, grid_size))
    cost_grid = csr_matrix(cost_adjacency_matrix(cost_grid))

    initial_node = toIndex(*initial_node)
    desired_node = toIndex(*desired_node)

    _, predecessors = dijkstra(csgraph=cost_grid, directed=False, indices=initial_node, return_predecessors=True)
    path = [toPair(i) for i in extract_path(predecessors, desired_node)]

    visited = np.zeros([grid_size, grid_size])
    for node in path:  visited[node[0], node[1]] = 1

    return cost_grid, visited, path