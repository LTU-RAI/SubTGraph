import os, pickle, math, string, pickle, random, bpy, shutil, numpy as np

from utils import *
from mathutils import Vector

from build import FactoryObj
from graph.grid import GridMap
from graph.dijkstra import dijkstraSolver

###

random.seed(config["generation_seed"])
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

def isVisited(constraint_set_choice, constraint, visitation):
    if constraint_set_choice == 0:  # Loops
        return visitation[constraint[0], constraint[1]] > 0 or \
               visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]+1] > 0 or \
               visitation[constraint[0]-1, constraint[1]-1] > 0 or visitation[constraint[0]+1, constraint[1]-1] > 0 or visitation[constraint[0]-1, constraint[1]+1] > 0 or visitation[constraint[0]+1, constraint[1]+1] > 0

    elif constraint_set_choice == 1:  # T-Junctions
        constraint, constraint_type = constraint
        if constraint_type == 0:  # Right
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0 or visitation[constraint[0], constraint[1]+1] > 0
        elif constraint_type == 1:  # Left
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0
        elif constraint_type == 2:  # Down
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]+1] > 0 or visitation[constraint[0]+1, constraint[1]] > 0
        elif constraint_type == 3:  # Up
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0]-1, constraint[1]] > 0
        
    elif constraint_set_choice == 2:  # Intersections
        return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0

def updateVisitation(origin, row, col, visitation):
    node = (row, col)
    check, contiguous = isContiguous(node, node_array)
    if check:  node = contiguous
    else:      node_array.append(node)
    visitation += dijkstraSolver(origin, node, grid_rows)[1]  # Create visitation from user parameters

###

for _ in range(config["generation_n_worlds"]):  # Generate as many worlds as indicated

    level_array = []
    level_origin_array = []
    level_visitation_array = []

    ###

    try:

        if LOAD_MATRIX:

            folder = config["generation_load_folder"].split('/')[-1]

            with open(os.path.join(SUBTGRAPH_PATH, config["generation_load_folder"], "pkl", "subtgraph.topological.pkl"), 'rb') as file:
                try:                    level_visitation_array = pickle.load(file)
                except Exception as e:  print(f"Error loading file: {e}")

            world_n_levels = len(level_visitation_array)        
            for ldx, visitation in enumerate(level_visitation_array):
                grid = GridMap(withDestinationShaft=(world_n_levels > 1), withOriginShaft=(ldx < world_n_levels - 1), level=ldx)  # Create grid map with shaft connection at all levels except the last one
                grid.dijkstra_grid(visitation)
                if config["generation_output"]:  print(grid.__str__())

                updated = False
                for idx in range(visitation.shape[0]):
                    for jdx in range(visitation.shape[1]):
                        if updated:                       continue
                        elif grid.grid_map[idx][jdx].id == 1:  level_origin_array.append((idx, jdx));  updated = True

                level_array.append(grid)

        else:

            folder = get_datetime_id()
            os.mkdir(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder))

            world_n_levels = np.random.randint(low=config["world_n_levels"][0], high=config["world_n_levels"][1]+1, size=1)[0]
            for ldx in range(world_n_levels):   # Reproduce spawn at each level 

                accepted = False
                while not accepted:

                    grid = GridMap(withDestinationShaft=(world_n_levels > 1), withOriginShaft=(ldx < world_n_levels - 1), level=ldx)  # Create grid map with shaft connection at all levels except the last one
                    visitation = np.zeros([grid_rows, grid_columns])

                    node_array = []

                    world_n_loops_per_level         = np.random.randint(low=config["world_n_loops_per_level"][0], high=config["world_n_loops_per_level"][1]+1, size=1)[0]
                    world_n_tjunctions_per_level    = np.random.randint(low=config["world_n_tjunctions_per_level"][0], high=config["world_n_tjunctions_per_level"][1]+1, size=1)[0]
                    world_n_intersections_per_level = np.random.randint(low=config["world_n_intersections_per_level"][0], high=config["world_n_intersections_per_level"][1]+1, size=1)[0]

                    print(f"World {ldx+1} - Loops: {world_n_loops_per_level}, T-Junctions: {world_n_tjunctions_per_level}, Intersections: {world_n_intersections_per_level}")

                    if world_n_loops_per_level == 0 and world_n_tjunctions_per_level == 0 and world_n_intersections_per_level == 0:  continue

                    nIter = 0
                    while (world_n_loops_per_level > 0 or world_n_tjunctions_per_level > 0 or world_n_intersections_per_level > 0) and nIter < 100:
                        constraint_set_choice = np.random.randint(low=0, high=3, size=1)[0]

                        if constraint_set_choice == 0 and world_n_loops_per_level > 0:  # Loops
                            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)

                            if isVisited(constraint_set_choice, constraint, visitation):  continue
                            visitation[constraint[0]-1, constraint[1]] = 1  
                            visitation[constraint[0]+1, constraint[1]] = 1  
                            visitation[constraint[0], constraint[1]-1] = 1  
                            visitation[constraint[0], constraint[1]+1] = 1  

                            origin = (constraint[0]-1, constraint[1]-1)
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)

                            origin = (constraint[0]-1,   constraint[1]+1)
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)

                            origin = (constraint[0]+1, constraint[1]-1)
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)

                            origin = (constraint[0]+1, constraint[1]+1)
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)

                            world_n_loops_per_level -= 1

                        elif constraint_set_choice == 1 and world_n_tjunctions_per_level > 0:  # T-Junctions
                            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
                            junction_type = np.random.randint(low=0, high=4, size=1)[0]

                            if isVisited(constraint_set_choice, (constraint, junction_type), visitation): continue
                            visitation[constraint[0], constraint[1]] = 1

                            if   junction_type == 0:
                                origin = (constraint[0]-1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         col_constraint, visitation)

                                origin = (constraint[0]+1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint, visitation)

                                origin = (constraint[0], constraint[1]+1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)

                            elif junction_type == 1:
                                origin = (constraint[0]-1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         col_constraint, visitation)
                                
                                origin = (constraint[0]+1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint, visitation)
                                
                                origin = (constraint[0], constraint[1]-1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)

                            elif junction_type == 2:
                                origin = (constraint[0], constraint[1]-1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)
                                
                                origin = (constraint[0], constraint[1]+1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)
                                
                                origin = (constraint[0]+1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint, visitation)
                                
                            elif junction_type == 3:
                                origin = (constraint[0], constraint[1]-1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)
                                
                                origin = (constraint[0], constraint[1]+1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)
                                
                                origin = (constraint[0]-1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0], col_constraint,         visitation)

                            world_n_tjunctions_per_level -= 1

                        elif constraint_set_choice == 2 and world_n_intersections_per_level > 0:  # Intersections
                            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)

                            if isVisited(constraint_set_choice, constraint, visitation):  continue
                            visitation[constraint[0], constraint[1]] = 1

                            origin = (constraint[0]-1, constraint[1])
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         col_constraint,                                                     visitation)
                            
                            origin = (constraint[0]+1, constraint[1])
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint,                                                     visitation)
                            
                            origin = (constraint[0], constraint[1]-1)
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, row_constraint,                                                     np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)
                            
                            origin = (constraint[0], constraint[1]+1)
                            row_constraint = origin[0];  col_constraint = origin[1]
                            updateVisitation(origin, row_constraint,                                                     np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)

                            world_n_intersections_per_level -= 1

                        nIter += 1

                    if nIter >= 100:  continue

                    for node in node_array:  # Set high cost to objective nodes
                        visitation[node[0], node[1]] = 10

                    for idx in range(visitation.shape[0]):
                        for jdx in range(visitation.shape[1]):
                            visitation[idx, jdx] = 1 if visitation[idx, jdx] > 0 and visitation[idx, jdx] < 10 else visitation[idx, jdx]

                    for idx in range(visitation.shape[0]):
                        for jdx in range(visitation.shape[1]):
                            if visitation[idx, jdx] == 10:  continue

                            occupancy = 0;  nodes = 0
                            if visitation[max(idx-1, 0), jdx] != 10:                        occupancy += visitation[max(idx-1, 0), jdx] 
                            else:                                                           nodes += 1

                            if visitation[min(idx+1, visitation.shape[0]-1), jdx] != 10:    occupancy += visitation[min(idx+1, visitation.shape[0]-1), jdx]
                            else:                                                           nodes += 1

                            if visitation[idx, max(jdx-1, 0)] != 10:                        occupancy += visitation[idx, max(jdx-1, 0)]  
                            else:                                                           nodes += 1

                            if visitation[idx, min(jdx+1, visitation.shape[1]-1)] != 10:    occupancy += visitation[idx, min(jdx+1, visitation.shape[1]-1)]
                            else:                                                           nodes += 1

                            if (occupancy == 0 and nodes < 2) or (occupancy == 1 and nodes == 0):  visitation[idx, jdx] = 0

                    grid.dijkstra_grid(visitation)  # Create grid from visitation satisfying local constraints
                    if config["generation_output"]:  print(grid.__str__())

                    if config["generation_level_control"]:
                        userAnswer = input("Press enter to continue, or type 'x' to remake this level: ")
                        if userAnswer.lower() != 'x':  accepted = True
                    else:  accepted = True

                level_array.append(grid)
                level_origin_array.append(node_array[0])
                level_visitation_array.append(visitation)

        ###

        if SAVE_MATRIX and not LOAD_MATRIX:
            os.mkdir(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, 'pkl'))

            matrix = []
            for ldx in range(world_n_levels):  matrix.append(level_visitation_array[ldx])
            with open(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, "pkl", "subtgraph.topological.pkl"), "wb") as file:
                pickle.dump(np.array(matrix), file)

            matrix = []
            for ldx in range(world_n_levels):
                visitation = level_visitation_array[ldx].copy()
                for node in node_array:
                    visitation[node[0], node[1]] = 1
                matrix.append(visitation)

            with open(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, "pkl", "subtgraph.structural.pkl"), "wb") as file:
                pickle.dump(np.array(matrix), file)

            matrix = []
            for ldx in range(world_n_levels):
                grid_map = level_array[ldx].grid_map
                visitation = level_visitation_array[ldx].copy()

                for idx in range(visitation.shape[0]):
                    for jdx in range(visitation.shape[1]):
                        visitation[idx, jdx] = grid_map[idx][jdx].id

                matrix.append(visitation)

            with open(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, "pkl", "subtgraph.spatial.pkl"), "wb") as file:
                pickle.dump(np.array(matrix), file)

        ###

        if SAVE_MESH:

            mesh_level_offset_array = []
            mesh_level_rotation_array = []
            mesh_level_filename_array = []
            mesh_level_direction_array = []

            os.mkdir(os.path.join(SUBTGRAPH_PATH, 'tmp', folder))
            baseOffsetz = 0.0;  assetMaxWidth = 0.0
            for ldx in range(world_n_levels):

                level = level_array[ldx]
                origin = level_origin_array[ldx]
                if len(level_array) > 1:
                    origin = level.originShaftNode if ldx == 0 else level.destinationShaftNode

                try:
                    imported_objects, shaftOffset, newBaseOffsetz, newAssetMaxWidth = factory_obj.world(level.grid_map, origin, 0.0, 0.0, baseOffsetz, folder)  # Create .obj mesh
                except Exception as e: print(f"Internal error during build, please try again: {e}");  exit(0)

                if newAssetMaxWidth > assetMaxWidth: assetMaxWidth = newAssetMaxWidth
                baseOffsetz += newBaseOffsetz

                if ldx == 0:  
                    mesh_level_rotation_array.append(0)

                    if len(level_array) > 1:
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
                bpy.ops.wm.obj_export(filepath=os.path.join(SUBTGRAPH_PATH, 'tmp', folder, filename + '.obj'))
                mesh_level_filename_array.append(filename)

            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

            for fdx in range(len(mesh_level_filename_array)):
                filename = mesh_level_filename_array[fdx]
                bpy.ops.wm.obj_import(filepath=os.path.join(SUBTGRAPH_PATH, 'tmp', folder, filename + '.obj'))

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
            world_max_width = np.random.randint(low=config['world_max_width'][0], high=config['world_max_width'][1]+1, size=1)[0]
            if assetMaxWidth > world_max_width:
                scaleWidth = world_max_width/assetMaxWidth

            scaleLength = 1.0
            world_min_length = np.random.randint(low=config['world_min_length'][0], high=config['world_min_length'][1]+1, size=1)[0]
            if merged_obj.dimensions[2] < world_min_length:
                scaleLength = world_min_length/merged_obj.dimensions[2]

            merged_obj.scale = (scaleWidth, scaleWidth, scaleLength)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            bpy.ops.wm.obj_export(filepath=os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, 'subtgraph.obj'))
            shutil.rmtree(os.path.join(SUBTGRAPH_PATH, "tmp", folder))

            temp_dir = bpy.context.preferences.filepaths.temporary_directory
            if os.path.exists(temp_dir):
                for file_name in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file_name)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

    except:
        shutil.rmtree(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder))
        shutil.rmtree(os.path.join(SUBTGRAPH_PATH, "tmp", folder))