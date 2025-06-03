import os, pickle, math, string, yaml, random, bpy, numpy as np

from utils import *

from build import FactoryObj
from graph.grid import GridMap
from graph.dijkstra import dijkstra

###

random.seed(topology["generation_seed"])

factory_obj = FactoryObj()
grid = GridMap()

origin = np.random.randint(low=0, high=grid_rows, size=2)
visitation = np.zeros([grid_rows, grid_columns])

###

def isContiguous(node, node_array):
    check = False
    for i in range(len(node_array)):
        check = check or \
        (node[0] + 1 == node_array[i][0] and node[1]     == node_array[i][1]) or \
        (node[0] - 1 == node_array[i][0] and node[1]     == node_array[i][1]) or \
        (node[0]     == node_array[i][0] and node[1] + 1 == node_array[i][1]) or \
        (node[0]     == node_array[i][0] and node[1] - 1 == node_array[i][1])
    return check


for _ in range(topology["generation_n_worlds"]):  # Generate as many worlds as indicated

    for _ in range(topology["world_n_levels"]):   # Reproduce spawn at each level 

        node_array = []
        for _ in range(topology["world_n_nodes_per_level"]):

            node = None
            while True:  # Define objective nodes (not contiguous)
                node = np.random.randint(low=0, high=grid_rows, size=2)
                if not isContiguous(node, node_array):  break
            node_array.append(node)

            # TODO Update with cost matrix
            _, visited, _ = dijkstra(origin, node, grid_rows)
            visitation += visited

        # TODO Add constraints

        for node in node_array:  # Set high cost to objective nodes
            visitation[node[0], node[1]] = 1000
            
        grid.dijkstra_grid(visitation)  # ??
        node_array = quickSort(node_array) # ??
        print(grid.__str__())

        # filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
        # factory_obj.world(grid.grid_map)  # Create .obj mesh
        # bpy.ops.wm.obj_export(filepath=os.path.join('../repo', filename + '.obj'))