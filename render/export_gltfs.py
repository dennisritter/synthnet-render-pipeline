# exporter
import json
import os
import importlib
import sys
import argparse

# helper
import bpy
import random
import mathutils
from typing import Generator

#########################################

# BLENDER HELPER FUNCTIONS

#########################################


def translate_all_objects_in_scene(root, translate_by):
    scene_collections = get_scene_collections(root)
    scene_objects = [ob for col in scene_collections for ob in col.objects]
    for ob in scene_objects:
        ob.location += translate_by


def get_bounding_sphere(objects: list):
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


def get_scene(name: str):
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
    bpy.ops.export_scene.gltf(filepath=file_path,
                              export_format="GLB",
                              use_selection=True,
                              export_image_format="JPEG",
                              export_cameras=True,
                              export_lights=True)


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
    ob.keyframe_insert(data_dir=attr_path, frame=frame)


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
    node_environment.image = bpy.data.images.load(file_path)  # Relative path
    node_environment.location = -300, 0
    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')
    node_output.location = 200, 0
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


#########################################

# EXPORTER

#########################################


class SceneExporter():

    def __init__(self, config: object, data_dir: str):
        # Load render config (rcfg)
        self.config_data = config
        self.data_dir = data_dir

        self.material_path = os.path.join(self.data_dir, "materials")

    def get_scene_description(self):
        # parse global scenes
        scene_descriptions = [None]
        render_setups = [[]]
        global_scene = self.config_data["global_scene"]
        if global_scene:
            cameras = []
            lights = []
            envmaps = []
            materials = []
            # iterate over cameras
            for camera in global_scene["cameras"]:
                cameras.append(camera)
            # iterate over lights
            for light in global_scene["lights"]:
                lights.append(light)
            # iterate over envmaps
            for envmap in global_scene["envmaps"]:
                envmaps.append(envmap)
            global_scene_description = dict(cameras=cameras, lights=lights, envmaps=envmaps, materials=materials)
            scene_descriptions[0] = global_scene_description

        # parse part scenes
        parts = self.config_data["parts"]
        for part in parts:
            scene = part["scenes"]
            # add the materials to be imported to the scene description
            materials = [
                os.path.join(self.material_path, single_part["material"])
                if not single_part["material"] == "default" else "default" for single_part in part["single_parts"]
            ]
            if len(scene) > 0:
                cameras = []
                lights = []
                envmaps = []
                # iterate over cameras
                for camera in scene["cameras"]:
                    cameras.append(camera)
                # iterate over lights
                for light in scene["lights"]:
                    lights.append(light)
                # iterate over envmaps
                for envmap in scene["envmaps"]:
                    envmaps.append(envmap)
                local_scene_description = dict(cameras=cameras, lights=lights, envmaps=envmaps, materials=materials)
                # TODO check if scene description exists already and get the index?
                # add scene description
                scene_descriptions.append(local_scene_description)
                # add a new list for render setups using this scene
                render_setups.append([])
                scene_idx = len(scene_descriptions) - 1

                # get render setups
                local_render_setups = []
                for render_setup in part["render_setups"]:
                    local_render_setup = render_setup.copy()
                    local_render_setup["part"] = part
                    local_render_setups.append(local_render_setup)
                render_setups[scene_idx] += local_render_setups
            else:
                scene_idx = 0
                # iterate over render setups
                local_render_setups = []
                for render_setup in global_scene["render_setups"]:
                    local_render_setup = render_setup.copy()
                    local_render_setup["part"] = part
                    local_render_setups.append(local_render_setup)
                render_setups[scene_idx] += local_render_setups
            # add materials to scene description
            scene_descriptions[scene_idx]["materials"] = materials

        return scene_descriptions, render_setups

    def validata_scene_description(scene_description):
        # verify valid
        return scene_description

    def load_scene(self, scene_description):
        bpy_scene_description = {"cameras": [], "lights": [], "materials": [], "envmaps": [], "scene": None}
        bpy_scene_description["scene"] = create_scene("scene_descr")
        for idx, camera_data in enumerate(scene_description["cameras"]):
            bpy_camera = create_camera("camera_{0}".format(str(idx)), camera_data)
            bpy_scene_description["cameras"].append(bpy_camera)
            #add_object_to_scene(bpy_scene_description["scene"], bpy_camera)
        for idx, light_data in enumerate(scene_description["lights"]):
            bpy_light = create_light("light_{0}".format(str(idx)), light_data)
            bpy_scene_description["lights"].append(bpy_light)
            #add_object_to_scene(bpy_scene_description["scene"], bpy_light)
        for material in scene_description["materials"]:
            if material == "default":
                continue
            bpy_material = import_materials_from_blend(material)
            bpy_scene_description["materials"].append(bpy_material)
            #add_object_to_scene(bpy_scene_description["scene"], bpy_material)
        for img in scene_description["envmaps"]:
            bpy_image = add_image_to_blender(img)
            bpy_scene_description["envmaps"].append(bpy_image)
            #add_object_to_scene(bpy_scene_description["scene"], bpy_image)
        return bpy_scene_description

    def get_render_parts(self, part_ids: list, root_collection) -> list[tuple]:
        """ returns a list of tuples.

            Args:
                part_ids (list<str>): A list of part IDs .
                root_collection (bpy_types.Collection): A blender collection that should contain machine parts subcollections.
        """
        print(f'- ' * 20)
        print(f'Matching (part_id, bpy_object) pairs')

        matches = []
        # validate whether part_ids match with first part of collection names
        for part_id in part_ids:
            # Get collections
            for coll in get_scene_collections(root_collection):
                coll.name = coll.name.replace(" ", "_")
                if coll.name.startswith(part_id) and part_id not in [m[0] for m in matches]:
                    matches.append((part_id, coll))

                for obj in coll.objects:
                    obj.name = obj.name.replace(" ", "_")
                    if obj.name.startswith(part_id) and part_id not in [m[0] for m in matches]:
                        matches.append((part_id, obj))

        # Assert
        # get matched part ids
        matched_part_ids = [part_id[0] for part_id in matches]
        unmatched_part_ids = [part_id for part_id in part_ids if part_id not in matched_part_ids]
        # assert no duplicates
        assert len(matched_part_ids) == len(set(matched_part_ids))

        # # Debug
        # for match in matches:
        #     print(f'{match[0], match[1].name}')
        # for nomatch in unmatched_part_ids:
        #     print(nomatch)

        print('---')
        print(f'root collection: {root_collection.name}')
        print(f'part_ids: {len(part_ids)}')
        print(f'matched: {len(matches)}')
        print(f'unmatched: {len(unmatched_part_ids)}')
        print(f'- ' * 20)
        return matches

    def create_render_frames(self, bpy_scene_description, render_setups):
        # hide all objects
        for frame, render in enumerate(render_setups):
            # hide all
            hide_all()
            # get relevant objects
            bpy_ob = get_object_by_name(render["obj"]["id"])
            camera_index = render["camera_i"]
            lights_indices = render["lights_i"]
            env_map = render["envmap_fname"]
            cameras = bpy_scene_description["cameras"]
            lights = bpy_scene_description["lights"]
            # make object visible or active
            show(bpy_ob)
            # make camera active or visible
            show(cameras[camera_index])
            # make lights visible
            for idx in lights_indices:
                show(lights[idx])
            #TODO add envmap to material later
            # set keys
            set_keyframe(bpy_ob, "hide_render", frame)
            for camera in cameras:
                #set_keyframe(camera, "hide_viewport", frame)
                set_keyframe(camera, "hide_render", frame)
            for light in lights:
                #set_keyframe(light, "hide_viewport", frame)
                set_keyframe(light, "hide_render", frame)

    def export_gltfs(self, output_directory, parts_scene_path):
        scene_descriptions, render_setups = scene_exporter.get_scene_description()
        open_scene(parts_scene_path)
        for scene_description, render_setup in zip(scene_descriptions, render_setups):
            # create empty scene
            open_scene(parts_scene_path)
            # test per scene TODO optimize
            part_ids = [render["part"]["id"] for render_setup in render_setups for render in render_setup]
            root_col = get_collections_by_suffix(".hierarchy")[0]
            parts_scene_dict = {part_id: ob for part_id, ob in self.get_render_parts(part_ids, root_col)}
            # import the parts file
            bpy_scene_description = scene_exporter.load_scene(scene_description=scene_description)
            # get relevant objects from scene description
            cameras = bpy_scene_description["cameras"]
            lights = bpy_scene_description["lights"]
            # iterate over all renders in render setup
            for render_idx, render in enumerate(render_setup):
                if not render["part"]["id"] in parts_scene_dict.keys():
                    continue
                objects_to_export = []
                # assign material
                bpy_single_parts = []
                for single_part in render["part"]["single_parts"]:
                    # get object
                    if not single_part["id"] in parts_scene_dict.keys():
                        continue
                    bpy_ob = parts_scene_dict[single_part["id"]]
                    bpy_single_parts.append(bpy_ob)
                    if single_part["material"] == "default":
                        continue
                    continue
                    apply_material(bpy_ob, single_part["material"])
                # get the bounding sphere center
                bsphere_center, bsphere_radius = get_bounding_sphere(bpy_single_parts)
                translate_all_objects_in_scene(root_col, -1 * bsphere_center)
                # get object
                render_ob = parts_scene_dict[render["part"]["id"]]
                # get cameras
                render_camera = cameras[render["camera_i"]]
                render_lights = [lights[idx] for idx in render["lights_i"]]
                #env_map = render["envmap_fname"]
                # select objects and export to gltf
                objects_to_export.append(render_camera)
                objects_to_export += render_lights
                objects_to_export.append(render_ob)
                select(objects_to_export)
                # export gltf
                export_gltf(os.path.join(output_directory, render["part"]["id"] + "_" + str(render_idx) + ".glb"))
                translate_all_objects_in_scene(root_col, bsphere_center)

    def run(self):
        scene_description = self.get_scene_description

        #self.validata_scene_description(scene_description)
        #self.load_scene(scene_description)
        #self.create_render_frames(scene_description)


# def add_module_to_blender(name, path):
#     spec = importlib.util.spec_from_file_location(name, path)
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[spec.name] = module
#     spec.loader.exec_module(module)


def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument('--rcfg_file', help="Render configuration file.")
    parser.add_argument('--data_dir', help="Data directory for materials, envmaps and other dependencies.")
    parser.add_argument('--out_dir', help="Root directory to save outputs in.")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    import time

    tstart = time.time()

    args = get_args()

    rcfg_file = args.rcfg_file
    data_dir = args.data_dir
    out_dir = args.out_dir

    # Create out dir if not existent
    os.makedirs(out_dir, exist_ok=True)

    # Get opened blender file path to reload scene when needed
    # blend_file = bpy.path.abspath("//")
    blend_file = bpy.data.filepath

    with open(rcfg_file, "r") as rcfg_json:
        rcfg_data = json.load(rcfg_json)

    scene_exporter = SceneExporter(rcfg_data, data_dir)
    scene_exporter.export_gltfs(f'{out_dir}', blend_file)

    tend = time.time() - tstart
    print('-' * 20)
    print(f'Done GLTF Export in {tend}')