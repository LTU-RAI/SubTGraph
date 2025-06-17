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
    mesh_level_direction_array = []
    mesh_level_offset_array = []
    mesh_level_rotation_array = []
    for ldx, level in enumerate(level_array):
        mergedObj, shaftOffsetx, shaftOffsety, shaftOffsetz = factory_obj.world(level.grid_map, level.originShaftNode if ldx == 0 else level.destinationShaftNode, baseOffsetx, baseOffsety, baseOffsetz)  # Create .obj mesh
        baseOffsetx += shaftOffsetx;  baseOffsety += shaftOffsety;  
        baseOffsetz += shaftOffsetz

        print(shaftOffsetx, shaftOffsety, shaftOffsetz)
        print(baseOffsetx, baseOffsety, baseOffsetz)

        if ldx == 0:  
            mesh_level_rotation_array.append(0)
            mesh_level_direction_array.append(level.grid_map[level.originShaftNode[0]][level.originShaftNode[1]].org_diff)  # First level is always 0 degrees

        else:  # Rotate other levels based on the direction of the shaft
            org_direction = mesh_level_direction_array[ldx - 1]
            dst_direction = level.grid_map[level.destinationShaftNode[0]][level.destinationShaftNode[1]].dst_diff

            if ldx < len(level_array) - 1:
                mesh_level_direction_array.append(level.grid_map[level.originShaftNode[0]][level.originShaftNode[1]].org_diff)

            if mesh_level_rotation_array[ldx - 1] == 90:
                if org_direction == ['n']:  org_direction = ['e']
                if org_direction == ['s']:  org_direction = ['w']
                if org_direction == ['e']:  org_direction = ['s']
                if org_direction == ['w']:  org_direction = ['n']

            if mesh_level_rotation_array[ldx - 1] == 180:
                if org_direction == ['n']:  org_direction = ['s']
                if org_direction == ['s']:  org_direction = ['n']
                if org_direction == ['e']:  org_direction = ['w']
                if org_direction == ['w']:  org_direction = ['e']

            if mesh_level_rotation_array[ldx - 1] == 270:
                if org_direction == ['n']:  org_direction = ['w']
                if org_direction == ['s']:  org_direction = ['e']  
                if org_direction == ['e']:  org_direction = ['n']
                if org_direction == ['w']:  org_direction = ['s'] 

            print(org_direction, dst_direction)

            if dst_direction == ['n']:
                if   org_direction == ['s']:  mesh_level_rotation_array.append(0)
                elif org_direction == ['e']:  mesh_level_rotation_array.append(270)
                elif org_direction == ['w']:  mesh_level_rotation_array.append(90)
                else:                         mesh_level_rotation_array.append(180)

            if dst_direction == ['s']:
                if   org_direction == ['n']:  mesh_level_rotation_array.append(0)
                elif org_direction == ['e']:  mesh_level_rotation_array.append(90)
                elif org_direction == ['w']:  mesh_level_rotation_array.append(270)
                else:                         mesh_level_rotation_array.append(180)

            if dst_direction == ['e']:
                if   org_direction == ['n']:  mesh_level_rotation_array.append(90)
                elif org_direction == ['s']:  mesh_level_rotation_array.append(270)
                elif org_direction == ['w']:  mesh_level_rotation_array.append(0)
                else:                         mesh_level_rotation_array.append(180)

            if dst_direction == ['w']:
                if   org_direction == ['n']:  mesh_level_rotation_array.append(270)
                elif org_direction == ['s']:  mesh_level_rotation_array.append(90)
                elif org_direction == ['e']:  mesh_level_rotation_array.append(0)
                else:                         mesh_level_rotation_array.append(180)

        print(mesh_level_rotation_array)

        bpy.ops.object.transform_apply(rotation=True)
        bpy.context.active_object.rotation_euler = (0, 0, math.radians(mesh_level_rotation_array[ldx]))
        bpy.ops.object.transform_apply(rotation=True)

        filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
        bpy.ops.wm.obj_export(filepath=os.path.join('../tmp', filename + '.obj'))
        mesh_level_array.append(filename)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for filename in mesh_level_array:
        bpy.ops.wm.obj_import(filepath=os.path.join('../tmp', filename + '.obj'))
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

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