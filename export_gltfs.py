""" Parse scene hierarchy and export objects """
import bpy
import mathutils

import json
import argparse


def create_light(name, data):
    """
    Create Light with given data
    Args:
        name: name of the light object
        data: data containing [type, position, orientation/target, focal_length]
    Returns:
    """
    light_type = data["type"]
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = data["position"] if "position" in data.keys() else [0, 0, 0]
    # TODO add settings for other light types
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
    camera_data = bpy.data.cameras.new(name=name)
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
        
def export_gltfs(settings, output_directory):
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
    # export all colletions and all objects as gltf
    print(len(all_objects.keys()))
    print(len(all_collections.keys()))

    print(all_objects.keys())
    print(all_collections.keys())

    # TODO create cameras and lights and apply materials

    # TODO export gltf files

def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument('-bf', '--blend_file', help="Ditrectory with gltf files.")
    parser.add_argument('-c', '--config', help="Ditrectory with gltf files.")
    parser.add_argument('-o', '--output_directory', help="Ditrectory to save the rendered images in.")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    blend_file = args["blend_file"]
    config_file = args["config"]
    output_directory = args["output_directory"]
    with open(config_file) as cfile:
        settings = json.load(cfile)
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    export_gltfs(settings, output_directory)

