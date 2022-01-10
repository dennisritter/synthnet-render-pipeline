""" Parse scene hierarchy and export objects """
import bpy
import mathutils

import json
import argparse
import os


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


def create_light(name, data):
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
    bpy.context.collection.objects.link(light_object)
    light_object.location = data["position"] if "position" in data.keys() else [0, 0, 0]
    if "target" in data.keys():
        target = data["target"]
        light_object.rotation_euler = look_at(mathutils.Vector(light_object.location), mathutils.Vector(target))
    elif "rotation" in data.keys():
        light_object.rotation_euler = data["rotation"]
    return light_object


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


def create_camera(name, data):
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
    camera_data.type = data["type"] if "type" in data.keys() else "perspective"
    camera_data.lens = data["focal_length"] if "focal_length" in data.keys() else 50
    # create camera object and link to scene collection
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    # set camera object settings
    camera_object.location = data["position"] if "position" in data.keys() else [0, 0, 0]
    if "target" in data.keys():
        target = data["target"]
        camera_object.rotation_euler = look_at(mathutils.Vector(camera_object.location), mathutils.Vector(target))
    elif "rotation" in data.keys():
        camera_object.rotation_euler = data["rotation"]
    return camera_object


def collections(collection, col_list):
    """
    Get list of all collections in blender scene
    Args:
        collection: root object
        col_list: list to fill with collections
    Returns: list of all collections
    """
    col_list.append(collection)
    for sub_collection in collection.children:
        collections(sub_collection, col_list)


def _export_gltfs(settings, output_directory):
    """
    Export parts as gltf
    Args:
        blend_file: blend file containing hierarchical object consisting of collections and objects
        settings: config file containing global and single part settings
        output_directory: directory to export gltfs to

    Returns:
    """
    # find the hierarchy node
    hierarchy_root = [ob for ob in bpy.context.scene.collection.children if ob.name.endswith(".hierarchy")][0]
    # get all collections under hierarchy node
    collections_in_scene = []
    collections(hierarchy_root, collections_in_scene)
    all_collections = {}
    all_objects = {}
    for col in collections_in_scene:
        col_name = col.name.split("~")[0]
        if col_name not in all_collections.keys():
            all_collections[col_name] = col
            for obj in col.objects:
                obj_name = obj.name.split("~")[0]
                # check if obj is unique
                if not obj_name in all_objects.keys():
                    all_objects[obj_name] = obj


def generate_scene(file_path, part):
    # reset scene
    bpy.ops.wm.read_homefile(use_empty=True)
    # import object
    bpy.ops.import_scene.obj(filepath=file_path)
    # generate cameras
    for idx, cam_data in enumerate(part["cameras"]):
        create_camera("camera{0}".format(idx), cam_data)
    for idx, light_data in enumerate(part["lights"]):
        create_light("light{0}".format(idx), light_data)
    for idx, node_data in enumerate(part["single_parts"]):
        ob_name = node_data["part_id"]
        material_id = node_data["material"]
        if not ob_name in bpy.data.objects.keys():
            print(ob_name + " does not exist!")
            continue
        print("Materials in scene are {0}".format(bpy.data.materials.keys()))
        if not material_id in bpy.data.materials.keys():
            print(material_id + " does not exist!")
            continue
        apply_material(bpy.data.objects[ob_name], material_id)


def export_gltfs(config, output_directory):
    # get basic variables
    obj_dir = config["global_scene"]["obj_path"]
    default_file = config["global_scene"]["gltf_path"]
    materials_file = config["global_scene"]["materials_path"]

    #import materials
    print(materials_file)
    bpy.ops.import_scene.fbx(filepath=materials_file)

    parts = []
    for part in config["parts"]:
        id = part["part_id"]
        file_path = os.path.join(obj_dir, id + ".obj")
        if not os.path.exists(file_path):
            print("Object {0} does not exist in path {1}".format(id, obj_dir))
            continue
        # check if the settings for this object exist in config
        # generate_scene based on settings
        generate_scene(file_path=file_path, part=part)
        # export gltf
        bpy.ops.export_scene.gltf(filepath=os.path.join(output_directory, id + ".glb"),
                                  export_cameras=True,
                                  export_lights=True)
        parts.append(part["part_id"])
    # handle objects with default settings
    for obj in os.listdir(obj_dir):
        id, ext = obj.split(".")
        if id in parts:
            # if id is in parts it is already processed
            print("Skipped ", id)
            continue
        # create base scene
        # reset scene
        bpy.ops.wm.read_homefile(use_empty=True)
        # import object
        bpy.ops.import_scene.gltf(filepath=default_file)
        bpy.ops.import_scene.obj(filepath=os.path.join(obj_dir, obj))

        # export gltf
        bpy.ops.export_scene.gltf(filepath=os.path.join(output_directory, id + ".glb"),
                                  export_cameras=True,
                                  export_lights=True)


def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument('-c', '--config', help="Directory with gltf files.")
    parser.add_argument('-o', '--output_directory', help="Directory to save the rendered images in.")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    config_file = args.config
    output_directory = args.output_directory
    with open(config_file) as cfile:
        settings = json.load(cfile)
    export_gltfs(settings, output_directory)