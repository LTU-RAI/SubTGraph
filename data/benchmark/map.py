import os, bpy, math
import mathutils

# ---------------------
# Configuration
# ---------------------
path = "/home/fernand0labra/rai-subtgraph/data/benchmark/lavatube"  # Change to your desired path

for dir in os.listdir(path):

    if os.path.isfile(os.path.join(path, dir, "subtgraph.png")): continue

    # ---------------------
    # Get the object
    # ---------------------

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    try:     bpy.ops.wm.obj_import(filepath=os.path.join(path, dir, "subtgraph.obj"))
    except:  print("Error importing object");  exit(1)
        
    bpy.data.worlds["World"].use_nodes = True
    bg_nodes = bpy.data.worlds["World"].node_tree.nodes
    bg_nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)  # RGBA

    objects_in_scene = bpy.context.scene.objects
    objects_in_scene = [obj for obj in objects_in_scene if obj.visible_get()]
    if len(objects_in_scene) == 1:
        obj = objects_in_scene[0]
    else:
        raise ValueError("There is either no object or more than one object in the workspace.")

    # Ensure object is visible and updated
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    mat = bpy.data.materials.get("MyWhiteMat")
    if not mat:
        mat = bpy.data.materials.new(name="MyWhiteMat")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Create nodes
        emission = nodes.new(type='ShaderNodeEmission')
        emission.inputs[0].default_value = (1, 1, 1, 1)  # White
        output = nodes.new(type='ShaderNodeOutputMaterial')
        links.new(emission.outputs[0], output.inputs[0])

    # Assign to object
    for idx in range(len(obj.data.materials)):
        obj.data.materials[idx] = mat

    # ---------------------
    # Calculate bounds in world space
    # ---------------------
    world_matrix = obj.matrix_world
    bbox = [world_matrix @ mathutils.Vector(corner) for corner in obj.bound_box]

    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)

    width_m = max_x - min_x
    height_m = max_y - min_y

    print(f"Mesh size: {width_m:.2f}m x {height_m:.2f}m")
        
    # ---------------------
    # Set camera
    # ---------------------
    scene = bpy.context.scene

    # Create or reuse camera
    cam = bpy.data.objects.get("TopDownCam")
    if not cam:
        cam_data = bpy.data.cameras.new("TopDownCam")
        cam = bpy.data.objects.new("TopDownCam", cam_data)
        scene.collection.objects.link(cam)

    scene.camera = cam
    cam.location = (min_x + width_m / 2, min_y + height_m / 2, 500)  # Z = 100m above
    cam.rotation_euler = (0, 0, 0)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = max(width_m, height_m)  # Covers whole object

    # ---------------------
    # Set render resolution
    # ---------------------
    scene.use_nodes = True
    scene.render.resolution_x = math.ceil(width_m)
    scene.render.resolution_y = math.ceil(height_m)
    scene.render.resolution_percentage = 100

    # ---------------------
    # Set render engine and output
    # ---------------------
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(path, dir, "subtgraph.png")

    # ---------------------
    # Render
    # ---------------------
    bpy.ops.render.render(write_still=True)
    print(f"Map saved to {scene.render.filepath}")