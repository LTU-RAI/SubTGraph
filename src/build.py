import bpy, yaml, random, string

from shape import *

###

class FactoryObj():
    def __init__(self):
        pass

    def get_random_id(self):
        return ''.join(random.choice(string.ascii_letters) for i in range(32))

    def get_room_info(self, grid, idx, jdx):
        doors = grid[idx][jdx].doors;  asset = grid[idx][jdx].r_asset
        asset += '_0' + str(4 - doors.__len__() if doors.__len__() > 0  else 4)

        if 4 - doors.__len__() == 1:
            if   not door_north(doors):                                               angle = '000'
            elif not door_east(doors):                                                angle = '090'
            elif not door_south(doors):                                               angle = '180'
            elif not door_west(doors):                                                angle = '270'

        elif doors.__len__() == 2:
            if   not (door_east(doors)  or door_west(doors)):                          angle = 'straight_000'
            elif not (door_north(doors) or door_south(doors)):                         angle = 'straight_090'

            elif not (door_north(doors) or door_east(doors)):                          angle = 'corner_000'
            elif not (door_east(doors) or door_south(doors)):                          angle = 'corner_090'
            elif not (door_south(doors) or door_west(doors)):                          angle = 'corner_180'
            elif not (door_west(doors) or door_north(doors)):                          angle = 'corner_270'

        elif 4 - doors.__len__() == 3:
            if   not (door_north(doors) or door_west(doors) or door_east(doors)):     angle = '000'
            elif not (door_north(doors) or door_east(doors) or door_south(doors)):    angle = '090'
            elif not (door_south(doors) or door_west(doors) or door_east(doors)):     angle = '180'
            elif not (door_north(doors) or door_west(doors) or door_south(doors)):    angle = '270'

        else:                                                                         angle = '000'

        return doors, asset, angle

    def get_room_idx_jdx(self, grid, idx, jdx, base_offseth, base_offsetv, origin):
        doors, asset, angle = self.get_room_info(grid, idx, jdx)
        obj_path = ASSET_PATH + asset + '/' + asset + '_' + angle + '.obj'

        if asset in ['room_03', 'room_04']: raise Exception('Not implemented')

        try:    bpy.ops.wm.obj_import(filepath=obj_path)
        except: print("Error importing object: " + obj_path);  return

        imported = bpy.context.selected_objects
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        for obj in imported:
            obj.location.x += base_offseth
            obj.location.y += base_offsetv

            imported_objects.append(obj)

        offseth = dimensions[asset + '_' + angle]['pos'][0]
        offsetv = dimensions[asset + '_' + angle]['pos'][1]

        if origin != None and origin not in grid[idx][jdx].doors:  grid[idx][jdx].doors.append(origin)

        difference = list(set(['n', 's', 'e', 'w']) - set(doors))
        print('room', difference)
        for door in list(difference):
            print(door, 'before')
            if door == origin:  print(door, 'origin'); continue
            if door == 'n':
                if door not in doors:  grid[idx][jdx].doors.append(door)
                if grid[idx - 1][jdx].doors.__len__() == 0: continue

                _, asset, angle = self.get_corridor_info(grid, idx - 1, jdx)
                dest_offsetv = dimensions[asset + '_' + angle]['pos'][1]
                self.get_corridor_idx_jdx(grid, idx - 1, jdx, base_offseth, base_offsetv - offsetv - dest_offsetv, 's')
            elif door == 's':
                if door not in doors:  grid[idx][jdx].doors.append(door)
                if grid[idx + 1][jdx].doors.__len__() == 0: continue

                _, asset, angle = self.get_corridor_info(grid, idx + 1, jdx)
                dest_offsetv = dimensions[asset + '_' + angle]['pos'][1]
                self.get_corridor_idx_jdx(grid, idx + 1, jdx, base_offseth, base_offsetv + offsetv + dest_offsetv, 'n')
            elif door == 'e':
                if door not in doors:  grid[idx][jdx].doors.append(door)
                if grid[idx][jdx + 1].doors.__len__() == 0: continue

                _, asset, angle = self.get_corridor_info(grid, idx, jdx + 1)
                dest_offseth = dimensions[asset + '_' + angle]['pos'][0]
                self.get_corridor_idx_jdx(grid, idx, jdx + 1, base_offseth + offseth + dest_offseth, base_offsetv, 'w')
            elif door == 'w':
                if door not in doors:  grid[idx][jdx].doors.append(door)
                if grid[idx][jdx - 1].doors.__len__() == 0: continue

                _, asset, angle = self.get_corridor_info(grid, idx, jdx - 1)
                dest_offseth = dimensions[asset + '_' + angle]['pos'][0]
                self.get_corridor_idx_jdx(grid, idx, jdx - 1, base_offseth - offseth - dest_offseth, base_offsetv, 'e')

        print('this is the end for room')

    def get_corridor_info(self, grid, idx, jdx):
        doors = grid[idx][jdx].doors; angle = grid[idx][jdx].c_angle; asset = grid[idx][jdx].c_asset

        if   angle ==   0:  angle = '000'
        elif angle ==  90:  angle = '090'
        elif angle == 180:  angle = '180'
        elif angle == 270:  angle = '270'

        return doors, asset, angle

    def get_corridor_idx_jdx(self, grid, idx, jdx, base_offseth, base_offsetv, origin):
        doors, asset, angle = self.get_corridor_info(grid, idx, jdx)
        obj_path = ASSET_PATH + asset + '/' + asset + '_' + angle + '.obj'

        if '04' in asset: raise Exception('Intersection not implemented')
        
        try:    bpy.ops.wm.obj_import(filepath=obj_path)
        except: print("Error importing object: " + obj_path);  return

        imported = bpy.context.selected_objects
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        for obj in imported:
            obj.location.x += base_offseth
            obj.location.y += base_offsetv
            
            imported_objects.append(obj)

        offseth = dimensions[asset + '_' + angle]['pos'][0]
        offsetv = dimensions[asset + '_' + angle]['pos'][1]

        if origin != None and origin in grid[idx][jdx].doors:  grid[idx][jdx].doors.remove(origin)

        for door in list(doors):
            if door == origin:  continue
            if door == 'n':
                if door in grid[idx][jdx].doors:  grid[idx][jdx].doors.remove(door)

                if isinstance(grid[idx - 1][jdx], RoomShape):           
                    if grid[idx - 1][jdx].doors.__len__() == 4: continue
                    function_info = self.get_room_info;     function_asset = self.get_room_idx_jdx
                elif isinstance(grid[idx - 1][jdx], CorridorShape):     
                    if grid[idx - 1][jdx].doors.__len__() == 0: continue
                    function_info = self.get_corridor_info; function_asset = self.get_corridor_idx_jdx
                
                _, asset, angle = function_info(grid, idx - 1, jdx)
                dest_offsetv = dimensions[asset + '_' + angle]['pos'][1]
                function_asset(grid, idx - 1, jdx, base_offseth, base_offsetv - offsetv - dest_offsetv, 's')

            elif door == 's':
                if door in grid[idx][jdx].doors:  grid[idx][jdx].doors.remove(door)

                if isinstance(grid[idx + 1][jdx], RoomShape):           
                    if grid[idx + 1][jdx].doors.__len__() == 4: continue
                    function_info = self.get_room_info;     function_asset = self.get_room_idx_jdx
                elif isinstance(grid[idx + 1][jdx], CorridorShape):     
                    if grid[idx + 1][jdx].doors.__len__() == 0: continue
                    function_info = self.get_corridor_info; function_asset = self.get_corridor_idx_jdx            

                _, asset, angle = function_info(grid, idx + 1, jdx)
                dest_offsetv = dimensions[asset + '_' + angle]['pos'][1]
                function_asset(grid, idx + 1, jdx, base_offseth, base_offsetv + offsetv + dest_offsetv, 'n')

            elif door == 'e':
                if door in grid[idx][jdx].doors:  grid[idx][jdx].doors.remove(door)

                if isinstance(grid[idx][jdx + 1], RoomShape):           
                    function_info = self.get_room_info;     function_asset = self.get_room_idx_jdx
                    if grid[idx][jdx + 1].doors.__len__() == 4: continue
                elif isinstance(grid[idx][jdx + 1], CorridorShape):     
                    function_info = self.get_corridor_info; function_asset = self.get_corridor_idx_jdx
                    if grid[idx][jdx + 1].doors.__len__() == 0: continue
                
                _, asset, angle = function_info(grid, idx, jdx + 1)
                dest_offseth = dimensions[asset + '_' + angle]['pos'][0]
                function_asset(grid, idx, jdx + 1, base_offseth + offseth + dest_offseth, base_offsetv, 'w')

            elif door == 'w':
                if   isinstance(grid[idx][jdx - 1], RoomShape):       
                    if grid[idx][jdx - 1].doors.__len__() == 4: continue  
                    function_info = self.get_room_info;      function_asset = self.get_room_idx_jdx
                elif isinstance(grid[idx][jdx - 1], CorridorShape):     
                    if grid[idx][jdx - 1].doors.__len__() == 0: continue
                    function_info = self.get_corridor_info;  function_asset = self.get_corridor_idx_jdx

                if door in grid[idx][jdx].doors:  grid[idx][jdx].doors.remove(door)

                _, asset, angle = function_info(grid, idx, jdx - 1)
                dest_offseth = dimensions[asset + '_' + angle]['pos'][0]
                function_asset(grid, idx, jdx - 1, base_offseth - offseth - dest_offseth, base_offsetv, 'e')


    def grid(self, grid):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        global dimensions
        with open(DARPA_DIMENSIONS, 'r') as file:
            dimensions = yaml.safe_load(file)

        global imported_objects
        imported_objects = []; selected = False
        for idx in range(0, N_ROW):  # Find initial tile
            for jdx in range(0, N_COLUMN):
                if empty_shape(grid[idx][jdx]): continue
                elif isinstance(grid[idx][jdx], RoomShape):
                    self.get_room_idx_jdx(grid, idx, jdx, 0, 0, None); selected = True; break      # Only once, then recursively
                elif isinstance(grid[idx][jdx], CorridorShape):
                    self.get_corridor_idx_jdx(grid, idx, jdx, 0, 0, None); selected = True; break  # Only once, then recursively

            if selected: break

        # Join all imported objects into one
        for obj in imported_objects:
            obj.select_set(True)

        bpy.context.view_layer.objects.active = imported_objects[0]  # Set active for join
        bpy.ops.object.join()

        merged_obj = bpy.context.active_object
        merged_obj.name = self.get_random_id()  # Rename the merged object
