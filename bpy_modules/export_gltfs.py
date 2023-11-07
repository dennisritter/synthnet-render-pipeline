import json
import os
import time
import argparse
import bpy
import mathutils
from typing import Generator

import builtins as __builtin__

#########################################

# PRINT TO SYSTEM CONSOLE

#########################################


def console_print(*args, **kwargs) -> None:
    """Prints stuff to the console outside of blender. (to your terminal basically)"""
    for a in bpy.context.screen.areas:
        if a.type == "CONSOLE":
            c = {}
            c["area"] = a
            c["space_data"] = a.spaces.active
            c["region"] = a.regions[-1]
            c["window"] = bpy.context.window
            c["screen"] = bpy.context.screen
            s = " ".join([str(arg) for arg in args])
            for line in s.split("\n"):
                bpy.ops.console.scrollback_append(c, text=line)


def print(*args, **kwargs) -> None:
    """Override pythons print function to pass args to internal console_print."""
    console_print(*args, **kwargs)  # to Python Console
    __builtin__.print(*args, **kwargs)  # to System Console


#########################################

# BLENDER HELPER FUNCTIONS

#########################################


def parent(objects: list, parent: bpy.types.Object) -> None:
    """Parents objects to given parent

    Args:
        objects (list): list of children to parent
        parent (bpy.types.Object): object to parent to
    """
    for ob in objects:
        ob.parent = parent


def unparent(objects: list) -> list[bpy.types.Object]:
    """Unparent given objects

    Args:
        objects (list): list of objects to unparent

    Returns:
        list[bpy.types.Object]: previous parent for each object
    """
    parents = []
    for ob in objects:
        parents.append(ob.parent)
        ob.parent = None
    return parents


def translate_objects_by(objects: list, translate_by: mathutils.Vector) -> None:
    """Translate objects by given vector

    Args:
        objects (list): objects to translate
        translate_by (mathutils.Vector): vector to translate by
    """
    for ob in objects:
        ob.location += translate_by


def translate_all_objects_in_scene(root: bpy.types.Collection, translate_by: mathutils.Vector) -> None:
    """Translate all objects in current scene

    Args:
        root (bpy.types.Collection): root collection in scene
        translate_by (mathutils.Vector): vector to translate by
    """
    scene_collections = get_scene_collections(root)
    scene_objects = [ob for col in scene_collections for ob in col.objects]
    for ob in scene_objects:
        ob.location += translate_by


def get_objects_center_pivot(objects: list) -> mathutils.Vector:
    """Calculate the center of a list of objects by their transform pivot

    Args:
        objects (list): objects to get the center point for

    Returns:
        mathutils.Vector: center pivot
    """
    world_positions = []
    # get positions
    for ob in objects:
        world_positions.append(ob.matrix_world.translation)
    vec = mathutils.Vector([0, 0, 0])
    for pos in world_positions:
        vec += pos

    vec = vec / len(world_positions)
    return vec


def get_bounding_sphere(objects: list) -> list[mathutils.Vector, float]:
    """
    Get Bounding Sphere for list of objects based on bounding boxes

    Args:
        objects: list of objects to calculate with
    """
    points_co_global = []
    for obj in objects:
        points_co_global.extend([obj.matrix_world @ mathutils.Vector(bbox) for bbox in obj.bound_box])

    def get_center(ax):
        return (max(ax) + min(ax)) / 2 if ax else 0.0

    x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
    b_sphere_center = mathutils.Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
    b_sphere_radius = max(((point - b_sphere_center) for point in points_co_global)) if b_sphere_center else None
    return b_sphere_center, b_sphere_radius.length


def get_scene_collections(parent_coll: bpy.types.Collection) -> Generator:
    """Recursively walks through the bpy collections tree and.
    Returns a generator for scene collections.

    Args:
        parent_coll (bpy.types.Collection): The bpy collection to get children from
    Return:
        Generator<bpy.types.Collection>
    """
    yield parent_coll
    for child_coll in parent_coll.children:
        yield from get_scene_collections(child_coll)


def delete_objects(objects: list) -> None:
    """Delete given objects

    Args:
        objects (list[bpy.types.Object]): list of blender objects to delete
    """
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def create_scene(name: str) -> bpy.types.Scene:
    """Create new scene

    Args:
        name (str): name of the scene

    Returns:
        bpy.types.Scene: created scene
    """
    scene = bpy.data.scenes.new(name)
    return scene


def add_object_to_scene(scene: bpy.types.Scene, object_to_add: bpy.types.Object) -> None:
    """Add object to given scene

    Args:
        scene (bpy.types.Scene): scene to add object to
        object_to_add (bpy.types.Object): object to add
    """
    scene.collection.objects.link(object_to_add)


def get_scene(name: str) -> bpy.types.Scene:
    """Get scene by name

    Args:
        name (str): name of the scene

    Returns:
        bpy.types.Scene: scene object if found else None
    """
    if name in bpy.data.scenes.keys():
        return bpy.data.scenes[name]
    return None


def create_collection(name: str) -> bpy.types.Collection:
    """Create new collection

    Args:
        name (str): name of collection

    Returns:
        bpy.types.Collection: created collection
    """
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def add_object_to_collection(collection: bpy.types.Collection, object_to_add: bpy.types.Object) -> None:
    """Add object to collection

    Args:
        collection (bpy.types.Collection): [description]
        object_to_add (bpy.types.Object): [description]
    """
    collection.objects.link(object_to_add)


def export_gltf(bpy_objs_to_export: list, file_path: str) -> None:
    """Export gltf

    Args:
        bpy_objs_to_export: The blender
        file_path (str): path to output gltf file
    """
    select(bpy_objs_to_export)
    bpy.ops.export_scene.gltf(
        filepath=file_path,
        export_format="GLB",
        use_selection=True,
        export_image_format="JPEG",
        export_cameras=True,
        export_lights=True,
        export_extras=True,
    )


def get_objects_from_collection(collection: bpy.types.Collection) -> list:
    """Get objects of collection

    Args:
        collection (bpy.types.Collection): collection to get objects from

    Returns:
        list(bpy.types.Object): list of object in collection
    """
    children = []
    collection.name
    for ob in collection.objects:
        if type(ob) is bpy.types.Collection:
            children += get_objects_from_collection()
            continue
        children.append(ob)
    return children


def select(objects_to_select: list) -> None:
    """Select objects

    Args:
        objects_to_select (list): list of objects to select
    """
    selected_objects = []
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects_to_select:
        if type(ob) is bpy.types.Collection:
            print(ob)
            for c in get_objects_from_collection(ob):
                c.select_set(True)
                selected_objects.append(c.name)
            continue
        ob.select_set(True)
        selected_objects.append(ob.name)


def new_scene() -> None:
    """Create new scene"""
    bpy.ops.scene.new(type="EMPTY")


def open_scene(file_path: str) -> None:
    """Open .blend file

    Args:
        file_path (str): path to .blend
    """
    bpy.ops.wm.open_mainfile(filepath=file_path)


def save_scene(filepath: str) -> None:
    """Save current as .blend file

    Args:
        filepath (str): path to output .blend file
    """
    bpy.ops.wm.save_as_mainfile(filepath=filepath)


def show(obj: bpy.types.Object, scene=None) -> None:
    """Show object in scene

    Args:
        obj (bpy.types.Object): object to show
        scene ([type], optional): [description]. Defaults to None.
    """
    obj.hide_render = False


def hide_all() -> None:
    """Hide all objects"""
    for ob in bpy.data.objects:
        ob.hide_render = True


def get_object_by_name(name: str) -> bpy.types.Object:
    """Get object by name

    Args:
        name (str): name or key of the object

    Returns:
        bpy.types.Object: [description]
    """
    return bpy.data.objects[name]


def get_collection_by_name(name: str) -> bpy.types.Collection:
    """Get collection by name

    Returns:
        bpy.types.Collection: the collection in the scene
    """
    return bpy.data.collections[name]


def get_collections_by_suffix(suffix: str) -> list:
    """Get collections by suffix in scene

    Args:
        suffix (str): string to search for

    Returns:
        bpy.types.Collection: collections that end with the given string
    """
    return [ob for ob in bpy.context.scene.collection.children if ob.name.endswith(suffix)]


def add_image_to_blender(file_path: str) -> bpy.types.Image:
    """Add image to .blend file

    Args:
        file_path (str): path to image file

    Returns:
        bpy.types.Image: created image node
    """
    return bpy.data.images.load(file_path, check_existing=True)


def look_at(
    start: mathutils.Vector, target: mathutils.Vector, forward_vector: str = "-Z", up_vector: str = "Y"
) -> mathutils.Euler:
    """Calculate rotation to look at target point from start point

    Args:
        start (mathutils.Vector): point of origin
        target (mathutils.Vector): point of target
        forward_vector (str, optional): forward axis. Defaults to "-Z".
        up_vector (str, optional): secondary axis. Defaults to "Y".

    Returns:
        bpy.types.EulerRotation: rotation to look at target
    """
    direction = target - start
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat(forward_vector, up_vector)
    return rot_quat.to_euler()


def create_light(name: str, data: dict, collection=None) -> bpy.types.Object:
    """
    Create Light with given data

    Args:
        name (str): name of the light object
        data (dict): data containing [type, position, orientation/target, focal_length]
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

    return light_object


def create_camera(name: str, data: dict, collection=None) -> bpy.types.Object:
    """
    Create a camera in the scene with the given data

    Args:
        name (str): name of the camera
        data (dict): data containing [type, position, orientation/target, focal_length]
    Returns: camera object
    """
    # create camera data
    camera_data = bpy.data.cameras.new(name)
    camera_data.type = data["type"] if "type" in data.keys() else "PERSP"
    camera_data.lens = data["focal_length"] if "focal_length" in data.keys() else 50
    # create camera object and link to scene collection
    camera_object = bpy.data.objects.new("Camera", camera_data)
    if collection:
        collection.objects.link(camera_object)
    else:
        bpy.context.scene.collection.objects.link(camera_object)
    # set camera object settings
    camera_object.location = data["position"] if "position" in data.keys() else [0, 0, 0]
    if "target" in data.keys():
        target = data["target"]
        camera_object.rotation_euler = look_at(mathutils.Vector(camera_object.location), mathutils.Vector(target))

    # Roll camera around local Z-Axis by defined angle
    bpy.context.scene.transform_orientation_slots[0].type = "LOCAL"
    if "local_rotation" in data.keys():
        camera_object.rotation_euler.rotate_axis("Z", data["local_rotation"][2])

    # Set camera clipping start (meters)
    camera_object.data.clip_start = 0.001

    return camera_object


#########################################

# EXPORTER

#########################################


def get_bpy_single_parts(part: dict) -> list[bpy.types.Object]:
    """Returns a list of all single parts of the given part/assembly.

    Args:
        part (dict): A machine part description from the render configuration (rcfg).
    """
    if isinstance(part["blend_obj"], bpy.types.Collection):
        bpy_single_parts = part["blend_obj"].all_objects
    else:
        bpy_single_parts = [part["blend_obj"]]
    return bpy_single_parts


def get_bpy_cameras(part: dict) -> list[bpy.types.Object]:
    """Returns a list of cameras for the given machine part.

    Args:
        part (dict): A machine part description from the render configuration (rcfg).
    """
    return [create_camera(f"camera_{i}", cam) for i, cam in enumerate(part["scene"]["cameras"])]


def get_bpy_lights(part: dict) -> list[bpy.types.Object]:
    """Returns a list of lights for the given machine part.

    Args:
        part (dict): A machine part description from the render configuration (rcfg).
    """
    return [create_light(f"light_{i}", light) for i, light in enumerate(part["scene"]["lights"])]


class SceneExporter:
    """The Scene Exporter exports Blender scenes as GLTF (GLB) files.
    It contains all single parts of an assembly/part, cameras and lights to render various images
    of that part.
    """

    def __init__(self, rcfg: dict, out_dir: str):
        """Creates a new SceneExporter instance

        Args:
            rcfg (dict): The render configuration. Contains machine parts along with their single parts, lights, cameras
            out_dir (str): Path to the output directory.
        """
        # Set parts
        # -> See Part definition in Render Config (RCFG)
        self.parts = []
        self._set_parts(rcfg)
        self.out_dir = out_dir

    def _set_parts(self, rcfg) -> None:
        """Sets the self.parts attribute of the SceneExporter.

        Takes all parts described in the Render Config and checks whether they are matched in the blender file.
        If a part can not be matched, it is not added to the list of parts and subsequently not exported/rendered.
        If it is matched, it is added to the SceneExporter.parts list with the respective blender object added to the part["blend_obj"] property.

        Args:
            rcfg (dict): The render configuration. Contains machine parts along with their single parts, lights, cameras
        """

        if bpy.data.filepath:
            # Create list of parts to render
            # NOTE: Adds "blend_obj" property to each parts dictionary.
            self.parts = []
            part_ids = [part["id"] for part in rcfg["parts"]]
            root_coll = get_collections_by_suffix(".hierarchy")[0]
            # Get blender objects for all parts that can be matched with given part ids
            render_parts = self._get_render_parts(part_ids, root_coll)
            render_parts_ids = [part_id[0] for part_id in render_parts]
            render_parts_obj = [part_id[1] for part_id in render_parts]
            for part in rcfg["parts"]:
                # Keep parts only if a matching blend_obj has been identified
                if part["id"] in render_parts_ids:
                    part["blend_obj"] = render_parts_obj[render_parts_ids.index(part["id"])]
                    self.parts.append(part)
        else:
            for part in rcfg["parts"]:
                # load .obj into scene, name it after id
                # save render_part_obj
                bpy.ops.import_scene.obj(filepath=os.path.abspath(part["path"]))
                obj = bpy.context.selected_objects[0]
                part["blend_obj"] = obj
                self.parts.append(part)

    def _get_render_parts(self, part_ids: list, root_collection) -> list[tuple]:
        """returns a list of tuples.

        Args:
            part_ids (list<str>): A list of part IDs .
            root_collection (bpy_types.Collection): A blender collection that should contain machine parts subcollections.
        """
        print("- " * 20)
        print("Matching (part_id, bpy_object) pairs")

        matches = []
        # validate whether part_ids match with first part of collection names
        for part_id in part_ids:
            # Get collections
            for coll in get_scene_collections(root_collection):
                coll.name = coll.name.replace(" ", "_")
                if coll.name.startswith(part_id) and part_id not in [m[0] for m in matches] and coll != root_collection:
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

        print("---")
        print(f"root collection: {root_collection.name}")
        print(f"part_ids: {len(part_ids)}")
        print(f"matched: {len(matches)}")
        print(f"unmatched: {len(unmatched_part_ids)}")
        for unmatched in unmatched_part_ids:
            print(unmatched)
        print("- " * 20)
        return matches

    def export_gltfs(self) -> None:
        """Export gltf files based on scene descriptions parsed from a valid config file."""
        for part in self.parts:
            ### CREATE BPY SCENE COMPONENTS
            bpy_single_parts = get_bpy_single_parts(part)
            bpy_cameras = get_bpy_cameras(part)
            bpy_lights = get_bpy_lights(part)
            # MATERIALS
            # NOTE: Moved material assignment to render.py as advanced materials are not properly converted from blender->gltf
            #       Just Uncomment if you use basic materials only using blenders Principled BSDF shader node or other materials
            #       that can be mapped to gltf properly
            # ENVMAPS
            # NOTE: Moved Envmap assignment to render.py as for now it's not possible to define envmaps in a gltf file from blender.

            ### TRANSLATE PART TO WORLD CENTER
            # get the bounding sphere center
            bsphere_center, _ = get_bounding_sphere(bpy_single_parts)
            # unparent single parts from collections
            original_parents = unparent(bpy_single_parts)
            translate_objects_by(bpy_single_parts, -1 * bsphere_center)

            ### COLLECT OBJS TO EXPORT
            bpy_objs_to_export = []
            # NOTE: Sometimes not all single part objects are exported by adding the collection, so we add all single parts instead
            bpy_objs_to_export += bpy_single_parts
            bpy_objs_to_export += bpy_cameras
            bpy_objs_to_export += bpy_lights
            export_gltf(bpy_objs_to_export=bpy_objs_to_export, file_path=f"{self.out_dir}/{part['id']}.glb")

            # Reparent single parts
            for p, c in zip(original_parents, bpy_single_parts):
                parent([c], p)

            # delete cameras and lights that are not needed anymore
            delete_objects(bpy_cameras)
            delete_objects(bpy_lights)


def get_args():
    """Returns script arguments as python variables."""
    parser = argparse.ArgumentParser()
    # Only consider script args, ignore blender args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index("--")
    script_args = all_arguments[double_dash_index + 1 :]

    parser.add_argument(
        "--rcfg_file",
        help="Render configuration file.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--out_dir",
        help="Root directory to save outputs in.",
        type=str,
        required=True,
    )
    args, _ = parser.parse_known_args(script_args)
    return args


if __name__ == "__main__":
    tstart = time.time()
    args = get_args()
    print(f"Running GLTF export with args:\n{args}")

    rcfg_file = args.rcfg_file
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    # Get opened blender file path to reload scene when needed
    if bpy.data.filepath:
        blend_file = bpy.data.filepath
        open_scene(blend_file)
    else:
        create_scene(name="scene")
    # Load RCFG data
    with open(rcfg_file, "r") as rcfg_json:
        rcfg_data = json.load(rcfg_json)

    scene_exporter = SceneExporter(
        rcfg=rcfg_data,
        out_dir=out_dir,
    )
    scene_exporter.export_gltfs()

    tend = time.time() - tstart
    print("-" * 20)
    print(f"Done GLTF Export in {tend}")
