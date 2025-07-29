import numpy as np
from utils import *

from scipy.sparse.csgraph import dijkstra
from scipy.sparse import csr_matrix

###

# Transform (row, column) to an index
get_index = lambda row, column: row * grid_columns + column

# Transform index to (row, column)
get_pair  = lambda index: divmod(index, grid_columns)

def harmonic_cost(start: tuple, end: tuple, hdx: int, shape: tuple) -> np.array:
    """
    Create the cost matrix with a discretized harmonic signal from start to end point.
    
    Parameters
    ----------
    start : tuple
        Starting node (x0, y0)
    end : tuple 
        Objective node (x1, y1)
    hdx : int
        Harmonic type of signal
    shape : tuple 
        Number of (rows, cols) in the matrix
    
    Returns
    ----------
    cost : numpy.array
        Cost matrix with 1s on the signal path
    """

    phi = 4  # Increase for smoother curves

    # Obtain coordinate points
    x0, y0 = start;  x1, y1 = end

    # Obtain number of samples along the path
    num_points = int(np.hypot(x1 - x0, y1 - y0) * phi)  
    
    # Compute linear path (t from 0 to 1)
    t = np.linspace(0, 1, num_points)
    x = x0 + (x1 - x0) * t;  y = y0 + (y1 - y0) * t
    
    # Calculate direction perpendicular to the path
    dx = x1 - x0;  dy = y1 - y0
    length = np.hypot(dx, dy)
    perp_dx = -dy / length;  perp_dy = dx / length

    # Apply sine signal offset (amplitude scales with distance for visibility)
    amplitude = min(shape) / 20
    frequency = hdx * np.pi
    offset = amplitude * np.sin(frequency * t)

    # Compute signal components
    x_signal = x + offset * perp_dx;  y_signal = y + offset * perp_dy
    
    # Discretize signal to grid
    cost = np.ones(shape) * np.inf
    for xi, yi in zip(x_signal, y_signal):  
        ix, iy = int(round(xi)), int(round(yi))
        if 0 <= ix < shape[1] and 0 <= iy < shape[0]:  cost[iy, ix] = 1

    return cost

def adjacency(cost: np.array):
    """
    Compute adjacency matrix from cost grid.

    Parameters
    ----------
    cost : numpy.array
        Dijkstra cost matrix
    
    Returns
    ----------
    adjacency : numpy.array
        Adjacency matrix describing node and edge connections
    """
    rows, cols = cost.shape
    N = rows * cols
    adj_matrix = np.zeros((N, N), dtype=np.float32)

    for rdx in range(rows):
        for cdx in range(cols):
            neighbors = []  # Holder for neighbours of current position
            if rdx > 0:           neighbors.append((rdx - 1, cdx))  # Up
            if rdx < rows - 1:    neighbors.append((rdx + 1, cdx))  # Down
            if cdx > 0:           neighbors.append((rdx, cdx - 1))  # Left
            if cdx < cols - 1:    neighbors.append((rdx, cdx + 1))  # Right

            from_idx = rdx * cols + cdx
            for nr, nc in neighbors:  # Set cost to neighbours
                to_idx = nr * cols + nc
                adj_matrix[from_idx][to_idx] = cost[nr][nc]

    return adj_matrix

def extract_path(predecessors: list, target: int) -> list:
    """
    Backwards extract path from target node following Dijkstra predecessors.

    Parameters
    ----------
    predecessors : list
        List of predecessor nodes to target value (from Dijkstra)
    target : int
        Index value of target node
    
    Returns
    ----------
    path : list
        Node list of Dijkstra selected points
    """
    path = []
    i = target
    while i != -9999:
        path.append(i)
        i = predecessors[i]
    return path[::-1]  # Reverse

###

def dijkstra_solver(start: tuple, end: tuple, size: int) -> tuple:
    """
    Compute Dijkstra path from origin to objective nodes and update visitation.

    Parameters
    ----------
    start : tuple
        Starting node (x0, y0)
    end : tuple 
        Objective node (x1, y1)
    size : int 
        Size of the the matrix
    
    Returns
    ----------
    cost : numpy.array
        Cost matrix from harmonic signal
    visitation : numpy.array
        Visitation matrix from Dijkstra path
    path : list
        Node list of Dijkstra selected points
    """

    # Select harmonic from specified value or desired topology
    if config["generation_route_harmonic"] == -1:
        if   config["generation_topology"] == "linear":     hdx = 0
        elif config["generation_topology"] == "parabolic":  hdx = 1
        elif config["generation_topology"] == "sine":       hdx = 2
    else:
        hdx = config["generation_route_harmonic"]

    # Obtain coordinate points
    x0, y0 = start;  x1, y1 = end

    # Compute cost and associated adajcency matrix
    cost = harmonic_cost((y0, x0), (y1, x1), hdx, (size, size))
    cost = csr_matrix(adjacency(cost))

    # Obtain indexes of start and end nodes
    start = get_index(*start);  end = get_index(*end)

    # Compute Dijkstra path between nodes and extract shortest path
    _, predecessors = dijkstra(csgraph=cost, directed=False, indices=start, return_predecessors=True)
    path = [get_pair(i) for i in extract_path(predecessors, end)]

    # Reflect selected path as a visitation matrix
    visitation = np.zeros([size, size])
    for node in path:  visitation[node[0], node[1]] = 1

    return cost, visitation, path