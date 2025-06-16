import operator, numpy as np

from graph.shape import *
from utils import *
from graph.dijkstra import *

###

class GridMap():

    def __init__(self, withShaft=False, level=0):
        self.grid_map =[[""] * grid_columns for _ in range(grid_rows)]
        self.level = level                # Level of the grid map, used for shaft connection
        self.withShaft = withShaft        # If the grid map has a shaft connection
        self.originShaftNode = None       # Shaft node position in the grid map
        self.destinationShaftNode = None  # Destination shaft node position in the grid map

    def dijkstra_grid(self, visitation):

        getValueNorth = lambda matrix, idx, jdx: matrix[idx-1][jdx]
        getValueSouth = lambda matrix, idx, jdx: matrix[idx+1][jdx]
        getValueWest  = lambda matrix, idx, jdx: matrix[idx][jdx-1]
        getValueEast  = lambda matrix, idx, jdx: matrix[idx][jdx+1]

        def isFeasible(idx, jdx, openings, op=operator.eq):
            
            def isOpening(directions):  # Visitation values as expected in the positions of openings
                boolean = True

                for direction in directions:
                    if   direction == "e":
                        boolean = boolean and op(min(1, getValueEast(visitation, idx, jdx)), openings.get(direction))
                    elif direction == "n":  
                        boolean = boolean and op(min(1, getValueNorth(visitation, idx, jdx)), openings.get(direction))
                    elif direction == "s":  
                        boolean = boolean and op(min(1, getValueSouth(visitation, idx, jdx)), openings.get(direction))
                    elif direction == "w":  
                        boolean = boolean and op(min(1, getValueWest(visitation, idx, jdx)), openings.get(direction))

                return boolean
            
            def isNotOpening(directions):  # No openings for this connection type at different grid limits
                boolean = True

                for direction in directions:
                    boolean = boolean and openings.get(direction) == 0

                return boolean

            if isLimitNorthWest(idx, jdx):    return isOpening("e,s".split(','))   and isNotOpening("n,w".split(','))
            if isLimitNorthEast(idx, jdx):    return isOpening("s,w".split(','))   and isNotOpening("n,e".split(','))
            if isLimitSouthWest(idx, jdx):    return isOpening("e,n".split(','))   and isNotOpening("w,s".split(','))
            if isLimitSouthEast(idx, jdx):    return isOpening("n,w".split(','))   and isNotOpening("e,s".split(','))

            if isLimitNorth(idx):             return isOpening("e,s,w".split(',')) and isNotOpening("n".split(','))
            if isLimitSouth(idx):             return isOpening("e,n,w".split(',')) and isNotOpening("s".split(','))
            if isLimitWest(jdx):              return isOpening("e,n,s".split(',')) and isNotOpening("w".split(','))
            if isLimitEast(jdx):              return isOpening("n,s,w".split(',')) and isNotOpening("e".split(','))

            return isOpening("e,n,s,w".split(','))  # In the middle of the grid


        def populate_connections(idx, jdx, parameters, angle):
            connection_type, openings = parameters[0], parameters[1:]
            connection = ConnectionShape(connection_type, openings)

            if angle != 0:  connection.rotate(angle)  # Rotate if applicable to get correct possible openings
            for openingdx in connection.openings:     # Add openings
                connection.opening(openingdx)

            self.grid_map[idx][jdx] = connection      # Add connection in grid map

        for idx in range(grid_rows):
            for jdx in range(grid_columns):
                
                if visitation[idx][jdx] == 0:  # If not visited it is an empty shape
                    self.grid_map[idx][jdx] = EmptyShape()

                elif visitation[idx][jdx] >= 1000:   # If objective node add openings accordingly
                    self.grid_map[idx][jdx] = NodeShape() 
                    if isFeasible(idx, jdx, {"n": 1, "s": 0, "w": 0, "e": 0}, operator.ge):  self.grid_map[idx][jdx].opening("n")
                    if isFeasible(idx, jdx, {"n": 0, "s": 1, "w": 0, "e": 0}, operator.ge):  self.grid_map[idx][jdx].opening("s")
                    if isFeasible(idx, jdx, {"n": 0, "s": 0, "w": 1, "e": 0}, operator.ge):  self.grid_map[idx][jdx].opening("w")
                    if isFeasible(idx, jdx, {"n": 0, "s": 0, "w": 0, "e": 1}, operator.ge):  self.grid_map[idx][jdx].opening("e")

                    if self.withShaft:
                        
                        if self.originShaftNode is None:  # If shaft enabled, add shaft only once
                            if self.grid_map[idx][jdx].openings.__len__() == 3: 
                                self.originShaftNode = [idx, jdx]  # Save shaft node position
                                self.grid_map[idx][jdx].set_origin_shaft()

                        elif self.destinationShaftNode is None and self.level != 0:  # If shaft enabled, add shaft only once
                            if self.grid_map[idx][jdx].openings.__len__() == 3: 
                                self.destinationShaftNode = [idx, jdx]  # Save shaft node position
                                self.grid_map[idx][jdx].set_destination_shaft()

                    else:  # If shaft not enabled, save first node as shaft node

                        if self.destinationShaftNode is None:  # If shaft enabled, add shaft only once
                            if self.grid_map[idx][jdx].openings.__len__() == 3: 
                                self.destinationShaftNode = [idx, jdx]  # Save shaft node position
                                self.grid_map[idx][jdx].set_destination_shaft()

                else:
                    corner_params       = topology["env_asset_list_type_b"]["corner"]["parameters"].split(',')
                    straight_params     = topology["env_asset_list_type_b"]["straight"]["parameters"].split(',')
                    junction_params     = topology["env_asset_list_type_b"]["junction"]["parameters"].split(',')
                    intersection_params = topology["env_asset_list_type_b"]["intersection"]["parameters"].split(',')

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

                    else:   
                        raise ValueError("Invalid connection configuration at idx: {}, jdx: {} in visitation \n{}".format(idx, jdx, visitation.astype(np.uint8)))
                    

    def __str__(self):
        str_format = "\n\n"
        for idx in range(grid_rows):
            str_grid = [""] * 6
            n_empty = 0
            for jdx in range(grid_columns):
                if isEmptyShape(self.grid_map[idx][jdx]): n_empty += 1
                for gridx, grid_element in enumerate(self.grid_map[idx][jdx].get_shape().split("\n")[:-1], start=0):  
                    str_grid[gridx] += grid_element

            if n_empty == grid_columns:  continue
            for gridx in range(6): # New line
                str_format += str_grid[gridx] + "\n"
                
        str_format += "\n"
        return str_format
