import os, bpy, yaml, random, string

from utils import *
from graph.shape import *

###

class FactoryObj():
    def __init__(self):
        self.imported_objects = []

        self.base_offsetz = 0.0  # Default base offset for z-axis
        self.shaftOffsetx, self.shaftOffsety, self.shaftOffsetz = 0.0, 0.0, 0.0  # Default shaft offsets

        with open('../config/dimensions-type-a.yaml', 'r') as file:
            self.dimensions_type_a = yaml.safe_load(file)
        with open('../config/dimensions-type-b.yaml', 'r') as file:
            self.dimensions_type_b = yaml.safe_load(file)

    def get_dimensions(self, dim_type):
        if   'type_a' in dim_type:  return self.dimensions_type_a
        elif 'type_b' in dim_type:  return self.dimensions_type_b
        else:                       raise ValueError("Invalid dimensions type specified: {}".format(type))

    def get_material(self, material_name, material_path):
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True  # Enable node-based materials

        # Create an image texture node
        nodes = material.node_tree.nodes
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.image = bpy.data.images.load(material_path)  # Path to your image file

        # Connect the texture node to the Principled BSDF shader
        principled_shader = nodes.get("Principled BSDF")
        material.node_tree.links.new(texture_node.outputs["Color"], principled_shader.inputs["Base Color"])

        return material

    # **************************************************************************************************************
    # Asset Handling

    def get_node_info(self, graph, idx, jdx):
        openings = graph[idx][jdx].openings

        if 4 - openings.__len__() == 1:
            if   not isOpenNorth(openings):                                                         angle = 180
            elif not isOpenEast(openings):                                                          angle = 270
            elif not isOpenSouth(openings):                                                         angle = 0
            elif not isOpenWest(openings):                                                          angle = 90

        elif openings.__len__() == 2:
            if   not (isOpenEast(openings)  or isOpenWest(openings)):                               angle = 0
            elif not (isOpenNorth(openings) or isOpenSouth(openings)):                              angle = 90

            elif not (isOpenNorth(openings) or isOpenEast(openings)):                               angle = 270
            elif not (isOpenEast(openings) or isOpenSouth(openings)):                               angle = 0
            elif not (isOpenSouth(openings) or isOpenWest(openings)):                               angle = 90
            elif not (isOpenWest(openings) or isOpenNorth(openings)):                               angle = 180

        elif 4 - openings.__len__() == 3:
            if   not (isOpenNorth(openings) or isOpenWest(openings) or isOpenEast(openings)):       angle = 270
            elif not (isOpenNorth(openings) or isOpenEast(openings) or isOpenSouth(openings)):      angle = 0
            elif not (isOpenSouth(openings) or isOpenWest(openings) or isOpenEast(openings)):       angle = 90
            elif not (isOpenNorth(openings) or isOpenWest(openings) or isOpenSouth(openings)):      angle = 180

        else:                                                                                       angle = 0

        return openings, graph[idx][jdx].connection_type, angle

    def get_node_idx_jdx(self, graph, idx, jdx, base_offsetx, base_offsety, originDir):
        openings, connection_type, angle = self.get_node_info(graph, idx, jdx)
        asset_type = topology['env_asset_list_type_b'][connection_type.split("_")[0]]["assets"][np.random.randint(0, len(topology['env_asset_list_type_b'][connection_type.split("_")[0]]["assets"]))]
        dimensions = self.get_dimensions(asset_type)

        if connection_type != "shaft_aux":
            obj_path = os.path.join(topology['asset_path'], dimensions["folder"].replace('_', ' '), asset_type.replace('_', ' '), dimensions[asset_type]['name'] + '.obj')

            try:    bpy.ops.wm.obj_import(filepath=obj_path)  # Import .obj asset of asset
            except: print("Error importing object: " + obj_path);  return

            imported = bpy.context.selected_objects  # Apply rotation and offset
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            for obj in imported:
                obj.location.x += base_offsetx
                obj.location.y += base_offsety
                obj.location.z = self.base_offsetz

                obj.rotation_euler = (0, 0, math.radians(angle))
                bpy.ops.object.transform_apply(rotation=True)

                self.imported_objects.append(obj)

        # Update horizontal and vertical offsets
        offsetx = dimensions[asset_type]['pos'][0]
        offsety = dimensions[asset_type]['pos'][1]
        offsetz = dimensions[asset_type]['pos'][2]

        if originDir != None and originDir not in graph[idx][jdx].openings:  graph[idx][jdx].openings.append(originDir)

        def recursiveConnection(connection, idx, jdx, dst_idx, dst_jdx, new_offsetx, new_offsety, dst_connection):
            if connection not in openings:  graph[idx][jdx].openings.append(connection)
            if graph[dst_idx][dst_jdx].openings.__len__() == 0: return

            _, connection_type, _ = self.get_connection_info(graph, dst_idx, dst_jdx)
            asset_type = topology['env_asset_list_type_b'][connection_type]["assets"][np.random.randint(0, len(topology['env_asset_list_type_b'][connection_type]["assets"]))]

            dimensions = self.get_dimensions(asset_type)
            if connection == 'n': new_offsety -= dimensions[asset_type]['pos'][1]
            if connection == 's': new_offsety += dimensions[asset_type]['pos'][1]	
            if connection == 'e': new_offsetx += dimensions[asset_type]['pos'][0]
            if connection == 'w': new_offsetx -= dimensions[asset_type]['pos'][0]

            self.get_connection_idx_jdx(graph, dst_idx, dst_jdx, new_offsetx, new_offsety, dst_connection)

        diff = list(set(['n', 's', 'e', 'w']) - set(openings))
        if diff.__len__() <= 1 and connection_type != "shaft" and connection_type != "shaft_aux":  # Add cave cap if no openings left
            asset_type = "cave_cap_type_b" if asset_type.split('_')[-1] == 'b' else "cave_cap_type_a"
            dimensions = self.get_dimensions(asset_type)
            obj_path = os.path.join(topology['asset_path'], dimensions["folder"].replace('_', ' '), asset_type.replace('_', ' '), dimensions[asset_type]['name'] + '.obj')
            
            if angle == 0:  # North Cap
                new_offsetx = base_offsetx + offsetx + dimensions[asset_type]['pos'][0]
                new_offsety = base_offsety
            if angle == 180: # South Cap
                new_offsetx = base_offsetx - offsetx - dimensions[asset_type]['pos'][0]
                new_offsety = base_offsety
            if angle == 90:  # East Cap
                new_offsetx = base_offsetx
                new_offsety = base_offsety + offsety + dimensions[asset_type]['pos'][1]	
            if angle == 270:  # West Cap
                new_offsetx = base_offsetx
                new_offsety = base_offsety - offsety - dimensions[asset_type]['pos'][1]

            try:    bpy.ops.wm.obj_import(filepath=obj_path)  # Import .obj asset of asset
            except: print("Error importing object: " + obj_path);  return

            imported = bpy.context.selected_objects  # Apply rotation and offset
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            for obj in imported:
                obj.location.x += new_offsetx
                obj.location.y += new_offsety
                obj.location.z = self.base_offsetz

                obj.rotation_euler = (0, 0, math.radians(angle + 90))
                bpy.ops.object.transform_apply(rotation=True)

                self.imported_objects.append(obj)

        for connection in diff:
            if   connection == 'n':  
                if connection_type.split('_')[0] == "shaft": 
                    self.shaftOffsetx = base_offsetx
                    self.shaftOffsety = base_offsety - offsety
                    self.shaftOffsetz = offsetz
                recursiveConnection(connection, idx, jdx, idx - 1, jdx,     base_offsetx,           base_offsety - offsety, 's')
            elif connection == 's':  
                if connection_type.split('_')[0] == "shaft": 
                    self.shaftOffsetx = base_offsetx
                    self.shaftOffsety = base_offsety + offsety
                    self.shaftOffsetz = offsetz
                recursiveConnection(connection, idx, jdx, idx + 1, jdx,     base_offsetx,           base_offsety + offsety, 'n')
            elif connection == 'e':  
                if connection_type.split('_')[0] == "shaft": 
                    self.shaftOffsetx = base_offsetx + offsetx
                    self.shaftOffsety = base_offsety
                    self.shaftOffsetz = offsetz
                recursiveConnection(connection, idx, jdx, idx,     jdx + 1, base_offsetx + offsetx, base_offsety,           'w')
            elif connection == 'w':  
                if connection_type.split('_')[0] == "shaft": 
                    self.shaftOffsetx = base_offsetx - offsetx
                    self.shaftOffsety = base_offsety
                    self.shaftOffsetz = offsetz
                recursiveConnection(connection, idx, jdx, idx,     jdx - 1, base_offsetx - offsetx, base_offsety,           'e')
    
    # **************************************************************************************************************
    # Connection Handling

    def get_connection_info(self, graph, idx, jdx):
        return graph[idx][jdx].openings, graph[idx][jdx].connection_type, graph[idx][jdx].angle

    def get_connection_idx_jdx(self, graph, idx, jdx, base_offsetx, base_offsety, origin):
        openings, connection_type, angle = self.get_connection_info(graph, idx, jdx)
        asset_type = topology['env_asset_list_type_b'][connection_type]["assets"][np.random.randint(0, len(topology['env_asset_list_type_b'][connection_type]["assets"]))]
        dimensions = self.get_dimensions(asset_type)
        obj_path = os.path.join(topology['asset_path'], dimensions["folder"].replace('_', ' '), asset_type.replace('_', ' '), dimensions[asset_type]['name'] + '.obj')

        try:    bpy.ops.wm.obj_import(filepath=obj_path)
        except: print("Error importing object: " + obj_path);  return

        imported = bpy.context.selected_objects
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        for obj in imported:
            obj.location.x += base_offsetx
            obj.location.y += base_offsety
            obj.location.z = self.base_offsetz
            
            obj.rotation_euler = (0, 0, math.radians(angle))
            bpy.ops.object.transform_apply(rotation=True)

            self.imported_objects.append(obj)

        offseth = dimensions[asset_type]['pos'][0]
        offsetv = dimensions[asset_type]['pos'][1]

        if origin != None and origin in graph[idx][jdx].openings:  graph[idx][jdx].openings.remove(origin)

        def recursiveConnection(connection, idx, jdx, dst_idx, dst_jdx, new_offseth, new_offsetv, dst_connection):
            if connection in graph[idx][jdx].openings:  graph[idx][jdx].openings.remove(connection)
            
            if isinstance(graph[dst_idx][dst_jdx], NodeShape):           
                if graph[dst_idx][dst_jdx].openings.__len__() == 4: return
                function_info = self.get_node_info;     function_asset = self.get_node_idx_jdx

            elif isinstance(graph[dst_idx][dst_jdx], ConnectionShape):     
                if graph[dst_idx][dst_jdx].openings.__len__() == 0: return
                function_info = self.get_connection_info; function_asset = self.get_connection_idx_jdx
            
            _, connection_type, _ = function_info(graph, dst_idx, dst_jdx)
            asset_type = topology['env_asset_list_type_b'][connection_type]["assets"][np.random.randint(0, len(topology['env_asset_list_type_b'][connection_type]["assets"]))]

            dimensions = self.get_dimensions(asset_type)
            if connection == 'n': new_offsetv -= dimensions[asset_type]['pos'][1]
            if connection == 's': new_offsetv += dimensions[asset_type]['pos'][1]	
            if connection == 'e': new_offseth += dimensions[asset_type]['pos'][0]
            if connection == 'w': new_offseth -= dimensions[asset_type]['pos'][0]

            function_asset(graph, dst_idx, dst_jdx, new_offseth, new_offsetv, dst_connection)

        for connection in list(openings):
            if   connection == origin:  continue

            if   connection == 'n':  recursiveConnection(connection, idx, jdx, idx - 1, jdx,     base_offsetx,           base_offsety - offsetv, 's')
            elif connection == 's':  recursiveConnection(connection, idx, jdx, idx + 1, jdx,     base_offsetx,           base_offsety + offsetv, 'n')
            elif connection == 'e':  recursiveConnection(connection, idx, jdx, idx,     jdx + 1, base_offsetx + offseth, base_offsety,           'w')
            elif connection == 'w':  recursiveConnection(connection, idx, jdx, idx,     jdx - 1, base_offsetx - offseth, base_offsety,           'e')


    # **************************************************************************************************************
    # World Creation

    def world(self, graph, origin, base_offsetx=0, base_offsety=0, base_offsetz=0):
        self.imported_objects = []  # Reset imported objects list
        self.base_offsetz = base_offsetz  # Set base offset for z-axis

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        self.get_node_idx_jdx(graph, origin[0], origin[1], base_offsetx, base_offsety, None)

        materials = {}
        materials.update({
            "CaveWall": self.get_material("CaveWall_Albedo", '../assets/textures/CaveWall_Albedo.jpg'),
            "RockPile": self.get_material("RockPile_Albedo", '../assets/textures/RockPile_Albedo.jpg'),
            "StriatedRock": self.get_material("StriatedRock_Albedo", '../assets/textures/StriatedRock_Albedo.jpg')
        })

        # 2. List of objects to assign the material to
        objects_to_assign = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']  # Can filter based on specific criteria

        # 3. Assign the material to all objects
        for obj in objects_to_assign:
            material = materials.get(obj.name.split('.')[0])
            if obj.data.materials:  obj.data.materials[0] = material     # Replace the first material slot or you can choose another index
            else:                   obj.data.materials.append(material)  # If no materials, append the material

        for obj in self.imported_objects:  # Select all imported objects for joining
            obj.select_set(True)

        bpy.context.view_layer.objects.active = self.imported_objects[0]  # Set active for join
        bpy.ops.object.join()

        merged_obj = bpy.context.active_object
        merged_obj.name = get_random_id()  # Rename the merged object

        return self.imported_objects, self.shaftOffsetx, self.shaftOffsety, self.shaftOffsetz
