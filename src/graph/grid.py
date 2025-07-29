import operator, numpy as np

from graph.shape import *
from utils import *
from graph.dijkstra import *

###

class GridMap():

    def __init__(self, withOriginShaft=False, withDestinationShaft=False, level=0):
        self.level = level  # Level of the grid map, used for shaft connection

        self.withOriginShaft = withOriginShaft              # If the grid map has a shaft connection
        self.withDestinationShaft = withDestinationShaft    # If the grid map receives a shaft connection

        self.originShaftNode = None                         # Shaft node position in the grid map
        self.destinationShaftNode = None                    # Destination shaft node position in the grid map

        # Grid of the topology, initially empty strings and transforms to (EmptyShape, ConnectionShape, NodeShape)
        self.grid_map =[[""] * grid_columns for _ in range(grid_rows)]


    def toShapes(self, visitation: np.array):
        """
        Transform visitation matrix onto object-level grid representation.
        
        Parameters
        ----------
        visitation : numpy.array
            The visitation matrix
        """

        def isFeasible(idx: int, jdx: int, requirement: list, op=operator.eq) -> bool:
            """
            Check occupancy of the given openings from the position in the grid.

            Parameters
            ----------
            idx : int
                The row of the selected tile
            jdx : int
                The column of the selected tile
            requirement : list
                The list of direction requirements to be satisfied
            op : (function), optional
                Operator to compare openings with requirements

            Returns
            ----------
            out : bool
                True if all requirements are satisfied, False otherwise
            """
            
            def isOpening(directions: list) -> bool:
                """
                Openings at given requirement positions.
                
                Parameters
                ----------
                directions : list
                    The opening directions of the connection type

                Returns
                ----------
                out : bool
                    True if openings at given requirement positions, False otherwise
                """
                boolean = True

                for direction in directions:  # For every possible irection
                    if   direction == "e":   boolean = boolean and op(min(1, getValueEast( visitation, idx, jdx)), requirement.get(direction))
                    elif direction == "n":   boolean = boolean and op(min(1, getValueNorth(visitation, idx, jdx)), requirement.get(direction))
                    elif direction == "s":   boolean = boolean and op(min(1, getValueSouth(visitation, idx, jdx)), requirement.get(direction))
                    elif direction == "w":   boolean = boolean and op(min(1, getValueWest( visitation, idx, jdx)), requirement.get(direction))

                return boolean
            
            def isNotOpening(directions: list) -> bool:
                """
                No openings at given requirement positions
                
                Parameters
                ----------
                directions : list
                    The opening directions of the connection type

                Returns
                ----------
                out : bool
                    True if no openings exist, False otherwise
                """

                boolean = True

                for direction in directions:
                    boolean = boolean and requirement.get(direction) == 0

                return boolean

            # Corner positions
            if isLimitNorthWest(idx, jdx):    return isOpening("e,s".split(','))   and isNotOpening("n,w".split(','))
            if isLimitNorthEast(idx, jdx):    return isOpening("s,w".split(','))   and isNotOpening("n,e".split(','))
            if isLimitSouthWest(idx, jdx):    return isOpening("e,n".split(','))   and isNotOpening("w,s".split(','))
            if isLimitSouthEast(idx, jdx):    return isOpening("n,w".split(','))   and isNotOpening("e,s".split(','))

            # Border positions
            if isLimitNorth(idx):             return isOpening("e,s,w".split(',')) and isNotOpening("n".split(','))
            if isLimitSouth(idx):             return isOpening("e,n,w".split(',')) and isNotOpening("s".split(','))
            if isLimitWest(jdx):              return isOpening("e,n,s".split(',')) and isNotOpening("w".split(','))
            if isLimitEast(jdx):              return isOpening("n,s,w".split(',')) and isNotOpening("e".split(','))

            # Any position
            return isOpening("e,n,s,w".split(','))

        def populate_connections(idx: int, jdx: int, parameters: list, angle: int):
            """
            Instantiate connection at specified position with given parameters
            
            Parameters
            ----------
            idx : int
                The row of the selected tile
            jdx : int
                The column of the selected tile
            parameters : list
                The list of parameters for this tile (connection_type, openings)
            angle : int
                Rotation to apply on the asset
            """
            connection_type, openings = parameters[0], parameters[1:]
            connection = ConnectionShape(connection_type, openings)

            if angle != 0:  connection.rotate(angle)  # Rotate if applicable to get correct possible openings
            for openingdx in connection.openings:     # Add openings
                connection.opening(openingdx)

            self.grid_map[idx][jdx] = connection      # Add connection in grid map

        for idx in range(grid_rows):
            for jdx in range(grid_columns):
                
                # If not visited is an empty shape
                if visitation[idx][jdx] == 0:  
                    self.grid_map[idx][jdx] = EmptyShape()

                # If node, add openings according to the feasibility
                elif visitation[idx][jdx] >= 10:   
                    self.grid_map[idx][jdx] = NodeShape() 

                    # Check feasibility of each opening in the grid
                    # Greater or equal operator, it is satisifed with any positive value within the limits of the grid
                    if isFeasible(idx, jdx, {"n": 1, "s": 0, "w": 0, "e": 0}, operator.ge):  self.grid_map[idx][jdx].opening("n")
                    if isFeasible(idx, jdx, {"n": 0, "s": 1, "w": 0, "e": 0}, operator.ge):  self.grid_map[idx][jdx].opening("s")
                    if isFeasible(idx, jdx, {"n": 0, "s": 0, "w": 1, "e": 0}, operator.ge):  self.grid_map[idx][jdx].opening("w")
                    if isFeasible(idx, jdx, {"n": 0, "s": 0, "w": 0, "e": 1}, operator.ge):  self.grid_map[idx][jdx].opening("e")

                    # If not last level
                    if self.withOriginShaft:
                        
                        # Add origin shaft only once
                        if self.originShaftNode is None:  
                            if self.grid_map[idx][jdx].openings.__len__() == 3:         # Shaft is a node with only one opening
                                self.originShaftNode = [idx, jdx]                       # Save shaft node position
                                self.grid_map[idx][jdx].set_origin_shaft()              # Update node to be a shaft

                        # Add destination shaft only once to all levels except first
                        elif self.destinationShaftNode is None and self.level != 0:  
                            if self.grid_map[idx][jdx].openings.__len__() == 3:         # Shaft is a node with only one opening
                                self.destinationShaftNode = [idx, jdx]                  # Save shaft node position
                                self.grid_map[idx][jdx].set_destination_shaft()         # Update node to be a shaft placeholder (empty)

                    # If last level, save first node as shaft
                    elif self.withDestinationShaft and not self.withOriginShaft:

                        # Add destination shaft only once
                        if self.destinationShaftNode is None:
                            if self.grid_map[idx][jdx].openings.__len__() == 3:         # Shaft is a node with only one opening
                                self.destinationShaftNode = [idx, jdx]                  # Save shaft node position
                                self.grid_map[idx][jdx].set_destination_shaft()         # Update node to be a shaft placeholder (empty)

                # If connection, add openings according to the feasibility
                else:

                    # Obtain parameters from configuration file
                    corner_params       = config["env_asset_list_type_b"]["corner"]["parameters"].split(',')
                    straight_params     = config["env_asset_list_type_b"]["straight"]["parameters"].split(',')
                    junction_params     = config["env_asset_list_type_b"]["junction"]["parameters"].split(',')
                    intersection_params = config["env_asset_list_type_b"]["intersection"]["parameters"].split(',')

                    # Equal operator, it is satisifed with exactly the given value

                    # Straight connection
                    if   isFeasible(idx, jdx, {"n": 0, "s": 0, "w": 1, "e": 1}): populate_connections(idx, jdx, straight_params, angle=0)
                    elif isFeasible(idx, jdx, {"n": 1, "s": 1, "w": 0, "e": 0}): populate_connections(idx, jdx, straight_params, angle=90)

                    # Corner connection
                    elif isFeasible(idx, jdx, {"n": 0, "s": 1, "w": 0, "e": 1}): populate_connections(idx, jdx, corner_params, angle=0)
                    elif isFeasible(idx, jdx, {"n": 0, "s": 1, "w": 1, "e": 0}): populate_connections(idx, jdx, corner_params, angle=90)
                    elif isFeasible(idx, jdx, {"n": 1, "s": 0, "w": 1, "e": 0}): populate_connections(idx, jdx, corner_params, angle=180)
                    elif isFeasible(idx, jdx, {"n": 1, "s": 0, "w": 0, "e": 1}): populate_connections(idx, jdx, corner_params, angle=270)

                    # Junction connection
                    elif isFeasible(idx, jdx, {"n": 1, "s": 1, "w": 0, "e": 1}): populate_connections(idx, jdx, junction_params, angle=0)
                    elif isFeasible(idx, jdx, {"n": 0, "s": 1, "w": 1, "e": 1}): populate_connections(idx, jdx, junction_params, angle=90)
                    elif isFeasible(idx, jdx, {"n": 1, "s": 1, "w": 1, "e": 0}): populate_connections(idx, jdx, junction_params, angle=180)
                    elif isFeasible(idx, jdx, {"n": 1, "s": 0, "w": 1, "e": 1}): populate_connections(idx, jdx, junction_params, angle=270)

                    # Intersection connection
                    elif isFeasible(idx, jdx, {"n": 1, "s": 1, "w": 1, "e": 1}): populate_connections(idx, jdx, intersection_params, angle=0)

    def __str__(self):  # Format grid object as a string
        str_format = "\n\n"
        for idx in range(grid_rows):
            str_grid = [""] * 6
            n_empty = 0
            for jdx in range(grid_columns):
                if isEmptyShape(self.grid_map[idx][jdx]): n_empty += 1
                for gridx, grid_element in enumerate(self.grid_map[idx][jdx].get_shape().split("\n")[:-1], start=0):  
                    str_grid[gridx] += grid_element

            if n_empty == grid_columns:  continue  # Eliminate empty rows and columns
            for gridx in range(6): # New line
                str_format += str_grid[gridx] + "\n"
                
        str_format += "\n"
        return str_format
