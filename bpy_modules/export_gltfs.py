# exporter
import json
import os
import time
import argparse
# helper
import bpy
import random
import mathutils
from typing import Generator

import builtins as __builtin__

#########################################

# PRINT TO SYSTEM CONSOLE


#########################################
def console_print(*args, **kwargs):
    for a in bpy.context.screen.areas:
        if a.type == 'CONSOLE':
            c = {}
            c['area'] = a
            c['space_data'] = a.spaces.active
            c['region'] = a.regions[-1]
            c['window'] = bpy.context.window
            c['screen'] = bpy.context.screen
            s = " ".join([str(arg) for arg in args])
            for line in s.split("\n"):
                bpy.ops.console.scrollback_append(c, text=line)


def print(*args, **kwargs):
    console_print(*args, **kwargs)  # to Python Console
    __builtin__.print(*args, **kwargs)  # to System Console


#########################################

# BLENDER HELPER FUNCTIONS

#########################################


def parent(objects: list, parent: bpy.types.Object):
    """ Parents objects to given parent

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


def translate_objects_by(objects: list, translate_by: mathutils.Vector):
    """Translate objects by given vector

    Args:
        objects (list): objects to translate
        translate_by (mathutils.Vector): vector to translate by
    """
    for ob in objects:
        ob.location += translate_by


def translate_all_objects_in_scene(root: bpy.types.Collection, translate_by: mathutils.Vector):
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


def add_object_to_scene(scene: bpy.types.Scene, object_to_add: bpy.types.Object):
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


def add_object_to_collection(collection: bpy.types.Collection, object_to_add: bpy.types.Object):
    """Add object to collection

    Args:
        collection (bpy.types.Collection): [description]
        object_to_add (bpy.types.Object): [description]
    """
    collection.objects.link(object_to_add)


def export_gltf(bpy_objs_to_export: list, file_path: str):
    """Export gltf

    Args:
        bpy_objs_to_export: The blender
        file_path (str): path to output gltf file
    """
    select(bpy_objs_to_export)
    bpy.ops.export_scene.gltf(filepath=file_path,
                              export_format="GLB",
                              use_selection=True,
                              export_image_format="JPEG",
                              export_cameras=True,
                              export_lights=True,
                              export_extras=True)


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
        if type(ob) == bpy.types.Collection:
            children += get_objects_from_collection()
            continue
        children.append(ob)
    return children


def select(objects_to_select: list):
    """Select objects

    Args:
        objects_to_select (list): list of objects to select
    """
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


def new_scene():
    """Create new scene"""
    bpy.ops.scene.new(type='EMPTY')


def open_scene(file_path: str):
    """Open .blend file

    Args:
        file_path (str): path to .blend
    """
    bpy.ops.wm.open_mainfile(filepath=file_path)


def save_scene(filepath: str):
    """Save current as .blend file

    Args:
        filepath (str): path to output .blend file
    """
    bpy.ops.wm.save_as_mainfile(filepath=filepath)


def set_keyframe(ob: bpy.types.Object, attr_path: str, frame: int):
    """Set keyframe on attribute for given frame

    Args:
        ob (bpy.types.Object): object with the keyable attribute
        attr_path (str): attr path on the object
        frame (int): frame to set the key on
    """
    ob.keyframe_insert(data_dir=attr_path, frame=frame)


def show(obj: bpy.types.Object, scene=None):
    """Show object in scene

    Args:
        obj (bpy.types.Object): object to show
        scene ([type], optional): [description]. Defaults to None.
    """
    obj.hide_render = False


def hide_all():
    """ Hide all objects """
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


def add_hdri_map(file_path: str) -> list:
    """Add hdri map to .blend

    Args:
        file_path (str): path to image file

    Returns:
        list(bpy.types.Material, bpy.types.EnvironmentTexture): [description]
    """
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


def add_image_to_blender(file_path: str) -> bpy.types.Image:
    """Add image to .blend file

    Args:
        file_path (str): path to image file

    Returns:
        bpy.types.Image: created image node
    """
    return bpy.data.images.load(file_path, check_existing=True)


def import_materials_from_blend(file_path):
    """ Loads materials from .blend files and replaces all materials with those in the target blend file.

        Args:
            file_path (str): The path to the .blend file containing materials
    
    """
    materials = None
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        materials = data_from.materials
        data_to.materials = data_from.materials
    return materials


def look_at(start: mathutils.Vector,
            target: mathutils.Vector,
            forward_vector: str = "-Z",
            up_vector: str = "Y") -> mathutils.Euler:
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


def get_random_color() -> list:
    """Generate random color

    Returns:
        list(float, float, float, float): [description]
    """
    r, g, b = [random.random() for i in range(3)]
    return r, g, b, 1


def apply_material(ob: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Material:
    """
    Apply material to given ob by material id
    Args:
        ob: object in scene to apply material to
        material_id: name of material in scene to apply
    Returns:
    """
    # Clear other mats?
    if ob.data.materials:
        ob.data.materials.clear()
    ob.data.materials.append(mat)

    # ob.data.materials.insert(0, mat)
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

    return light_object


def create_camera(name, data, collection=None):
    """
    Create a camera in the scene with the given data
    Args:
        name: name of the camera
        data: data containing [type, position, orientation/target, focal_length]
    Returns: camera object
    """
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

    # Roll camera around local Z-Axis by defined angle
    bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
    if "local_rotation" in data.keys():
        camera_object.rotation_euler.rotate_axis("Z", data["local_rotation"][2])

    # Set camera clipping start (meters)
    camera_object.data.clip_start = 0.001

    return camera_object


def add_camera_frame(frame: int, camera: bpy.types.Camera) -> bpy.types.TimelineMarker:
    """Add camera marker to frame which switches the main camera.

    Args:
        frame (int): frame to set the marker at
        camera (bpy.types.Camera): camera to mark

    Returns:
        bpy.types.TimelineMarker: created timeline marker 
    """
    marker = scene.timeline_markers.new("marker{0}".format(frame), frame=frame)
    marker.camera = camera
    return marker


def remove_markers(objs: list):
    """Remove TimelineMarkers from object

    Args:
        objs (list): [description]
    """
    for obj in objs:
        bpy.types.TimelineMarkers.remove(obj)


def remove_vertex_colors(obj: bpy.types.Object):
    """Removes the Vertex Colors from the given object.

    Args:
        mat (bpy.types.Object): Blender object to remove the Vertex Colors from.
    """
    vertex_colors = obj.data.vertex_colors
    while vertex_colors:
        print(vertex_colors[0])
        vertex_colors.remove(vertex_colors[0])


def set_object_material_basecolor(obj: bpy.types.Object, color):
    """Set the base color in the Principled BSDF node for the material of the given object.

        Args: 
            mat (bpy.types.Material)
    """
    mat = obj.data.materials[0]
    # Remove Texture input from base color and set a color
    if mat.node_tree.nodes["Principled BSDF"].inputs[0].links:
        base_color_link = mat.node_tree.nodes["Principled BSDF"].inputs[0].links[0]
        mat.node_tree.links.remove(base_color_link)
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color


#########################################

# EXPORTER


#########################################
def get_bpy_single_parts(part) -> list:
    # Get all BPY single parts of the current part
    if isinstance(part["blend_obj"], bpy.types.Collection):
        bpy_single_parts = part["blend_obj"].all_objects
    else:
        bpy_single_parts = [part["blend_obj"]]
    return bpy_single_parts


def get_bpy_cameras(part) -> list:
    return [create_camera(f"camera_{i}", cam) for i, cam in enumerate(part["scene"]["cameras"])]


def get_bpy_lights(part) -> list:
    return [create_light(f"light_{i}", light) for i, light in enumerate(part["scene"]["lights"])]


def get_bpy_materials(part, bpy_materials, materials_dir) -> dict:
    part_mats = [sp_mat["material"] for sp_mat in part["single_parts"]]
    # import materials
    for material_fn in part_mats:
        if material_fn == "none":
            continue
        if material_fn in bpy_materials.keys():
            continue
        # NOTE: Only works for materials included/defined as .blend files
        # If we use another material format, we need to first convert it to a Blender material
        # NOTE: We assume the file contains only the single material and id it by the file name
        bpy_material = import_materials_from_blend(f"{materials_dir}/{material_fn}")[0]
        bpy_materials[material_fn] = bpy_material
    return bpy_materials


def apply_materials(part, bpy_single_parts, bpy_materials):
    for bpy_single_part in bpy_single_parts:
        for single_part in part["single_parts"]:
            if bpy_single_part.name.startswith(single_part["id"]):
                # Remove the Vertex Colors from the object
                remove_vertex_colors(bpy_single_part)
                print(f"Apply material: {single_part['id']}: {single_part['material']}")
                if single_part["material"] in bpy_materials.keys():
                    apply_material(bpy_single_part, bpy_materials[single_part["material"]])
                    set_object_material_basecolor(bpy_single_part, (0.15, 0.15, 0.15, 1.0))
                continue


class SceneExporter():
    """The Scene Exporter exports scenes."""

    def __init__(self, rcfg: object, data_dir: str, blend_file: str, out_dir: str):
        # Set parts
        # -> See Part definition in Render Config (RCFG)
        self.parts = []
        self._set_parts(rcfg)

        self.data_dir = data_dir
        self.out_dir = out_dir
        self.blend_file = blend_file

    def _set_parts(self, rcfg):
        """ Sets the self.parts attribute of the SceneExporter.

            Takes all parts described in the Render Config and checks whether they are matched in the blender file.
            If a part can not be matched, it is not added to the list of parts and subsequently not exported/rendered.
            If it is matched, it is aded to the SceneExporter.parts list with the respective blender object added to the part["blend_obj"] property.

            Args:
                config
        """
        # Create list of parts to render
        # Note: Adds "blend_obj" property to each part.
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
                # If a global_scene is defined, assign it as a part scene
                if rcfg["global_scene"]:
                    part["scene"] = rcfg["global_scene"]
                self.parts.append(part)

    def _get_render_parts(self, part_ids: list, root_collection) -> list:
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
        for unmatched in unmatched_part_ids:
            print(unmatched)
        print(f'- ' * 20)
        return matches

    def export_gltfs(self):
        """ Export gltf files based on scene descriptions parsed from a valid 
            config file

        """
        # materials only need to be imported once each
        bpy_materials = {}
        for part in self.parts:
            ### CREATE BPY SCENE COMPONENTS
            bpy_single_parts = get_bpy_single_parts(part)
            bpy_cameras = get_bpy_cameras(part)
            bpy_lights = get_bpy_lights(part)
            # MATERIALS
            # NOTE: Moved material assignment to render.py as advanced materials are not properly converted from blender->gltf
            #       Just Uncomment if you use basic materials only using blenders Principled BSDF shader node or other materials
            #       that can be mapped to gltf properly
            # bpy_materials = get_bpy_materials(part, bpy_materials, materials_dir=f"{self.data_dir}/materials")
            #
            # print(bpy_materials)
            # apply_materials(part, bpy_single_parts, bpy_materials)

            # ----------
            # ENVMAPS
            # TODO: Check if we can add envmaps directly to gltf
            # envmap_dir = f"{self.data_dir}/envmaps"
            # bpy_envmaps = [add_image_to_blender(f"{envmap_dir}/{envmap_fn}") for envmap_fn in rcfg_scene["envmaps"]]

            ### Translate current part to world center
            # get the bounding sphere center
            bsphere_center, _ = get_bounding_sphere(bpy_single_parts)
            # unparent single parts from collections
            original_parents = unparent(bpy_single_parts)
            translate_objects_by(bpy_single_parts, -1 * bsphere_center)

            # COLLECT OBJS TO EXPORT
            bpy_objs_to_export = []
            # NOTE: Sometimes not all single part objects are exported by adding the collection, so we add all single parts instead
            bpy_objs_to_export += bpy_single_parts
            bpy_objs_to_export += bpy_cameras
            bpy_objs_to_export += bpy_lights
            export_gltf(bpy_objs_to_export=bpy_objs_to_export, file_path=f"{self.out_dir}/{part['id']}.glb")

            # if render_setup['envmap_fname'] != 'none':
            #         # render_envmap = add_hdri_map(f"{self.data_dir}/envmaps/{render_setup['envmap_fname']}")
            #         # render_envmap = add_image_to_blender(f"{self.data_dir}/envmaps/{render_setup['envmap_fname']}")
            #         # TODO: Apply actual Envmap to scene/render
            #         # we attach the envmap to the camera in the scene to identify easily later for now
            #         render_camera.data["ud_envmap"] = f"{self.data_dir}/envmaps/{render_setup['envmap_fname']}"

            # Reparent single parts
            for p, c in zip(original_parents, bpy_single_parts):
                parent([c], p)

            # delete cameras and lights that are not needed anymore
            delete_objects(bpy_cameras)
            delete_objects(bpy_lights)


def get_args():
    parser = argparse.ArgumentParser()
    # Only consider script args, ignore blender args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    parser.add_argument(
        '--rcfg_file',
        help="Render configuration file.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--data_dir',
        help="Data directory for materials, envmaps and other dependencies.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--out_dir',
        help="Root directory to save outputs in.",
        type=str,
        required=True,
    )
    args, _ = parser.parse_known_args(script_args)
    return args


if __name__ == '__main__':
    tstart = time.time()
    args = get_args()
    print(f"Running GLTF export with args:\n{args}")

    rcfg_file = args.rcfg_file
    data_dir = args.data_dir
    out_dir = args.out_dir
    # Create out dir if not existent
    os.makedirs(out_dir, exist_ok=True)
    # Get opened blender file path to reload scene when needed
    # blend_file = bpy.path.abspath("//")
    blend_file = bpy.data.filepath
    # Load RCFG data
    with open(rcfg_file, "r") as rcfg_json:
        rcfg_data = json.load(rcfg_json)

    open_scene(blend_file)
    scene_exporter = SceneExporter(
        rcfg=rcfg_data,
        data_dir=data_dir,
        blend_file=blend_file,
        out_dir=out_dir,
    )
    scene_exporter.export_gltfs()

    tend = time.time() - tstart
    print('-' * 20)
    print(f'Done GLTF Export in {tend}')
