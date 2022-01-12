import bpy
import random
import mathutils
from typing import Generator

def translate_all_objects_in_scene(root, translate_by):
    scene_collections = get_scene_collections(root)
    scene_objects = [ob for col in scene_collections for ob in col.objects]
    for ob in scene_objects:
        ob.location += translate_by

def get_bounding_sphere(objects:list):
    """
    Get Bounding Sphere for list of objects based on bounding boxes
    params:
        objects: list of objects to calculate with
    """
    points_co_global = []
    for obj in objects:
        points_co_global.extend([obj.matrix_world @ mathutils.Vector(bbox) for bbox in obj.bound_box])
    def get_center(l):
        return (max(l) + min(l)) / 2 if l else 0.0
    x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
    b_sphere_center = mathutils.Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
    b_sphere_radius = max(((point - b_sphere_center) for point in points_co_global)) if b_sphere_center else None
    return b_sphere_center, b_sphere_radius.length

def get_scene_collections(parent_coll: bpy.types.Collection) -> Generator:
    """ Recursively walks through the bpy collections tree and.
        Returns a generator for scene collections.

        Args:
            parent_coll (bpy.types.Collection): The bpy collection to get children from
        Return:
            Generator<bpy.types.Collection>
    """
    yield parent_coll
    for child_coll in parent_coll.children:
        yield from get_scene_collections(child_coll)

def delete(object: bpy.types.Object):
    bpy.ops.object.select_all(action='DESELECT')
    object.select = True
    bpy.ops.object.delete()

def create_scene(name: str):
    scene = bpy.data.scenes.new(name)
    return scene

def add_object_to_scene(scene: bpy.types.Scene, object_to_add: bpy.types.Object):
    scene.collection.objects.link(object_to_add)

def get_scene(name:str):
    if name in bpy.data.scenes.keys():
        return bpy.data.scenes[name]
    return None

def create_collection(name: str):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection

def add_object_to_collection(collection: bpy.types.Collection, object_to_add: bpy.types.Object):
    collection.objects.link(object_to_add)

def export_gltf(file_path: str, export_selected=True):
    bpy.ops.export_scene.gltf(filepath=file_path, export_format="GLB", use_selection=True, export_image_format="JPEG", export_cameras=True, export_lights=True)

def get_objects_from_collection(collection: bpy.types.Collection):
    children = []
    collection.name
    for ob in collection.objects:
        if type(ob) == bpy.types.Collection:
            children += get_objects_from_collection()
            continue
        children.append(ob)
    return children

def select(objects_to_select: list):
    selected_objects = []
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects_to_select:
        if type(ob) == bpy.types.Collection:
            print(ob)
            for c in get_objects_from_collection(ob):
                c.select_set(True)
                selected_objects.append(c.name)
            continue
        ob.select_set(True)
        selected_objects.append(ob.name)
    print("SELECTION:", bpy.context.selected_objects)
    print("SELECTED:", selected_objects)


def new_scene():
    bpy.ops.scene.new(type='EMPTY')

def open_scene(file_path: str):
    bpy.ops.wm.open_mainfile(filepath=file_path)

def save_scene(filepath: str):
    bpy.ops.wm.save_as_mainfile(filepath=filepath)

def set_keyframe(ob: bpy.types.Object, attr_path: str, frame: int):
    ob.keyframe_insert(data_path=attr_path, frame=frame)

def show(obj: bpy.types.Object, scene=None):
    obj.hide_render = False

def hide_all():
    for ob in bpy.data.objects:
        ob.hide_render = True

def get_object_by_name(name: str):
    return bpy.data.objects[name]

def get_collection_by_name(name: str):
    return bpy.data.collections[name]

def get_collections_by_suffix(suffix: str):
    return [ob for ob in bpy.context.scene.collection.children if ob.name.endswith(suffix)]

def add_hdri_map(file_path: str):
    # Get the environment node tree of the current scene
    node_tree = bpy.context.scene.world.node_tree
    tree_nodes = node_tree.nodes
    # Clear all nodes
    tree_nodes.clear()
    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')
    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images.load(file_path) # Relative path
    node_environment.location = -300,0
    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
    node_output.location = 200,0
    # Link all nodes
    links = node_tree.links
    link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])
    return node_background, node_environment

def add_image_to_blender(file_path):
    return bpy.data.images.load(file_path, check_existing=True)

def import_materials_from_blend(file_path):
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.materials = data_from.materials 

def look_at(start, target, forward_vector="-Z", up_vector="Y"):
    """
    Calculate camera rotation
    Args:
        position: start position
        point: target position
    Returns: euler rotation
    """
    direction = target - start
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat(forward_vector, up_vector)
    return rot_quat.to_euler()

def get_random_color():
    ''' generate rgb using a list comprehension '''
    r, g, b = [random.random() for i in range(3)]
    return r, g, b, 1

def apply_material(ob, material_id):
    """
    Apply material to given ob by material id
    Args:
        ob: object in scene to apply material to
        material_id: name of material in scene to apply
    Returns:
    """
    # Get material
    mat = bpy.data.materials.get(material_id)
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name=material_id)
    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)
    return mat

def create_light(name, data, collection=None):
    """
    Create Light with given data
    Args:
        name: name of the light object
        data: data containing [type, position, orientation/target, focal_length]
    Returns:
    """
    light_type = data["type"] if "type" in data.keys() else "POINT"
    light_data = bpy.data.lights.new(name, type=light_type)
    light_data.energy = data["intensity"] if "intensity" in data.keys() else 500
    light_object = bpy.data.objects.new(name, object_data=light_data)
    if collection:
        collection.objects.link(light_object)
    else:
        bpy.context.collection.objects.link(light_object)
    light_object.location = data["position"] if "position" in data.keys() else [0, 0, 0]
    if "target" in data.keys():
        target = data["target"]
        light_object.rotation_euler = look_at(mathutils.Vector(light_object.location), mathutils.Vector(target))
    elif "rotation" in data.keys():
        light_object.rotation_euler = data["rotation"]
    return light_object

def create_camera(name, data, collection=None):
    """
    Create a camera in the scene with the given data
    Args:
        name: name of the camera
        data: data containing [type, position, orientation/target, focal_length]
    Returns: camera object
    """
    #TODO make assertions that camera data contains certain keys
    # create camera data
    camera_data = bpy.data.cameras.new(name)
    camera_data.type = data["type"] if "type" in data.keys() else "PERSP"
    camera_data.lens = data["focal_length"] if "focal_length" in data.keys() else 50
    # create camera object and link to scene collection
    camera_object = bpy.data.objects.new('Camera', camera_data)
    if collection:
        collection.objects.link(camera_object)
    else:
        bpy.context.scene.collection.objects.link(camera_object)
    # set camera object settings
    camera_object.location = data["position"] if "position" in data.keys() else [0, 0, 0]
    if "target" in data.keys():
        target = data["target"]
        camera_object.rotation_euler = look_at(mathutils.Vector(camera_object.location), mathutils.Vector(target))
    elif "rotation" in data.keys():
        camera_object.rotation_euler = data["rotation"]
    return camera_object

def add_camera_frame(frame, camera):
    marker = scene.timeline_markers.new("marker{0}".format(frame), frame=frame)
    marker.camera = camera
    return marker

def remove_markers(objs):
    for obj in objs:
        bpy.types.TimelineMarkers.remove(obj)