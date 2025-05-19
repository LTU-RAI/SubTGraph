import numpy as np

from utils import *
from dijkstra import *
from shape import *

###

class GridMap():

    def __init__(self):
        self.grid_map =[[""] * N_COLUMN for _ in range(N_ROW)]        # To store elements of type 'r,X,*' with X number of doors and * direction of openings

    def maze_grid(self):

        def populate_door(idx, jdx, direction_list):
            open_door = False
            
            for direction in direction_list:           
                if direction == 'e':
                    if not empty_shape(self.grid_map[idx][jdx+1]) and door_west(self.grid_map[idx][jdx+1].doors):   
                        self.grid_map[idx][jdx].door('e');  open_door = True
                elif direction == 'w':
                    if not empty_shape(self.grid_map[idx][jdx-1]) and door_east(self.grid_map[idx][jdx-1].doors):     
                        self.grid_map[idx][jdx].door('w');  open_door = True
                elif direction == 'n':
                    if not empty_shape(self.grid_map[idx-1][jdx]) and door_south(self.grid_map[idx-1][jdx].doors):  
                        self.grid_map[idx][jdx].door('n');  open_door = True
                elif direction == 's':
                    if not empty_shape(self.grid_map[idx+1][jdx]) and door_north(self.grid_map[idx+1][jdx].doors): 
                        self.grid_map[idx][jdx].door('s');  open_door = True

            return open_door

        def populate_room(idx, jdx):
            self.grid_map[idx][jdx] = RoomShape()
            open_door = False

            if side_north(idx):
                if side_west(jdx):      open_door = populate_door(idx, jdx, 'e,n'.split(','))
                elif side_east(jdx):    open_door = populate_door(idx, jdx, 'w,n'.split(','))
                else:                   open_door = populate_door(idx, jdx, 'w,e,n'.split(','))
            
            elif side_south(idx):
                if side_west(jdx):      open_door = populate_door(idx, jdx, 'e,s'.split(','))
                elif side_east(jdx):    open_door = populate_door(idx, jdx, 'w,s'.split(','))
                else:                   open_door = populate_door(idx, jdx, 'e,w,s'.split(','))

            elif side_west(jdx):        open_door = populate_door(idx, jdx, 'e,n,s'.split(','))
            elif side_east(jdx):        open_door = populate_door(idx, jdx, 'w,n,s'.split(','))
            else:                       open_door = populate_door(idx, jdx, 'e,w,n,s'.split(','))

            if not open_door:
                self.grid_map[idx][jdx] = EmptyShape()

        def populate_corridor(idx, jdx):
            if full_row(idx) and jdx%2 != 0:
                self.grid_map[idx][jdx] = EmptyShape() # EmptyShape to first horizontal corridor (does not exist)
                return

            high_asset = len(ENV_CORRIDOR_ASSET_LIST) - 1
            if side_north(idx) or side_south(idx) or side_west(jdx) or side_east(jdx): high_asset = 6

            corridordx = np.random.randint(low=-1, high=high_asset + 1, size=1)[0]
            if corridordx == -1:
                self.grid_map[idx][jdx] = EmptyShape()
                return

            parameters = ENV_CORRIDOR_ASSET_LIST[corridordx][1].split(',')

            asset, doors = parameters[0], parameters[2:]
            corridor = CorridorShape(asset, doors)
            rotate_border_regions(asset, corridor, idx, jdx)

            for param in corridor.doors:  corridor.door(param)
            self.grid_map[idx][jdx] = corridor

        for idx in range(0, N_ROW, 2):
            for jdx in range(1, N_COLUMN, 2):
                    populate_corridor(idx, jdx)

        for idx in range(1, N_ROW, 2):
            for jdx in range(0, N_COLUMN, 1):
                    populate_corridor(idx, jdx)

        self.grid_map[-1][:] = [EmptyShape() for _ in range(N_COLUMN)]
        for grid_row in self.grid_map:           
            grid_row[-1] = EmptyShape()

        for idx in range(0, N_ROW, 2):
            for jdx in range(0, N_COLUMN, 2):
                    populate_room(idx, jdx)               

    def dijkstra_grid(self, visitation):

        def compare_grid_path(idx, jdx, values, soft_check=False):
            
            def check_visited(directions):
                is_visited = True
                
                for direction in directions:
                    if   direction == "e":      is_visited = is_visited and (visitation[idx][jdx+1] >= values.get("e") if values.get("e") != 0 or soft_check else visitation[idx][jdx+1] == values.get("e"))
                    elif direction == "n":      is_visited = is_visited and (visitation[idx-1][jdx] >= values.get("n") if values.get("n") != 0 or soft_check else visitation[idx-1][jdx] == values.get("n"))
                    elif direction == "s":      is_visited = is_visited and (visitation[idx+1][jdx] >= values.get("s") if values.get("s") != 0 or soft_check else visitation[idx+1][jdx] == values.get("s"))
                    elif direction == "w":      is_visited = is_visited and (visitation[idx][jdx-1] >= values.get("w") if values.get("w") != 0 or soft_check else visitation[idx][jdx-1] == values.get("w"))

                return is_visited

            if side_north(idx):
                if   side_west(jdx):    return check_visited("e,s".split(','))      and values.get("n") == 0 and values.get("w") == 0
                elif side_east(jdx):    return check_visited("s,w".split(','))      and values.get("n") == 0 and values.get("e") == 0
                else:                   return check_visited("e,s,w".split(','))    and values.get("n") == 0
            
            elif idx == N_ROW - 1:
                if   side_west(jdx):    return check_visited("e,n".split(','))      and values.get("w") == 0 and values.get("s") == 0
                elif side_east(jdx):    return check_visited("n,w".split(','))      and values.get("e") == 0 and values.get("s") == 0
                else:                   return check_visited("e,n,w".split(','))    and values.get("s") == 0
            
            elif     side_west(jdx):    return check_visited("e,n,s".split(','))    and values.get("w") == 0
            elif     side_east(jdx):    return check_visited("n,s,w".split(','))    and values.get("e") == 0
            else:                       return check_visited("e,n,s,w".split(','))

        def populate_corridor(idx, jdx, parameters, angle=0, all_doors=None):
            asset, doors = parameters[0], parameters[2:]
            corridor = CorridorShape(asset, doors)

            if angle != 0:                  corridor.rotate(angle)
            if all_doors == None:           all_doors = corridor.doors

            for doordx in all_doors:        
                corridor.door(doordx); 
                if doordx not in corridor.doors:   corridor.doors.append(doordx)

            self.grid_map[idx][jdx] = corridor

        for idx in range(visitation.__len__()):
            for jdx in range(visitation.__len__()):
                if visitation[idx][jdx] == 0:         self.grid_map[idx][jdx] = EmptyShape()
                elif visitation[idx][jdx] == 1000:   
                    self.grid_map[idx][jdx] = RoomShape() 
                    if compare_grid_path(idx, jdx, {"n": 1, "s": 0, "w": 0, "e": 0}, soft_check=True):  self.grid_map[idx][jdx].door("n")
                    if compare_grid_path(idx, jdx, {"n": 0, "s": 1, "w": 0, "e": 0}, soft_check=True):  self.grid_map[idx][jdx].door("s")
                    if compare_grid_path(idx, jdx, {"n": 0, "s": 0, "w": 1, "e": 0}, soft_check=True):  self.grid_map[idx][jdx].door("w")
                    if compare_grid_path(idx, jdx, {"n": 0, "s": 0, "w": 0, "e": 1}, soft_check=True):  self.grid_map[idx][jdx].door("e")
                    
                else:
                    # Straight corridor
                    if   compare_grid_path(idx, jdx, {"n": 0, "s": 0, "w": 1, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[1][1].split(','))
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 1, "w": 0, "e": 0}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[1][1].split(','), 
                                                                                                                    angle=90,  all_doors="n,s".split(','))
                    # Corner corridor
                    elif compare_grid_path(idx, jdx, {"n": 0, "s": 1, "w": 0, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[3][1].split(','))

                    elif compare_grid_path(idx, jdx, {"n": 0, "s": 1, "w": 1, "e": 0}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[3][1].split(','), 
                                                                                                                    angle=90,  all_doors="s,w".split(','))
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 0, "w": 1, "e": 0}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[3][1].split(','), 
                                                                                                                    angle=180, all_doors="n,w".split(','))
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 0, "w": 0, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[3][1].split(','), 
                                                                                                                    angle=270, all_doors="e,n".split(','))
                    # Triangle corridor
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 1, "w": 0, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[6][1].split(','))
                    elif compare_grid_path(idx, jdx, {"n": 0, "s": 1, "w": 1, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[6][1].split(','), 
                                                                                                                    angle=90,  all_doors="e,s,w".split(','))
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 1, "w": 1, "e": 0}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[6][1].split(','), 
                                                                                                                    angle=180, all_doors="n,s,w".split(','))
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 0, "w": 1, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[6][1].split(','), 
                                                                                                                    angle=270, all_doors="e,n,w".split(','))
                    # Crossing corridor
                    elif compare_grid_path(idx, jdx, {"n": 1, "s": 1, "w": 1, "e": 1}):     populate_corridor(idx, jdx, ENV_CORRIDOR_ASSET_LIST[-1][1].split(','))

                    else:   
                        raise ValueError("Invalid corridor configuration at idx: {}, jdx: {} in visitation \n{}".format(idx, jdx, visitation.astype(np.uint8)))
                    
    def __str__(self):
        str_format = "\n\n"
        for idx in range(N_ROW):
            str_grid = [""] * 6
            n_empty = 0
            for jdx in range(N_COLUMN):
                if empty_shape(self.grid_map[idx][jdx]): n_empty += 1
                for gridx, grid_element in enumerate(self.grid_map[idx][jdx].get_shape().split("\n")[:-1], start=0):  
                    str_grid[gridx] += grid_element

            if n_empty == N_COLUMN:  continue
            for gridx in range(6): # New line
                str_format += str_grid[gridx] + "\n"
                
        str_format += "\n"
        return str_format
