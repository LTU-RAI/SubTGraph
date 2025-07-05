import os, pickle, math, string, yaml, random, bpy, numpy as np

from utils import *

from mathutils import Vector

from build import FactoryObj
from graph.grid import GridMap
from graph.dijkstra import dijkstraSolver

###

random.seed(topology["generation_seed"])
factory_obj = FactoryObj()

###

isValidNode = lambda node, grid_size: not (node[0] < 0 or node[0] >= grid_size) and not (node[1] < 0 or node[1] >= grid_size)

def isContiguous(node, node_array):
    check = False;  contiguous = None
    for i in range(len(node_array)):
        contiguous = node_array[i]
        check = check or \
        (node[0] + 1 == contiguous[0] and node[1]     == contiguous[1]) or \
        (node[0] - 1 == contiguous[0] and node[1]     == contiguous[1]) or \
        (node[0]     == contiguous[0] and node[1] + 1 == contiguous[1]) or \
        (node[0]     == contiguous[0] and node[1] - 1 == contiguous[1])
        if check: break
    return check, contiguous

def updateVisitation(origin, row, col, visitation):
    node = (row, col)
    check, contiguous = isContiguous(node, node_array)
    if check:  node = contiguous
    else:      node_array.append(node)
    visitation += dijkstraSolver(origin, node, [origin], grid_rows)[1]  # Create visitation from user parameters

###

for _ in range(topology["generation_n_worlds"]):  # Generate as many worlds as indicated

    level_array = []
    world_n_levels = np.random.randint(low=topology["world_n_levels"][0], high=topology["world_n_levels"][1]+1, size=1)[0]
    for ldx in range(world_n_levels):   # Reproduce spawn at each level 

        grid = GridMap(withShaft=True if ldx < world_n_levels - 1 else False, level=ldx)  # Create grid map with shaft connection at all levels except the last one
        visitation = np.zeros([grid_rows, grid_columns])

        node_array = []

        world_n_loops_per_level = np.random.randint(low=topology["world_n_loops_per_level"][0], high=topology["world_n_loops_per_level"][1]+1, size=1)[0]
        constraint_loop_array = []
        for _ in range(world_n_loops_per_level):  # Define loop constraints
            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
            constraint_loop_array.append((constraint[0], constraint[1]))
        
            new_constraint = (constraint[0],   constraint[1]+1);  constraint_loop_array.append(new_constraint)
            new_constraint = (constraint[0]+1, constraint[1]+1);  constraint_loop_array.append(new_constraint)
            new_constraint = (constraint[0]+1, constraint[1]);    constraint_loop_array.append(new_constraint)

        for cdx in range(0, len(constraint_loop_array), 4):

            origin = constraint_loop_array[cdx]
            row_constraint = origin[0];  col_constraint = origin[1]
            updateVisitation(origin, np.random.randint(low=0, high=row_constraint-2, size=1)[0],         np.random.randint(low=0, high=col_constraint-2, size=1)[0],         visitation)

            origin = constraint_loop_array[cdx+1]
            row_constraint = origin[0];  col_constraint = origin[1]
            updateVisitation(origin, np.random.randint(low=0, high=row_constraint-2, size=1)[0],         np.random.randint(low=col_constraint+2, high=grid_rows, size=1)[0], visitation)

            origin = constraint_loop_array[cdx+2]
            row_constraint = origin[0];  col_constraint = origin[1]
            updateVisitation(origin, np.random.randint(low=row_constraint+2, high=grid_rows, size=1)[0], np.random.randint(low=0, high=col_constraint-2, size=1)[0],         visitation)

            origin = constraint_loop_array[cdx+3]
            row_constraint = origin[0];  col_constraint = origin[1]
            updateVisitation(origin, np.random.randint(low=row_constraint+2, high=grid_rows, size=1)[0], np.random.randint(low=col_constraint+2, high=grid_rows, size=1)[0], visitation)


        world_n_tjunctions_per_level = np.random.randint(low=topology["world_n_tjunctions_per_level"][0], high=topology["world_n_tjunctions_per_level"][1]+1, size=1)[0]
        constraint_junction_array = []
        constraint_junction_type_array = []
        for _ in range(world_n_tjunctions_per_level):  # Define tjunctions
            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
            constraint_junction_array.append((constraint[0], constraint[1]))

            junction_type = np.random.randint(low=0, high=4, size=1)[0]
            constraint_junction_type_array.append(junction_type)

        for cdx in range(len(constraint_junction_array)):

            junction_type = constraint_junction_type_array[cdx]
            if   junction_type == 0:
                origin = constraint_junction_array[cdx]
                row_constraint = origin[0];  col_constraint = origin[1]

                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-2, size=1)[0],         col_constraint, visitation)
                updateVisitation(origin, np.random.randint(low=row_constraint+2, high=grid_rows, size=1)[0], col_constraint, visitation)
                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+2, high=grid_rows, size=1)[0], visitation)

            elif junction_type == 1:
                origin = constraint_junction_array[cdx]
                row_constraint = origin[0];  col_constraint = origin[1]

                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-2, size=1)[0],         col_constraint, visitation)
                updateVisitation(origin, np.random.randint(low=row_constraint+2, high=grid_rows, size=1)[0], col_constraint, visitation)
                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-2, size=1)[0],         visitation)
                
            elif junction_type == 2:
                origin = constraint_junction_array[cdx]
                row_constraint = origin[0];  col_constraint = origin[1]

                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-2, size=1)[0],         visitation)
                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+2, high=grid_rows, size=1)[0], visitation)
                updateVisitation(origin, np.random.randint(low=row_constraint+2, high=grid_rows, size=1)[0], col_constraint, visitation)
                
            elif junction_type == 3:
                origin = constraint_junction_array[cdx]
                row_constraint = origin[0];  col_constraint = origin[1]

                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-2, size=1)[0],         visitation)
                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+2, high=grid_rows, size=1)[0], visitation)
                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-2, size=1)[0], col_constraint, visitation)
                

        world_n_intersections_per_level = np.random.randint(low=topology["world_n_intersections_per_level"][0], high=topology["world_n_intersections_per_level"][1]+1, size=1)[0]
        constraint_intersection_array = []
        for _ in range(world_n_intersections_per_level):  # Define intersections
            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
            constraint_intersection_array.append((constraint[0], constraint[1]))

        for cdx in range(len(constraint_intersection_array)):

            origin = constraint_intersection_array[cdx]
            row_constraint = origin[0];  col_constraint = origin[1]

            updateVisitation(origin, np.random.randint(low=0, high=row_constraint-2, size=1)[0],         col_constraint,                                                     visitation)
            updateVisitation(origin, np.random.randint(low=row_constraint+2, high=grid_rows, size=1)[0], col_constraint,                                                     visitation)
            updateVisitation(origin, row_constraint,                                                     np.random.randint(low=0, high=col_constraint-2, size=1)[0],         visitation)
            updateVisitation(origin, row_constraint,                                                     np.random.randint(low=col_constraint+2, high=grid_rows, size=1)[0], visitation)


        for node in node_array:  # Set high cost to objective nodes
            visitation[node[0], node[1]] = 1000

        grid.dijkstra_grid(visitation)  # Create grid from visitation satisfying local constraints
        level_array.append(grid)
        print(grid.__str__())

    # exit(0)

    mesh_level_offset_array = []
    mesh_level_rotation_array = []
    mesh_level_filename_array = []
    mesh_level_direction_array = []

    baseOffsetz = 0.0; assetMaxWidth = 0.0
    for ldx in range(len(level_array)):
        level = level_array[ldx]
        try:
            imported_objects, shaftOffset, newBaseOffsetz, newAssetMaxWidth = factory_obj.world(level.grid_map, level.originShaftNode if ldx == 0 else level.destinationShaftNode, 0.0, 0.0, baseOffsetz)  # Create .obj mesh
        except Exception:
            ldx -= 1;  continue

        if newAssetMaxWidth > assetMaxWidth: assetMaxWidth = newAssetMaxWidth
        baseOffsetz += newBaseOffsetz

        if ldx == 0:  
            mesh_level_rotation_array.append(0)
            mesh_level_direction_array.append(level.grid_map[level.originShaftNode[0]][level.originShaftNode[1]].org_diff)  # First level is always 0 degrees

        else:  # Rotate other levels based on the direction of the shaft
            org_direction = mesh_level_direction_array[ldx - 1]
            dst_direction = level.grid_map[level.destinationShaftNode[0]][level.destinationShaftNode[1]].dst_diff

            if ldx < len(level_array) - 1:
                mesh_level_direction_array.append(level.grid_map[level.originShaftNode[0]][level.originShaftNode[1]].org_diff)

            if mesh_level_rotation_array[-1] == 90:
                if   org_direction == ['n']:  org_direction = ['e']
                elif org_direction == ['e']:  org_direction = ['s']
                elif org_direction == ['s']:  org_direction = ['w']
                elif org_direction == ['w']:  org_direction = ['n']

            if mesh_level_rotation_array[-1] == 180:
                if   org_direction == ['n']:  org_direction = ['s']
                elif org_direction == ['s']:  org_direction = ['n']
                elif org_direction == ['e']:  org_direction = ['w']
                elif org_direction == ['w']:  org_direction = ['e']

            if mesh_level_rotation_array[-1] == 270:
                if   org_direction == ['n']:  org_direction = ['w']
                elif org_direction == ['w']:  org_direction = ['s']
                elif org_direction == ['s']:  org_direction = ['e']
                elif org_direction == ['e']:  org_direction = ['n']

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

            # Transform location of origin shaft base on rotation
            if   mesh_level_rotation_array[-1] == 90:   # (-1, 1)
                shaftOffset = [-1 * shaftOffset[1], shaftOffset[0], shaftOffset[2]]
            elif mesh_level_rotation_array[-1] == 180:  # (-1, -1)
                shaftOffset = [-1 * shaftOffset[0], -1 * shaftOffset[1], shaftOffset[2]]
            elif mesh_level_rotation_array[-1] == 270:  # (1, -1)
                shaftOffset = [shaftOffset[1], -1 * shaftOffset[0], shaftOffset[2]]

        mesh_level_offset_array.append(shaftOffset)

        bpy.ops.object.transform_apply(location=True, rotation=True)
        bpy.context.active_object.rotation_euler = (0, 0, math.radians(mesh_level_rotation_array[ldx]))
        bpy.ops.object.transform_apply(location=True, rotation=True)

        filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
        bpy.ops.wm.obj_export(filepath=os.path.join('../tmp', filename + '.obj'))
        mesh_level_filename_array.append(filename)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for fdx in range(len(mesh_level_filename_array)):
        filename = mesh_level_filename_array[fdx]
        bpy.ops.wm.obj_import(filepath=os.path.join('../tmp', filename + '.obj'))

        # Join all imported objects into one
        bpy.ops.object.select_all(action='SELECT')
        for obj in bpy.context.selected_objects:
            obj.select_set(True)
        bpy.ops.object.join()

        merged_obj = bpy.context.active_object
        merged_obj.name = get_random_id()  # Rename the merged object
        
        if fdx < len(mesh_level_filename_array) - 1:
            bpy.context.scene.cursor.location = Vector((mesh_level_offset_array[fdx][0], mesh_level_offset_array[fdx][1], mesh_level_offset_array[fdx][2]))
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')

        merged_obj.location.x = 0.0
        merged_obj.location.y = 0.0
    
    scaleWidth = 1.0
    world_max_width = np.random.randint(low=topology['world_max_width'][0], high=topology['world_max_width'][1]+1, size=1)[0]
    if assetMaxWidth > world_max_width:
        scaleWidth = world_max_width/assetMaxWidth

    scaleLength = 1.0
    world_min_length = np.random.randint(low=topology['world_min_length'][0], high=topology['world_min_length'][1]+1, size=1)[0]
    if merged_obj.dimensions[2] < world_min_length:
        scaleLength = world_min_length/merged_obj.dimensions[2]

    merged_obj.scale = (scaleWidth, 1.0, scaleLength)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
    bpy.ops.wm.obj_export(filepath=os.path.join('../repo', filename + '.obj'))

    for filename in os.listdir('../tmp'):
        file_path = os.path.join('../tmp', filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')