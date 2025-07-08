import math, random, string, yaml, numpy as np

from graph.shape import EmptyShape

###

with open('../config/topology/operational.yaml', 'r') as file:
    topology = yaml.safe_load(file)

grid_rows = grid_columns = int(math.sqrt(np.random.randint(low=topology["world_min_length"][0], high=topology["world_min_length"][1]+1, size=1)[0]))

# Checking the openings of the asset
isOpenWest =     lambda openings:   "w" in openings
isOpenNorth =    lambda openings:   "n" in openings
isOpenSouth =    lambda openings:   "s" in openings
isOpenEast =     lambda openings:   "e" in openings

# Checking the limits of the grid
isLimitNorth =    lambda idx:     idx == 0
isLimitWest  =    lambda jdx:     jdx == 0
isLimitSouth =    lambda idx:     idx == grid_rows - 1
isLimitEast  =    lambda jdx:     jdx == grid_columns - 1

isLimitNorthWest  = lambda idx, jdx: isLimitNorth(idx) and isLimitWest(jdx)
isLimitNorthEast  = lambda idx, jdx: isLimitNorth(idx) and isLimitEast(jdx)
isLimitSouthWest  = lambda idx, jdx: isLimitSouth(idx) and isLimitWest(jdx)
isLimitSouthEast  = lambda idx, jdx: isLimitSouth(idx) and isLimitEast(jdx)

# Checking empty shape
isEmptyShape =   lambda obj:     isinstance(obj, EmptyShape)

def get_random_id():
        return ''.join(random.choice(string.ascii_letters) for i in range(32))