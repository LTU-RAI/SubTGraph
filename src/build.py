import os, bpy, yaml, random, string

from utils import *
from graph.shape import *

###

class FactoryObj():
    def __init__(self):
        self.imported_objects = []

        with open('../config/dimensions-type-a.yaml', 'r') as file:
            self.dimensions_type_a = yaml.safe_load(file)

        with open('../config/dimensions-type-b.yaml', 'r') as file:
            self.dimensions_type_b = yaml.safe_load(file)


    # **************************************************************************************************************
    # Asset Handling

    def get_asset_info(self, graph, idx, jdx):
        openings = graph[idx][jdx].openings;  asset = graph[idx][jdx].r_asset
        asset += '_0' + str(4 - openings.__len__() if openings.__len__() > 0  else 4)

        if 4 - openings.__len__() == 1:
            if   not isOpenNorth(openings):                                               angle = '000'
            elif not isOpenEast(openings):                                                angle = '090'
            elif not isOpenSouth(openings):                                               angle = '180'
            elif not isOpenWest(openings):                                                angle = '270'

        elif openings.__len__() == 2:
            if   not (isOpenEast(openings)  or isOpenWest(openings)):                          angle = 'straight_000'
            elif not (isOpenNorth(openings) or isOpenSouth(openings)):                         angle = 'straight_090'

            elif not (isOpenNorth(openings) or isOpenEast(openings)):                          angle = 'corner_000'
            elif not (isOpenEast(openings) or isOpenSouth(openings)):                          angle = 'corner_090'
            elif not (isOpenSouth(openings) or isOpenWest(openings)):                          angle = 'corner_180'
            elif not (isOpenWest(openings) or isOpenNorth(openings)):                          angle = 'corner_270'

        elif 4 - openings.__len__() == 3:
            if   not (isOpenNorth(openings) or isOpenWest(openings) or isOpenEast(openings)):     angle = '000'
            elif not (isOpenNorth(openings) or isOpenEast(openings) or isOpenSouth(openings)):    angle = '090'
            elif not (isOpenSouth(openings) or isOpenWest(openings) or isOpenEast(openings)):     angle = '180'
            elif not (isOpenNorth(openings) or isOpenWest(openings) or isOpenSouth(openings)):    angle = '270'

        else:                                                                         angle = '000'

        return openings, asset, angle

    def get_asset_idx_jdx(self, graph, idx, jdx, base_offseth, base_offsetv, originDir):
        connections, asset, angle = self.get_asset_info(graph, idx, jdx)
        obj_path = os.path.join(topology['asset_path'], asset, asset + '_' + angle + '.obj')

        if asset in ['room_03', 'room_04']: raise Exception('Not implemented')  # TODO Implement

        try:    bpy.ops.wm.obj_import(filepath=obj_path)  # Import .obj mesh of asset
        except: print("Error importing object: " + obj_path);  return

        imported = bpy.context.selected_objects  # Apply rotation and offset
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        for obj in imported:
            obj.location.x += base_offseth
            obj.location.y += base_offsetv

            self.imported_objects.append(obj)

        # Update horizontal and vertcal offsets
        offseth = self.dimensions_type_a[asset + '_' + angle]['pos'][0]
        offsetv = self.dimensions_type_a[asset + '_' + angle]['pos'][1]

        if originDir != None and originDir not in graph[idx][jdx].connections:  graph[idx][jdx].connections.append(originDir)

        diff = list(set(['n', 's', 'e', 'w']) - set(connections))
        for connection in list(diff):
            if connection == 'n':
                if connection not in connections:  graph[idx][jdx].connections.append(connection)
                if graph[idx - 1][jdx].connections.__len__() == 0: continue

                _, asset, angle = self.get_connection_info(graph, idx - 1, jdx)
                dest_offsetv = self.dimensions_type_a[asset + '_' + angle]['pos'][1]
                self.get_connection_idx_jdx(graph, idx - 1, jdx, base_offseth, base_offsetv - offsetv - dest_offsetv, 's')
            elif connection == 's':
                if connection not in connections:  graph[idx][jdx].connections.append(connection)
                if graph[idx + 1][jdx].connections.__len__() == 0: continue

                _, asset, angle = self.get_connection_info(graph, idx + 1, jdx)
                dest_offsetv = self.dimensions_type_a[asset + '_' + angle]['pos'][1]
                self.get_connection_idx_jdx(graph, idx + 1, jdx, base_offseth, base_offsetv + offsetv + dest_offsetv, 'n')
            elif connection == 'e':
                if connection not in connections:  graph[idx][jdx].connections.append(connection)
                if graph[idx][jdx + 1].connections.__len__() == 0: continue

                _, asset, angle = self.get_connection_info(graph, idx, jdx + 1)
                dest_offseth = self.dimensions_type_a[asset + '_' + angle]['pos'][0]
                self.get_connection_idx_jdx(graph, idx, jdx + 1, base_offseth + offseth + dest_offseth, base_offsetv, 'w')
            elif connection == 'w':
                if connection not in connections:  graph[idx][jdx].connections.append(connection)
                if graph[idx][jdx - 1].connections.__len__() == 0: continue

                _, asset, angle = self.get_connection_info(graph, idx, jdx - 1)
                dest_offseth = self.dimensions_type_a[asset + '_' + angle]['pos'][0]
                self.get_connection_idx_jdx(graph, idx, jdx - 1, base_offseth - offseth - dest_offseth, base_offsetv, 'e')


    # **************************************************************************************************************
    # Connection Handling

    def get_connection_info(self, graph, idx, jdx):
        connections = graph[idx][jdx].connections; angle = graph[idx][jdx].c_angle; asset = graph[idx][jdx].c_asset

        if   angle ==   0:  angle = '000'
        elif angle ==  90:  angle = '090'
        elif angle == 180:  angle = '180'
        elif angle == 270:  angle = '270'

        return connections, asset, angle

    def get_connection_idx_jdx(self, graph, idx, jdx, base_offseth, base_offsetv, origin):
        connections, asset, angle = self.get_connection_info(graph, idx, jdx)
        obj_path = os.path.join(topology['asset_path'], asset, asset + '_' + angle + '.obj')

        if '04' in asset: raise Exception('Intersection not implemented')
        
        try:    bpy.ops.wm.obj_import(filepath=obj_path)
        except: print("Error importing object: " + obj_path);  return

        imported = bpy.context.selected_objects
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        for obj in imported:
            obj.location.x += base_offseth
            obj.location.y += base_offsetv
            
            self.imported_objects.append(obj)

        offseth = self.dimensions_type_a[asset + '_' + angle]['pos'][0]
        offsetv = self.dimensions_type_a[asset + '_' + angle]['pos'][1]

        if origin != None and origin in graph[idx][jdx].connections:  graph[idx][jdx].connections.remove(origin)

        for connection in list(connections):
            if connection == origin:  continue
            if connection == 'n':
                if connection in graph[idx][jdx].connections:  graph[idx][jdx].connections.remove(connection)

                if isinstance(graph[idx - 1][jdx], NodeShape):           
                    if graph[idx - 1][jdx].connections.__len__() == 4: continue
                    function_info = self.get_asset_info;     function_asset = self.get_asset_idx_jdx
                elif isinstance(graph[idx - 1][jdx], ConnectionShape):     
                    if graph[idx - 1][jdx].connections.__len__() == 0: continue
                    function_info = self.get_connection_info; function_asset = self.get_connection_idx_jdx
                
                _, asset, angle = function_info(graph, idx - 1, jdx)
                dest_offsetv = self.dimensions_type_a[asset + '_' + angle]['pos'][1]
                function_asset(graph, idx - 1, jdx, base_offseth, base_offsetv - offsetv - dest_offsetv, 's')

            elif connection == 's':
                if connection in graph[idx][jdx].connections:  graph[idx][jdx].connections.remove(connection)

                if isinstance(graph[idx + 1][jdx], NodeShape):           
                    if graph[idx + 1][jdx].connections.__len__() == 4: continue
                    function_info = self.get_asset_info;     function_asset = self.get_asset_idx_jdx
                elif isinstance(graph[idx + 1][jdx], ConnectionShape):     
                    if graph[idx + 1][jdx].connections.__len__() == 0: continue
                    function_info = self.get_connection_info; function_asset = self.get_connection_idx_jdx            

                _, asset, angle = function_info(graph, idx + 1, jdx)
                dest_offsetv = self.dimensions_type_a[asset + '_' + angle]['pos'][1]
                function_asset(graph, idx + 1, jdx, base_offseth, base_offsetv + offsetv + dest_offsetv, 'n')

            elif connection == 'e':
                if connection in graph[idx][jdx].connections:  graph[idx][jdx].connections.remove(connection)

                if isinstance(graph[idx][jdx + 1], NodeShape):           
                    function_info = self.get_asset_info;     function_asset = self.get_asset_idx_jdx
                    if graph[idx][jdx + 1].connections.__len__() == 4: continue
                elif isinstance(graph[idx][jdx + 1], ConnectionShape):     
                    function_info = self.get_connection_info; function_asset = self.get_connection_idx_jdx
                    if graph[idx][jdx + 1].connections.__len__() == 0: continue
                
                _, asset, angle = function_info(graph, idx, jdx + 1)
                dest_offseth = self.dimensions_type_a[asset + '_' + angle]['pos'][0]
                function_asset(graph, idx, jdx + 1, base_offseth + offseth + dest_offseth, base_offsetv, 'w')

            elif connection == 'w':
                if   isinstance(graph[idx][jdx - 1], NodeShape):       
                    if graph[idx][jdx - 1].connections.__len__() == 4: continue  
                    function_info = self.get_asset_info;      function_asset = self.get_asset_idx_jdx
                elif isinstance(graph[idx][jdx - 1], ConnectionShape):     
                    if graph[idx][jdx - 1].connections.__len__() == 0: continue
                    function_info = self.get_connection_info;  function_asset = self.get_connection_idx_jdx

                if connection in graph[idx][jdx].connections:  graph[idx][jdx].connections.remove(connection)

                _, asset, angle = function_info(graph, idx, jdx - 1)
                dest_offseth = self.dimensions_type_a[asset + '_' + angle]['pos'][0]
                function_asset(graph, idx, jdx - 1, base_offseth - offseth - dest_offseth, base_offsetv, 'e')


    # **************************************************************************************************************
    # World Creation

    def world(self, graph):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        selected = False
        for idx in range(0, grid_rows):  # Find initial tile
            for jdx in range(0, grid_columns):
                if isEmptyShape(graph[idx][jdx]): continue
                elif isinstance(graph[idx][jdx], NodeShape):
                    self.get_asset_idx_jdx(graph, idx, jdx, 0, 0, None);      selected = True; break  # Only once, then recursively
                elif isinstance(graph[idx][jdx], ConnectionShape):
                    self.get_connection_idx_jdx(graph, idx, jdx, 0, 0, None); selected = True; break  # Only once, then recursively

            if selected: break

        # Join all imported objects into one
        for obj in self.imported_objects:
            obj.select_set(True)

        bpy.context.view_layer.objects.active = self.imported_objects[0]  # Set active for join
        bpy.ops.object.join()

        merged_obj = bpy.context.active_object
        merged_obj.name = self.get_random_id()  # Rename the merged object
