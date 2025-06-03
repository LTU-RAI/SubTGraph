import math, random, string, yaml, numpy as np

from graph.shape import EmptyShape

###

with open('../config/topology.yaml', 'r') as file:
    topology = yaml.safe_load(file)

grid_rows = grid_columns = int(math.sqrt(topology["world_max_length"]))

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


def quickSort(array: list):  # O(n * log(n))
    if array.__len__() <= 1:  return array

    distance = [0] * array.__len__()
    for idx in range(array.__len__()):
        distance[idx] = math.sqrt(array[idx][0]**2 + array[idx][1]**2)

    pivot = np.random.randint(0, array.__len__())

    idx = 0;  left = 0
    while idx < array.__len__():
        if idx == pivot:  idx += 1;  continue

        if distance[idx] < distance[pivot]:  left += 1
        idx += 1

    tmp_left  = [0] * left
    tmp_right = [0] * (array.__len__() - left - 1)

    idx = 0;  idx_left = 0;  idx_right = 0
    while idx < array.__len__():
        if idx == pivot:  idx += 1;  continue

        if distance[idx] < distance[pivot]:  tmp_left[idx_left] = array[idx];    idx_left += 1
        else:                                tmp_right[idx_right] = array[idx];  idx_right += 1
        idx += 1
    
    return quickSort(tmp_left) + [array[pivot]] + quickSort(tmp_right)
