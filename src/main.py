import os, pickle, math, string, yaml, random, bpy, numpy as np

from utils import *

from build import FactoryObj
from graph.grid import GridMap
from graph.dijkstra import dijkstra

###

random.seed(topology["generation_seed"])

factory_obj = FactoryObj()
origin = np.random.randint(low=0, high=grid_rows, size=2)

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

    level_array = []
    for ldx in range(topology["world_n_levels"]):   # Reproduce spawn at each level 

        grid = GridMap(withShaft=True if ldx < topology["world_n_levels"] - 1 else False, level=ldx)  # Create grid map with shaft connection at all levels except the last one
        visitation = np.zeros([grid_rows, grid_columns])

        node_array = []
        for _ in range(topology["world_n_nodes_per_level"] - len(node_array)):

            node = None
            while True:  # Define objective nodes (not contiguous)
                node = np.random.randint(low=0, high=grid_rows, size=2)
                if not isContiguous(node, node_array):  break
            node_array.append(node)

            _, visited, _ = dijkstra(origin, node, grid_rows)  # Create visitation from user parameters
            visitation += visited

        for node in node_array:  # Set high cost to objective nodes
            visitation[node[0], node[1]] = 1000
            
        grid.dijkstra_grid(visitation)  # Create grid from visitation satisfying local constraints
        level_array.append(grid)
        print(grid.__str__())

    baseOffsetx = 0.0;  baseOffsety = 0.0;  baseOffsetz = 0.0
    mesh_level_array = []
    for ldx, level in enumerate(level_array):
        origin = level.originShaftNode if ldx == 0 else level.destinationShaftNode  # Set origin shaft node for first level, destination shaft node for others
        mergedObj, shaftOffsetx, shaftOffsety, shaftOffsetz = factory_obj.world(level.grid_map, origin, baseOffsetx, baseOffsety, baseOffsetz)  # Create .obj mesh
        baseOffsetx += shaftOffsetx;  baseOffsety += shaftOffsety;  baseOffsetz += shaftOffsetz

        filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
        bpy.ops.wm.obj_export(filepath=os.path.join('../tmp', filename + '.obj'))
        mesh_level_array.append(filename)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for fdx, filename in enumerate(mesh_level_array):
        bpy.ops.wm.obj_import(filepath=os.path.join('../tmp', filename + '.obj'))
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        # if fdx > 0:
        #     bpy.ops.object.transform_apply(rotation=True)
        #     bpy.context.active_object.rotation_euler = (0, 0, math.radians(180))
        #     bpy.ops.object.transform_apply(rotation=True)

    # Join all imported objects into one
    for obj in bpy.context.selected_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]  # Set active for join
    bpy.ops.object.join()

    merged_obj = bpy.context.active_object
    merged_obj.name = get_random_id()  # Rename the merged object

    filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
    bpy.ops.wm.obj_export(filepath=os.path.join('../repo', filename + '.obj'))

    for filename in os.listdir('../tmp'):
        file_path = os.path.join('../tmp', filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')