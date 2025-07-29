import math, random, string, yaml, numpy as np

from datetime import datetime
from graph.shape import EmptyShape

###

# !!! PATH TO CONFIGURATION !!!
with open('../config/generation/custom.yaml', 'r') as file:
    config = yaml.safe_load(file)

SUBTGRAPH_PATH = config["repository_path"]      # Repository Path

SAVE_MESH   = config["generation_save_mesh"]    # Allow saving of the mesh
LOAD_MATRIX = config["generation_load_matrix"]  # Allow loading of the topological matrix
SAVE_MATRIX = config["generation_save_matrix"]  # Allow saving of the generation matrix

# Obtain limits of grid as square root of the world length
grid_rows = grid_columns = int(math.sqrt(np.random.randint(low=config["world_min_length"][0], high=config["world_min_length"][1]+1, size=1)[0]))

# Check empty shape
isEmptyShape =   lambda obj:     isinstance(obj, EmptyShape)

# Check openings of the asset based on direction array
isOpenWest =     lambda openings:   "w" in openings
isOpenNorth =    lambda openings:   "n" in openings
isOpenSouth =    lambda openings:   "s" in openings
isOpenEast =     lambda openings:   "e" in openings

# Check the limits of the grid based on coordinates
isLimitNorth =    lambda idx:     idx == 0
isLimitWest  =    lambda jdx:     jdx == 0
isLimitSouth =    lambda idx:     idx == grid_rows - 1
isLimitEast  =    lambda jdx:     jdx == grid_columns - 1

isLimitNorthWest  = lambda idx, jdx: isLimitNorth(idx) and isLimitWest(jdx)
isLimitNorthEast  = lambda idx, jdx: isLimitNorth(idx) and isLimitEast(jdx)
isLimitSouthWest  = lambda idx, jdx: isLimitSouth(idx) and isLimitWest(jdx)
isLimitSouthEast  = lambda idx, jdx: isLimitSouth(idx) and isLimitEast(jdx)

def get_random_id() -> str:
    """
    Generate random 32 length string.

    Returns
    -------
    out : str
        Random 32 length string
    """
    return ''.join(random.choice(string.ascii_letters) for i in range(32))

def get_datetime_id(prefix="subtgraph") -> str:
    """
    Generate date and time string.

    Parameters
    -------
    prefix : str, optional
        Prefix of the string
    
    Returns
    -------
    out : str
        Date and Time string
    """
        
    # Get current date and time
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Combine prefix with the formatted date and time
    return f"{prefix}_{current_time}"