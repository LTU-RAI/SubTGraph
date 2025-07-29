import os, bpy, yaml, shutil

from utils import *
from graph.shape import *

###

class FactoryObj():

    def __init__(self):
        self.imported_objects = []          # List of imported objects

        self.current_base_offsetz = 0.0     # Default base offset for z-axis
        self.next_base_offsetz = 0.0        # New base offset for z-axis
        self.asset_max_width = -np.inf      # Maximum width of spawned assets
        self.shaftOffset = [0.0, 0.0, 0.0]  # Offset of shaft tile

        # Dict with selection of available assets to spawn
        self.env_asset_dict = config['env_asset_list_type_a'] if config['generation_tile_type'] == 'a' else config['env_asset_list_type_b']
        
        # Dict with dimensions of assets for selected type
        with open(SUBTGRAPH_PATH + ('/config/dimensions-type-a.yaml' if config['generation_tile_type'] == 'a' else '/config/dimensions-type-b.yaml'), 'r') as file:
            self.dimensions = yaml.safe_load(file)

    def get_material(self, material_name: str, material_path: str, folder_path: str):
        """
        Load material image in blender and copy to generation folder.

        Parameters
        ----------
        material_name : str
            Name of the material
        material_path : str
            Path of the texture image
        folder_path : str
            Path of the mesh generation folder

        Returns
        -------
        out: Any
            The blender material object
        """

        # Create texture folder if not existing in generation folder
        if not os.path.exists(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder_path, "textures")):
            os.mkdir(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder_path, "textures"))

        # Copy texture image to generation folder if not exists
        texture = material_path.split('/')[-1]
        if not os.path.exists(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder_path, "textures", texture)):
            shutil.copy(material_path, os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder_path, "textures", texture))

        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True  # Enable node-based materials

        # Create an image texture node
        nodes = material.node_tree.nodes
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.image = bpy.data.images.load(os.path.join(SUBTGRAPH_PATH, config["generation_save_folder"], folder_path, "textures", texture))

        # Connect the texture node to the Principled BSDF shader
        principled_shader = nodes.get("Principled BSDF")
        material.node_tree.links.new(texture_node.outputs["Color"], principled_shader.inputs["Base Color"])

        return material

    # **************************************************************************************************************
    # Node Handling

    def get_node_info(self, graph: list, idx: int, jdx: int) -> tuple:
        """
        Get information of the specified node.

        Parameters
        ----------
        graph : list
            Connection graph
        idx : int
            Row of the selected node
        jdx : int
            Column of the selected node

        Returns
        -------
        openings : list
            List of the openings for this node
        connection_type : str
            Connection type of the node ('node', 'shaft', 'shaft_aux')
        angle : int
            Angle of the asset wrt. original position
        """
        openings = graph[idx][jdx].openings

        # 1 opening needs to check one value
        if 4 - openings.__len__() == 1:
            if   not isOpenNorth(openings):                                                         angle = 180
            elif not isOpenEast(openings):                                                          angle = 270
            elif not isOpenSouth(openings):                                                         angle = 0
            elif not isOpenWest(openings):                                                          angle = 90

        # 2 openings needs to check two values
        elif openings.__len__() == 2:
            if   not (isOpenEast(openings)  or isOpenWest(openings)):                               angle = 0
            elif not (isOpenNorth(openings) or isOpenSouth(openings)):                              angle = 90

            elif not (isOpenNorth(openings) or isOpenEast(openings)):                               angle = 270
            elif not (isOpenEast(openings) or isOpenSouth(openings)):                               angle = 0
            elif not (isOpenSouth(openings) or isOpenWest(openings)):                               angle = 90
            elif not (isOpenWest(openings) or isOpenNorth(openings)):                               angle = 180

        # 3 openings needs to check three values
        elif 4 - openings.__len__() == 3:
            if   not (isOpenNorth(openings) or isOpenWest(openings) or isOpenEast(openings)):       angle = 270
            elif not (isOpenNorth(openings) or isOpenEast(openings) or isOpenSouth(openings)):      angle = 0
            elif not (isOpenSouth(openings) or isOpenWest(openings) or isOpenEast(openings)):       angle = 90
            elif not (isOpenNorth(openings) or isOpenWest(openings) or isOpenSouth(openings)):      angle = 180

        # 4 openings needs no rotation
        else:                                                                                       angle = 0

        return openings, graph[idx][jdx].connection_type, angle

    def get_node_idx_jdx(self, graph: list, idx: int, jdx: int, base_offsetx: float, base_offsety: float, org_connection: str) -> None:
        """
        Import node asset into Blender context.

        Parameters
        ----------
        graph : list
            Connection graph
        idx : int
            Row of the selected node
        jdx : int
            Column of the selected node
        base_offsetx : float
            Accumulated x offset
        base_offsety : float
            Accumulated y offset
        org_connection: str
            Origin direction the asset attaches to
        """
        openings, connection_type, angle = self.get_node_info(graph, idx, jdx)  # Obtain node information

        # Randomly select which asset will be imported for the connection type
        asset_type = self.env_asset_dict[connection_type.split("_")[0]]["assets"][np.random.randint(0, len(self.env_asset_dict[connection_type.split("_")[0]]["assets"]))]

        if connection_type != "shaft_aux":  # All but destination shaft are imported (shaft_aux is a logical placeholder)

            # Import .obj asset
            obj_path = os.path.join(SUBTGRAPH_PATH, config['asset_path'], self.dimensions["folder"].replace('_', ' '), asset_type.replace('_', ' '), self.dimensions[asset_type]['name'] + '.obj')
            try:    bpy.ops.wm.obj_import(filepath=obj_path)
            except: print("Error importing object: " + obj_path);  return

            # Apply rotation and offset
            imported = bpy.context.selected_objects  
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            for obj in imported:
                obj["asset_type"] = asset_type

                # Remove internal objects if their textures are not specified by the user
                if "RockPile" in obj.name and config['texture_rock_pile'] == '':             bpy.data.objects.remove(obj);  continue
                if "StriatedRock" in obj.name  and config['texture_striated_rock'] == '':    bpy.data.objects.remove(obj);  continue

                obj.location.x += base_offsetx
                obj.location.y += base_offsety
                obj.location.z  = self.current_base_offsetz

                if connection_type == "shaft":  # Keep offset of shaft for next level spawn
                    self.shaftOffset = [obj.location.x, obj.location.y, obj.location.z]

                obj.rotation_euler = (0, 0, math.radians(angle))
                bpy.ops.object.transform_apply(rotation=True)

                self.imported_objects.append(obj)

        # Update horizontal and vertical offsets
        offsetx = self.dimensions[asset_type]['pos'][0]
        offsety = self.dimensions[asset_type]['pos'][1]

        if connection_type == "shaft":  # Keep z offset of shaft for next level
            self.next_base_offsetz = self.dimensions[asset_type]['pos'][2]

        # Update maximum width of spawned assetss
        if offsetx > self.asset_max_width:  self.asset_max_width = offsetx
        if offsety > self.asset_max_width:  self.asset_max_width = offsety

        # Mark the opening as visited if not first node and origin direction not visited
        if org_connection != None and org_connection not in graph[idx][jdx].openings:  graph[idx][jdx].openings.append(org_connection)

        diff = list(set(['n', 's', 'e', 'w']) - set(openings))  # Obtain openings left to satisfy

        # Add cave cap if no openings left
        if diff.__len__() <= 1 and connection_type != "shaft" and connection_type != "shaft_aux": 

            # Import .obj asset accordingly to the type
            asset_type = "cave_cap_type_b" if asset_type.split('_')[-1] == 'b' else "cave_cap_type_a"
            obj_path = os.path.join(SUBTGRAPH_PATH, config['asset_path'], self.dimensions["folder"].replace('_', ' '), asset_type.replace('_', ' '), self.dimensions[asset_type]['name'] + '.obj')
            try:    bpy.ops.wm.obj_import(filepath=obj_path)
            except: print("Error importing object: " + obj_path);  return

            # Update x and y offsets to locate the cap
            if angle == 0:  # North Cap
                new_offsetx = base_offsetx + offsetx + self.dimensions[asset_type]['pos'][0]
                new_offsety = base_offsety
            if angle == 180: # South Cap
                new_offsetx = base_offsetx - offsetx - self.dimensions[asset_type]['pos'][0]
                new_offsety = base_offsety
            if angle == 90:  # East Cap
                new_offsetx = base_offsetx
                new_offsety = base_offsety + offsety + self.dimensions[asset_type]['pos'][1]	
            if angle == 270:  # West Cap
                new_offsetx = base_offsetx
                new_offsety = base_offsety - offsety - self.dimensions[asset_type]['pos'][1]

            # Apply rotation and offset
            imported = bpy.context.selected_objects  
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            for obj in imported:
                obj["asset_type"] = asset_type

                # Remove internal objects if their textures are not specified by the user
                if "RockPile" in obj.name and config['texture_rock_pile'] == '':             bpy.data.objects.remove(obj);  continue
                if "StriatedRock" in obj.name  and config['texture_striated_rock'] == '':    bpy.data.objects.remove(obj);  continue

                obj.location.x += new_offsetx
                obj.location.y += new_offsety
                obj.location.z = self.current_base_offsetz

                obj.rotation_euler = (0, 0, math.radians(angle + 90))
                bpy.ops.object.transform_apply(rotation=True)

                self.imported_objects.append(obj)

        def recursiveConnection(org_connection: str, dst_connection: str, idx: int, jdx: int, dst_idx: int, dst_jdx: int, new_offsetx: float, new_offsety: float):
            """
            Select next generation step based on connections and update offsets accordingly.

            Parameters
            ----------
            org_connection : str
                Origin direction of the current asset
            dst_connection: str
                Destination direction of the attaching asset
            idx : int
                Row of the current node
            jdx : int
                Column of the current node
            dst_idx : int
                Row of the destination node
            dst_jdx : int
                Column of the destination node
            new_offsetx : float
                New accumulated x offset of destination node
            new_offsety : float
                New accumulated y offset of destination node
            """

            # Mark the opening as visited
            if org_connection not in openings:  graph[idx][jdx].openings.append(org_connection)

            # If this was the last opening, the asset was capped and no more connections are possible
            if graph[dst_idx][dst_jdx].openings.__len__() == 0: return

            # Nodes only attach to connections, get information for destination tile
            _, connection_type, _ = self.get_connection_info(graph, dst_idx, dst_jdx)
            asset_type = self.env_asset_dict[connection_type]["assets"][np.random.randint(0, len(self.env_asset_dict[connection_type]["assets"]))]

            # Update offsets accordingly
            if org_connection == 'n': new_offsety -= self.dimensions[asset_type]['pos'][1]
            if org_connection == 's': new_offsety += self.dimensions[asset_type]['pos'][1]	
            if org_connection == 'e': new_offsetx += self.dimensions[asset_type]['pos'][0]
            if org_connection == 'w': new_offsetx -= self.dimensions[asset_type]['pos'][0]

            # Spawn the asset in blender context
            self.get_connection_idx_jdx(graph, dst_idx, dst_jdx, new_offsetx, new_offsety, dst_connection)

        for connection in diff:  # Recursively complete the grid for each of the remaining connections
            if   connection == 'n':  recursiveConnection('n', 's', idx, jdx, idx - 1, jdx,     base_offsetx,           base_offsety - offsety)
            elif connection == 's':  recursiveConnection('s', 'n', idx, jdx, idx + 1, jdx,     base_offsetx,           base_offsety + offsety)
            elif connection == 'e':  recursiveConnection('e', 'w', idx, jdx, idx,     jdx + 1, base_offsetx + offsetx, base_offsety)
            elif connection == 'w':  recursiveConnection('w', 'e', idx, jdx, idx,     jdx - 1, base_offsetx - offsetx, base_offsety)
    

    # **************************************************************************************************************
    # Connection Handling

    def get_connection_info(self, graph: list, idx: int, jdx: int):
        """
        Get information of the specified node.

        Parameters
        ----------
        graph : list
            Connection graph
        idx : int
            Row of the selected node
        jdx : int
            Column of the selected node

        Returns
        -------
        openings : list
            List of the openings for this node
        connection_type : str
            Connection type of the node ('straight', 'corner', 'junction', 'intersection')
        angle : int
            Angle of the asset wrt. original position
        """
        return graph[idx][jdx].openings, graph[idx][jdx].connection_type, graph[idx][jdx].angle

    def get_connection_idx_jdx(self, graph: list, idx: int, jdx: int, base_offsetx: float, base_offsety: float, org_connection: str):
        """
        Import connection asset into Blender context.

        Parameters
        ----------
        graph : list
            Connection graph
        idx : int
            Row of the selected node
        jdx : int
            Column of the selected node
        base_offsetx : float
            Accumulated x offset
        base_offsety : float
            Accumulated y offset
        org_connection: str
            Origin direction the asset attaches to
        """
        openings, connection_type, angle = self.get_connection_info(graph, idx, jdx)  # Obtain connection information

        # Randomly select which asset will be imported for the connection type
        asset_type = self.env_asset_dict[connection_type]["assets"][np.random.randint(0, len(self.env_asset_dict[connection_type]["assets"]))]

        # Import .obj asset
        obj_path = os.path.join(SUBTGRAPH_PATH, config['asset_path'], self.dimensions["folder"].replace('_', ' '), asset_type.replace('_', ' '), self.dimensions[asset_type]['name'] + '.obj')
        try:    bpy.ops.wm.obj_import(filepath=obj_path)
        except: print("Error importing object: " + obj_path);  return

        # Apply rotation and offset
        imported = bpy.context.selected_objects
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        for obj in imported:
            obj["asset_type"] = asset_type

            # Remove internal objects if their textures are not specified by the user
            if "RockPile" in obj.name and config['texture_rock_pile'] == '':             bpy.data.objects.remove(obj);  continue
            if "StriatedRock" in obj.name  and config['texture_striated_rock'] == '':    bpy.data.objects.remove(obj);  continue

            obj.location.x += base_offsetx
            obj.location.y += base_offsety
            obj.location.z = self.current_base_offsetz
            
            obj.rotation_euler = (0, 0, math.radians(angle))
            bpy.ops.object.transform_apply(rotation=True)

            self.imported_objects.append(obj)

        # Update horizontal and vertical offsets
        offsetx = self.dimensions[asset_type]['pos'][0]
        offsety = self.dimensions[asset_type]['pos'][1]

        # Update maximum width of spawned assetss
        if offsetx > self.asset_max_width:  self.asset_max_width = offsetx
        if offsety > self.asset_max_width:  self.asset_max_width = offsety

        # Mark the opening as visited if not first node and origin direction not visited
        if org_connection != None and org_connection in graph[idx][jdx].openings:  graph[idx][jdx].openings.remove(org_connection)

        def recursiveConnection(org_connection: str, dst_connection: str, idx: int, jdx: int, dst_idx: int, dst_jdx: int, new_offsetx: float, new_offsety: float):
            """
            Select next generation step based on connections and update offsets accordingly.

            Parameters
            ----------
            org_connection : str
                Origin direction of the current asset
            dst_connection: str
                Destination direction of the attaching asset
            idx : int
                Row of the current node
            jdx : int
                Column of the current node
            dst_idx : int
                Row of the destination node
            dst_jdx : int
                Column of the destination node
            new_offsetx : float
                New accumulated x offset of destination node
            new_offsety : float
                New accumulated y offset of destination node
            """
            
            # Mark the opening as visited
            if org_connection in graph[idx][jdx].openings:  graph[idx][jdx].openings.remove(org_connection)
            
            # If destination is node and has not been visited, mark as next generation step
            if isinstance(graph[dst_idx][dst_jdx], NodeShape):   
                if graph[dst_idx][dst_jdx].openings.__len__() == 4: return
                function_info = self.get_node_info;     function_asset = self.get_node_idx_jdx

            # If destination is connection and has not been visited, mark as next generation step
            elif isinstance(graph[dst_idx][dst_jdx], ConnectionShape):
                if graph[dst_idx][dst_jdx].openings.__len__() == 0: return
                function_info = self.get_connection_info; function_asset = self.get_connection_idx_jdx
            
            # Connections attach to themselves and nodes, get information for destination tile
            _, connection_type, _ = function_info(graph, dst_idx, dst_jdx)
            asset_type = self.env_asset_dict[connection_type]["assets"][np.random.randint(0, len(self.env_asset_dict[connection_type]["assets"]))]

            # Update offsets accordingly
            if org_connection == 'n': new_offsety -= self.dimensions[asset_type]['pos'][1]
            if org_connection == 's': new_offsety += self.dimensions[asset_type]['pos'][1]	
            if org_connection == 'e': new_offsetx += self.dimensions[asset_type]['pos'][0]
            if org_connection == 'w': new_offsetx -= self.dimensions[asset_type]['pos'][0]

            # Spawn the asset (node or connection) in blender context
            function_asset(graph, dst_idx, dst_jdx, new_offsetx, new_offsety, dst_connection)

        for connection in list(openings):   # Recursively complete the grid for each of the remaining connections
            if   connection == org_connection:  continue  # Omit origin direction

            if   connection == 'n':  recursiveConnection('n', 's', idx, jdx, idx - 1, jdx,     base_offsetx,           base_offsety - offsety)
            elif connection == 's':  recursiveConnection('s', 'n', idx, jdx, idx + 1, jdx,     base_offsetx,           base_offsety + offsety)
            elif connection == 'e':  recursiveConnection('e', 'w', idx, jdx, idx,     jdx + 1, base_offsetx + offsetx, base_offsety)
            elif connection == 'w':  recursiveConnection('w', 'e', idx, jdx, idx,     jdx - 1, base_offsetx - offsetx, base_offsety)


    # **************************************************************************************************************
    # World Creation

    def world(self, graph:list, start: tuple, base_offsetx=0.0, base_offsety=0.0, base_offsetz=0.0, folder_path=""):
        """
        Create world from graph connectivity

        Parameters
        ----------
        graph : list
            Connection graph
        start : tuple
            Starting node of the generation
        base_offsetx : float
            Accumulated level x offset
        base_offsety : float
            Accumulated level y offset
        base_offsety : float
            Accumulated level z offset
        folder_path: str
            Path of the mesh generation folder
        """

        self.imported_objects = []                  # Reset imported objects list
        self.current_base_offsetz = base_offsetz    # Set base offset for z-axis

        # Select and remove all objects in blender python memory
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Initialize recursive generation of mesh from start node
        self.get_node_idx_jdx(graph, start[0], start[1], base_offsetx, base_offsety, None)

        # Add materials based on user specificationsn
        materials = {}
        materials.update({"CaveWall":   self.get_material("CaveWall_Albedo", SUBTGRAPH_PATH + '/assets/textures/' + config['texture_cave_wall'], folder_path)})
        materials.update({"Gravel":     self.get_material("CaveWall_Albedo", SUBTGRAPH_PATH + '/assets/textures/' + config['texture_cave_wall'], folder_path)})
        materials.update({"Cap":        self.get_material("CaveWall_Albedo", SUBTGRAPH_PATH + '/assets/textures/' + config['texture_cave_wall'], folder_path)})

        if config['texture_rock_pile'] != '':
            materials.update({"RockPile": self.get_material("RockPile_Albedo", SUBTGRAPH_PATH + '/assets/textures/' + config['texture_rock_pile'], folder_path)})

        if config['texture_striated_rock'] != '':
            materials.update({"StriatedRock": self.get_material("StriatedRock_Albedo", SUBTGRAPH_PATH + '/assets/textures/' + config['texture_striated_rock'], folder_path)})

        # List of objects to assign the material to
        objects_to_assign = [obj for obj in self.imported_objects if obj.type == 'MESH']
        
        for obj in objects_to_assign:  # Assign the material to all objects
            material = materials.get(obj.name.split('.')[0])
            if obj.data.materials:  obj.data.materials[0] = material
            else:                   obj.data.materials.append(material)

        # Select all imported objects for joining
        for obj in self.imported_objects:  obj.select_set(True) 

        bpy.context.view_layer.objects.active = self.imported_objects[0]  # Set active for join
        bpy.ops.object.join()

        merged_obj = bpy.context.active_object
        merged_obj.name = get_random_id()  # Rename the merged object

        return self.imported_objects, self.shaftOffset, self.next_base_offsetz, self.asset_max_width
