import os, pickle, math, string, pickle, random, bpy, shutil, numpy as np

from utils import *
from mathutils import Vector

from build import FactoryObj
from graph.grid import GridMap
from graph.dijkstra import dijkstraSolver

###

random.seed(config["generation_seed"])  # Initialize random seed
factory_obj = FactoryObj()

###

isValidNode = lambda node, grid_size: not (node[0] < 0 or node[0] >= grid_size) and not (node[1] < 0 or node[1] >= grid_size)
"""
Check if a node is valid within the grid size.

Parameters
----------
node : tuple
    The node (x, y) to check
grid_size : int
    The size of the grid (same width and height)

Returns
-------
out: bool
    True if the node is valid, False otherwise
"""

def isContiguous(node: tuple, node_array: list) -> tuple:
    """
    Check if a node is contiguous with any node in the array.
    
    Parameters
    ----------
    node : tuple
        The node (x, y) to check
    node_array : list
        The array of nodes [(x, y), ...] to check against
    
    Returns
    -------
    check: bool
        True if contiguous node is found
    contiguous: tuple 
        (x, y) if the contiguous node is found, else None
    """
    check = False;  contiguous = None
    for i in range(len(node_array)):  # For every node
        contiguous = node_array[i]
        check = check or \
        (node[0] + 1 == contiguous[0] and node[1]     == contiguous[1]) or \
        (node[0] - 1 == contiguous[0] and node[1]     == contiguous[1]) or \
        (node[0]     == contiguous[0] and node[1] + 1 == contiguous[1]) or \
        (node[0]     == contiguous[0] and node[1] - 1 == contiguous[1])
        if check: break  # Check if contiguous node is found
    return check, contiguous

def isVisited(constraint_set_choice: int, constraint: list, visitation: np.array) -> bool:
    """
    Check if the constraint is already visited based on the constraint set choice.

    Parameters
    ----------
    constraint_set_choice : int
        Choice of constraint set (0: Loops, 1: T-Junctions, 2: Intersections)
    constraint : list
        The node constraints [(x, y), ...] to check
    visitation : numpy.array
        The visitation matrix

    Returns
    -------
    out: bool
        True if the any of the nodes in the constraint is visited, False otherwise
    """

    # Loops
    # x x x
    # x o x
    # x x x
    if constraint_set_choice == 0:  
        return visitation[constraint[0], constraint[1]] > 0     or \
               visitation[constraint[0]-1, constraint[1]] > 0   or visitation[constraint[0]+1, constraint[1]] > 0   or visitation[constraint[0], constraint[1]-1] > 0   or visitation[constraint[0], constraint[1]+1] > 0   or \
               visitation[constraint[0]-1, constraint[1]-1] > 0 or visitation[constraint[0]+1, constraint[1]-1] > 0 or visitation[constraint[0]-1, constraint[1]+1] > 0 or visitation[constraint[0]+1, constraint[1]+1] > 0

    # T-Junctions
    #  0    1     2      3
    # x o  o x  x x x  o x o
    # x x  x x  o x o  x x x
    # x o  o x
    elif constraint_set_choice == 1: 
        constraint, constraint_type = constraint
        if constraint_type == 0:    # Right
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0 or visitation[constraint[0], constraint[1]+1] > 0
        elif constraint_type == 1:  # Left
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0
        elif constraint_type == 2:  # Down
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]+1] > 0 or visitation[constraint[0]+1, constraint[1]] > 0
        elif constraint_type == 3:  # Up
            return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0]-1, constraint[1]] > 0
        
    # Intersections
    # o x o
    # x x x
    # o x o
    elif constraint_set_choice == 2:
        return visitation[constraint[0], constraint[1]] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0], constraint[1]-1] > 0 or visitation[constraint[0]-1, constraint[1]] > 0 or visitation[constraint[0]+1, constraint[1]] > 0

def updateVisitation(origin: tuple, row: int, col: int, visitation: np.array) -> None:
    """
    Compute Dijkstra path from origin to objective nodes and update visitation.

    Parameters
    ----------
    origin : tuple
        Origin node for the Dijkstra algorithm
    row : int
        The row of the objective node
    col : int
        The column of the objective node
    visitation : numpy.array
        The visitation matrix
    """
    node = (row, col)
    check, contiguous = isContiguous(node, node_array)
    if check:  node = contiguous
    else:      node_array.append(node)
    visitation += dijkstraSolver(origin, node, grid_rows)[1]

###

for _ in range(config["generation_n_worlds"]):  # Generate as many worlds as indicated

    level_array = []                # Holder of grid level objects
    level_origin_array = []         # Holder of initial node to build mesh level recursively
    level_visitation_array = []     # Holder of visitation level matrices

    ###

    try:

        if LOAD_MATRIX:  # Load matrix to visualize or generate mesh if specified by the user

            # Load topology matrix from specified folder
            folder = config["generation_load_folder"].split('/')[-1]
            with open(os.path.join(SUBTGRAPH_PATH, config["generation_load_folder"], "pkl", "subtgraph.topological.pkl"), 'rb') as file:
                try:                    level_visitation_array = pickle.load(file)
                except Exception as e:  print(f"Error loading file: {e}")

            # Compute shapes grid from visitation
            world_n_levels = len(level_visitation_array)        
            for ldx, visitation in enumerate(level_visitation_array):
                # Create grid map with shaft connection at all levels except the last one
                grid = GridMap(withDestinationShaft=(world_n_levels > 1), withOriginShaft=(ldx < world_n_levels - 1), level=ldx)
                grid.toShapes(visitation)  # Transform visitation to object-based matrix
                
                if config["generation_output"]:  print(grid.__str__())  # Output grid if specified

                # Find first node for mesh generation
                updated = False
                for idx in range(visitation.shape[0]):
                    for jdx in range(visitation.shape[1]):
                        if updated:                       continue
                        elif grid.grid_map[idx][jdx].id == 1:  level_origin_array.append((idx, jdx));  updated = True  # Store starting node

                level_array.append(grid)  # Store grid level object

        else:  # Generate random grid with user specifications

            folder = get_datetime_id()  # Create folder to store generated files
            os.mkdir(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder))

            world_n_levels = np.random.randint(low=config["world_n_levels"][0], high=config["world_n_levels"][1]+1, size=1)[0]
            for ldx in range(world_n_levels):  # Compute grid at each level

                accepted = False
                while not accepted:  # Recalculate grid until accepted by the user

                    # Create grid map with shaft connection at all levels except the last one
                    grid = GridMap(withDestinationShaft=(world_n_levels > 1), withOriginShaft=(ldx < world_n_levels - 1), level=ldx)
                    visitation = np.zeros([grid_rows, grid_columns])

                    node_array = []  # Holder for all nodes in grid

                    # Obtain constraints specifications from user
                    world_n_loops_per_level         = np.random.randint(low=config["world_n_loops_per_level"][0], high=config["world_n_loops_per_level"][1]+1, size=1)[0]
                    world_n_tjunctions_per_level    = np.random.randint(low=config["world_n_tjunctions_per_level"][0], high=config["world_n_tjunctions_per_level"][1]+1, size=1)[0]
                    world_n_intersections_per_level = np.random.randint(low=config["world_n_intersections_per_level"][0], high=config["world_n_intersections_per_level"][1]+1, size=1)[0]

                    if config["generation_output"]:  # Output constraints if specified
                        print(f"World {ldx+1} - Loops: {world_n_loops_per_level}, T-Junctions: {world_n_tjunctions_per_level}, Intersections: {world_n_intersections_per_level}")

                    # Recalculate grid if no constraints have been considered during random selection
                    if world_n_loops_per_level == 0 and world_n_tjunctions_per_level == 0 and world_n_intersections_per_level == 0:  continue

                    iter = 0  # Define limit of iterations for non-solvable topologies
                    while (world_n_loops_per_level > 0 or world_n_tjunctions_per_level > 0 or world_n_intersections_per_level > 0) and iter < 100:
                        constraint_set_choice = np.random.randint(low=0, high=3, size=1)[0]  # Randomly select constraint type

                        # Loops
                        # x x x
                        # x o x
                        # x x x
                        if constraint_set_choice == 0 and world_n_loops_per_level > 0:

                            # Discard random position for constraint if already occupied
                            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
                            if isVisited(constraint_set_choice, constraint, visitation):  continue

                            # Update visitation for non-corner constraints
                            visitation[constraint[0]-1, constraint[1]] = 1  
                            visitation[constraint[0]+1, constraint[1]] = 1  
                            visitation[constraint[0], constraint[1]-1] = 1  
                            visitation[constraint[0], constraint[1]+1] = 1  

                            # Update visitation with calculated Dijkstra path between corner constraint and random guided objective node
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

                            world_n_loops_per_level -= 1  # Update number of loops left in generation

                        # T-Junctions
                        #  0    1     2      3
                        # x o  o x  x x x  o x o
                        # x x  x x  o x o  x x x
                        # x o  o x
                        elif constraint_set_choice == 1 and world_n_tjunctions_per_level > 0:

                            # Discard random position for constraint if already occupied
                            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
                            junction_type = np.random.randint(low=0, high=4, size=1)[0]
                            if isVisited(constraint_set_choice, (constraint, junction_type), visitation): continue

                            # Update visitation for non-corner constraints
                            visitation[constraint[0], constraint[1]] = 1

                            if   junction_type == 0:  # Update visitation with calculated Dijkstra path between corner constraint and random guided objective node
                                origin = (constraint[0]-1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         col_constraint, visitation)

                                origin = (constraint[0]+1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint, visitation)

                                origin = (constraint[0], constraint[1]+1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)

                            elif junction_type == 1:  # Update visitation with calculated Dijkstra path between corner constraint and random guided objective node
                                origin = (constraint[0]-1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0],         col_constraint, visitation)
                                
                                origin = (constraint[0]+1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint, visitation)
                                
                                origin = (constraint[0], constraint[1]-1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)

                            elif junction_type == 2:  # Update visitation with calculated Dijkstra path between corner constraint and random guided objective node
                                origin = (constraint[0], constraint[1]-1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)
                                
                                origin = (constraint[0], constraint[1]+1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)
                                
                                origin = (constraint[0]+1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=row_constraint+1, high=grid_rows, size=1)[0], col_constraint, visitation)
                                
                            elif junction_type == 3:  # Update visitation with calculated Dijkstra path between corner constraint and random guided objective node
                                origin = (constraint[0], constraint[1]-1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=0, high=col_constraint-1, size=1)[0],         visitation)
                                
                                origin = (constraint[0], constraint[1]+1)
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, row_constraint, np.random.randint(low=col_constraint+1, high=grid_rows, size=1)[0], visitation)
                                
                                origin = (constraint[0]-1, constraint[1])
                                row_constraint = origin[0];  col_constraint = origin[1]
                                updateVisitation(origin, np.random.randint(low=0, high=row_constraint-1, size=1)[0], col_constraint,         visitation)

                            world_n_tjunctions_per_level -= 1  # Update number of junctions left in generation

                        # Intersections
                        # o x o
                        # x x x
                        # o x o
                        elif constraint_set_choice == 2 and world_n_intersections_per_level > 0:

                            # Discard random position for constraint if already occupied
                            constraint = np.random.randint(low=3, high=grid_rows-3, size=2)
                            if isVisited(constraint_set_choice, constraint, visitation):  continue

                            # Update visitation for non-corner constraints
                            visitation[constraint[0], constraint[1]] = 1

                            # Update visitation with calculated Dijkstra path between corner constraint and random guided objective node
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

                            world_n_intersections_per_level -= 1  # Update number of interesections left in generation

                        iter += 1  # Update number of iterations needed to spawn all node constraints

                    if iter >= 100:  continue  # Discard non-solvable topologies

                    # Change value of nodes to identify during shape association
                    for node in node_array:  visitation[node[0], node[1]] = 10

                    # Change value of edge connections to identify during shape association
                    for idx in range(visitation.shape[0]):
                        for jdx in range(visitation.shape[1]):
                            visitation[idx, jdx] = 1 if visitation[idx, jdx] > 0 and visitation[idx, jdx] < 10 else visitation[idx, jdx]

                    # Remove non-feasible edges during generation
                    for idx in range(visitation.shape[0]):
                        for jdx in range(visitation.shape[1]):
                            if visitation[idx, jdx] == 10:  continue  # Omit nodes

                            edge_occupancy = 0;  node_occupancy = 0  # Compute edge and node occupancy
                            if visitation[max(idx-1, 0), jdx] != 10:                        edge_occupancy += visitation[max(idx-1, 0), jdx] 
                            else:                                                           node_occupancy += 1

                            if visitation[min(idx+1, visitation.shape[0]-1), jdx] != 10:    edge_occupancy += visitation[min(idx+1, visitation.shape[0]-1), jdx]
                            else:                                                           node_occupancy += 1

                            if visitation[idx, max(jdx-1, 0)] != 10:                        edge_occupancy += visitation[idx, max(jdx-1, 0)]  
                            else:                                                           node_occupancy += 1

                            if visitation[idx, min(jdx+1, visitation.shape[1]-1)] != 10:    edge_occupancy += visitation[idx, min(jdx+1, visitation.shape[1]-1)]
                            else:                                                           node_occupancy += 1

                            # Discard edge if (next to nodes with no edge connections) OR (next to one edge with no node connections)
                            if (edge_occupancy == 0 and node_occupancy < 2) or (edge_occupancy == 1 and node_occupancy == 0):  visitation[idx, jdx] = 0

                    grid.toShapes(visitation)  # Transform visitation to object-based matrix

                    if config["generation_output"]:  print(grid.__str__())  # Output constraints if specified

                    if config["generation_level_control"]:  # Allow user approval of grid topology
                        userAnswer = input("Press enter to continue, or type 'x' to remake this level: ")
                        if userAnswer.lower() != 'x':  accepted = True
                    else:  accepted = True  # Consider first generated instance if no user control

                # Update level topology, origin and visitation for mesh generation
                level_array.append(grid)
                level_origin_array.append(node_array[0])
                level_visitation_array.append(visitation)

        ###

        if SAVE_MATRIX and not LOAD_MATRIX:  # Save matrices describing asset type and topology information if specified by the user
            os.mkdir(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, 'pkl'))

            matrix = []  # Visitation matrix describing the graph topology {Empty: 0, Edge: 1, Node: 10}
            for ldx in range(world_n_levels):  matrix.append(level_visitation_array[ldx])
            with open(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, "pkl", "subtgraph.topological.pkl"), "wb") as file:
                pickle.dump(np.array(matrix), file)

            matrix = []  # Structural matrix describing the grid topology {Empty: 0, Occupied: 1})
            for ldx in range(world_n_levels):
                visitation = level_visitation_array[ldx].copy()
                for node in node_array:
                    visitation[node[0], node[1]] = 1
                matrix.append(visitation)

            with open(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, "pkl", "subtgraph.structural.pkl"), "wb") as file:
                pickle.dump(np.array(matrix), file)

            matrix = []  # Spatial matrix describing the grid components {Empty: 0, Node: 1, Straight: 2, Corner: 3, Junction: 4, Intersection: 5}
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

        if SAVE_MESH:   # Generate and save mesh if specified by the user

            mesh_level_offset_array = []        # Holder of vertical offsets
            mesh_level_rotation_array = []      # Holder of level rotations
            mesh_level_filename_array = []      # Holder of level temporal objects
            mesh_level_direction_array = []     # Holder of shaft directions

            # Create temporal folder to store level meshes
            os.mkdir(os.path.join(SUBTGRAPH_PATH, 'tmp', folder))

            baseOffsetz = 0.0;  assetMaxWidth = 0.0  # Vertical offset and maximum width
            for ldx in range(world_n_levels):

                level = level_array[ldx]
                origin = level_origin_array[ldx]
                if len(level_array) > 1:  # Consider origin opening of the shaft for first level otherwise destination opening
                    origin = level.originShaftNode if ldx == 0 else level.destinationShaftNode

                try:  # Recursively create .obj mesh of level following the grid topology
                    imported_objects, shaftOffset, newBaseOffsetz, newAssetMaxWidth = factory_obj.world(level.grid_map, origin, 0.0, 0.0, baseOffsetz, folder)  
                except Exception as e: print(f"Internal error during build, please try again: {e}");  exit(0)

                if newAssetMaxWidth > assetMaxWidth: assetMaxWidth = newAssetMaxWidth  # Update maximum asset width in mesh
                baseOffsetz += newBaseOffsetz  # Update vertical offset

                if ldx == 0:   # Update rotation and direction of first level
                    mesh_level_rotation_array.append(0)

                    if len(level_array) > 1:  # First level is always 0 degrees
                        mesh_level_direction_array.append(level.grid_map[level.originShaftNode[0]][level.originShaftNode[1]].org_diff)  

                else:  # Rotate and translate other levels based on the direction of the shaft
                    org_direction = mesh_level_direction_array[ldx - 1]
                    dst_direction = level.grid_map[level.destinationShaftNode[0]][level.destinationShaftNode[1]].dst_diff

                    if ldx < len(level_array) - 1:  # Add direction of origin shaft for next level without any rotations
                        mesh_level_direction_array.append(level.grid_map[level.originShaftNode[0]][level.originShaftNode[1]].org_diff)

                    # Origin shaft has been rotated, it's facing a new direction
                    # Update directions of origin shaft based on its rotation

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

                    # Origin and destination shafts are facing different directions, destination shaft needs to be rotated
                    # Update rotation of destination shaft based on its direction wrt. origin shaft

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

                    # Transform offsets of origin shaft based on rotation
                    if   mesh_level_rotation_array[-1] == 90:   # (-1, 1)
                        shaftOffset = [-1 * shaftOffset[1], shaftOffset[0], shaftOffset[2]]

                    elif mesh_level_rotation_array[-1] == 180:  # (-1, -1)
                        shaftOffset = [-1 * shaftOffset[0], -1 * shaftOffset[1], shaftOffset[2]]
                        
                    elif mesh_level_rotation_array[-1] == 270:  # (1, -1)
                        shaftOffset = [shaftOffset[1], -1 * shaftOffset[0], shaftOffset[2]]

                # Destination shaft becomes origin shaft in the next level
                mesh_level_offset_array.append(shaftOffset)

                # Apply translation and rotation transforms
                bpy.ops.object.transform_apply(location=True, rotation=True)
                bpy.context.active_object.rotation_euler = (0, 0, math.radians(mesh_level_rotation_array[ldx]))
                bpy.ops.object.transform_apply(location=True, rotation=True)

                # Export mesh to temporary folder
                filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
                bpy.ops.wm.obj_export(filepath=os.path.join(SUBTGRAPH_PATH, 'tmp', folder, filename + '.obj'))
                mesh_level_filename_array.append(filename)

            # Select and remove all objects in blender python memory
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

            for fdx in range(len(mesh_level_filename_array)):  # For each generated mesh level
                filename = mesh_level_filename_array[fdx]
                bpy.ops.wm.obj_import(filepath=os.path.join(SUBTGRAPH_PATH, 'tmp', folder, filename + '.obj'))

                # Join mesh with previous level
                bpy.ops.object.select_all(action='SELECT')
                for obj in bpy.context.selected_objects:
                    obj.select_set(True)
                bpy.ops.object.join()

                merged_obj = bpy.context.active_object
                merged_obj.name = get_random_id()  # Rename the merged object
                
                if fdx < len(mesh_level_filename_array) - 1:  # If not last level

                    # Locate blender cursor to location of shaft for the next level
                    bpy.context.scene.cursor.location = Vector((mesh_level_offset_array[fdx][0], mesh_level_offset_array[fdx][1], mesh_level_offset_array[fdx][2]))
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')

                # Move merged object to the center, for connecting with next level
                merged_obj.location.x = 0.0
                merged_obj.location.y = 0.0
            
            scaleWidth = 1.0  # Apply width scale based on ratio with user specifications
            world_max_width = np.random.randint(low=config['world_max_width'][0], high=config['world_max_width'][1]+1, size=1)[0]
            if assetMaxWidth > world_max_width:
                scaleWidth = world_max_width/assetMaxWidth

            scaleLength = 1.0  # Apply length scale based on ratio with user specifications
            world_min_length = np.random.randint(low=config['world_min_length'][0], high=config['world_min_length'][1]+1, size=1)[0]
            if merged_obj.dimensions[2] < world_min_length:
                scaleLength = world_min_length/merged_obj.dimensions[2]

            # Apply scale transforms to merged object
            merged_obj.scale = (scaleWidth, scaleWidth, scaleLength)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            # Export object and remove elements in temporal folder
            bpy.ops.wm.obj_export(filepath=os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder, 'subtgraph.obj'))
            shutil.rmtree(os.path.join(SUBTGRAPH_PATH, "tmp", folder))

            # Remove elements in blender's temporal directory
            temp_dir = bpy.context.preferences.filepaths.temporary_directory
            if os.path.exists(temp_dir):
                for file_name in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file_name)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

            # Select and remove all objects in blender python memory
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

    except:
        # Remove generated mesh and temporal folders if any error occurs during generation
        shutil.rmtree(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder))
        shutil.rmtree(os.path.join(SUBTGRAPH_PATH, "tmp", folder))