""" Render gltf files via Blender Software """
import argparse
import os
import time
import bpy
import mathutils
import json

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

# MATERIALS

#########################################


def remove_vertex_colors(obj: bpy.types.Object) -> None:
    """Removes the Vertex Colors from the given object.

    Args:
        mat (bpy.types.Object): Blender object to remove the Vertex Colors from.
    """
    vertex_colors = obj.data.vertex_colors
    while vertex_colors:
        print(vertex_colors[0])
        vertex_colors.remove(vertex_colors[0])


def set_object_material_basecolor(obj: bpy.types.Object, color) -> None:
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


def import_materials_from_blend(file_path) -> list:
    """Loads materials from .blend files and replaces all materials with those in the target blend file.

    Args:
        file_path (str): The path to the .blend file containing materials
    """
    materials = None
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        materials = data_from.materials
        data_to.materials = data_from.materials
    return materials


def get_bpy_materials(materials_dir: str) -> dict:
    """Returns a dictionary of blender materials read from the materials directory.

    The materials_dir should contain .blend files that contain exactly one material.
    The name of the .blend file should match the material name in that file.

    Args:
        materials_dir (str): Path to directory containing .blend files that contain a material.
    """
    bpy_materials = {}
    for material_fn in os.listdir(material_dir):
        if material_fn.endswith(".blend"):
            bpy_materials[material_fn] = import_materials_from_blend(f"{materials_dir}/{material_fn}")[0]
    return bpy_materials


def apply_material(ob: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Material:
    """Apply material to given ob by material id

    Args:
        ob: object in scene to apply material to
        material_id: name of material in scene to apply
    """
    # remove former materials from object
    if ob.data.materials:
        ob.data.materials.clear()
    # Add new material to object
    ob.data.materials.append(mat)

    return mat


def apply_materials(scene: bpy.types.Scene, rcfg_part: dict, bpy_materials: dict) -> None:
    """Applies blender materials to all objects in the current scene.

    Args:
        scene (bpy.types.Scene): The blender scene.
        rcfg_part (dict): Machine part definition. Includes single_parts withmaterial definitions.
        bpy_materials (dict): Material dictionary that maps material names to actual blender materials.
    """
    for bpy_obj in scene.objects:
        # Reset obj color for all mesh objects
        if bpy_obj.type == "MESH":
            remove_vertex_colors(bpy_obj)
            # Check for obj references in render config
            for rcfg_single_part in rcfg_part["single_parts"]:
                if bpy_obj.name.startswith(rcfg_single_part["id"]):
                    # Do nothing if no material defined
                    if rcfg_single_part["material"] in ["none", None]:
                        print(f"Apply material: {bpy_obj.name}: {rcfg_single_part['material']}")
                        continue
                    # Apply material to mesh obj
                    print(f"Apply material: {bpy_obj.name}: {rcfg_single_part['material']}")
                    apply_material(bpy_obj, bpy_materials[rcfg_single_part["material"]])
                    break


#########################################

# RENDER

#########################################


def add_image_to_blender(file_path: str) -> bpy.types.Image:
    """Add image to .blend file

    Args:
        file_path (str): path to image file

    Returns:
        bpy.types.Image: created image node
    """
    return bpy.data.images.load(file_path, check_existing=True)


def add_hdri_map(file_path: str) -> tuple:
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
    node_background = tree_nodes.new(type="ShaderNodeBackground")
    # Add Environment Texture node
    node_environment = tree_nodes.new("ShaderNodeTexEnvironment")
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images.load(file_path)  # Relative path
    node_environment.location = -300, 0
    # Add Output node
    node_output = tree_nodes.new(type="ShaderNodeOutputWorld")
    node_output.location = 200, 0
    # Link all nodes
    links = node_tree.links
    link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])
    return node_background, node_environment


def translate_objects_by(objects: list, translate_by: mathutils.Vector) -> None:
    """Translate objects by given vector

    Args:
        objects (list): objects to translate
        translate_by (mathutils.Vector): vector to translate by
    """
    for ob in objects:
        ob.location += translate_by


def new_empty_scene() -> None:
    """Open new empty scene."""
    bpy.ops.wm.read_homefile(use_empty=True)


def objs_set_hide_render(objs: list[bpy.types.Object], hide_render: bool) -> None:
    """Hide/show given objects in render.

    Args:
        objs (list[bpy.types.Object]): Objects to hide/show in render.
        hide_render (bool): Defines whether to hide (True) or not hide (False) objects in render.
    """
    for obj in objs:
        obj.hide_render = hide_render


def get_compositor_depthmap_node_tree():
    """Returns a Blender Compositor node tree that renders a normalized depth map."""
    bpy.context.scene.use_nodes = True
    bpy.context.scene.render.use_compositing = True
    bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)
    # create input render layer node
    map = tree.nodes.new(type="CompositorNodeMapValue")
    map.size = [1.0]
    map.use_min = True
    map.min = [0]
    map.use_max = True
    map.max = [255]
    rl = tree.nodes.new("CompositorNodeRLayers")
    normalize = tree.nodes.new("CompositorNodeNormalize")
    invert = tree.nodes.new("CompositorNodeInvert")
    links.new(rl.outputs[2], normalize.inputs[0])
    links.new(normalize.outputs[0], map.inputs[0])
    links.new(map.outputs[0], invert.inputs[1])

    # Depth map as 1-Channel PNG
    depth_file_output_png = tree.nodes.new(type="CompositorNodeOutputFile")
    depth_file_output_png.format.color_mode = "BW"
    depth_file_output_png.format.file_format = "PNG"
    tree.links.new(invert.outputs[0], depth_file_output_png.inputs[0])
    # Depth map as OPEN_EXR
    depth_file_output_exr = tree.nodes.new(type="CompositorNodeOutputFile")
    depth_file_output_exr.format.file_format = "OPEN_EXR"
    tree.links.new(rl.outputs[2], depth_file_output_exr.inputs[0])

    return tree, depth_file_output_png, depth_file_output_exr


def setup_gpu_cycles() -> None:
    """Applies setup for GPU usage while rendering with Cycles render engine."""
    # Render settings CYCLES GPU rendering
    # Set the device_type
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
    # Set the device and feature set
    bpy.context.scene.cycles.device = "GPU"
    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons["cycles"].preferences.get_devices()
    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        for k in d.keys():
            print(f"{k}: {d[k]}")
        print("---")
        d["use"] = 1
        if d["type"] == 0:  # type 0 -> CPU
            d["use"] = 0


def apply_render_settings(
    engine: str = "CYCLES",
    device: str = "GPU",
    res_x: int = 256,
    res_y: int = 256,
    out_format: str = "PNG",
    out_quality: int = 100,
) -> None:
    """asd

    Args:
        engine (str): The render engine.
        device (str): The render device. One of ["GPU", "CPU"]
        res_x (int): Render image resolution width.
        res_y (int): Render image resolution height.
        out_format (str): Image output format. One of ["PNG", "JPG"]
        out_quality (int): Output quality in percent. Integer Range [0, 100]
    """
    scene = bpy.context.scene

    scene.render.engine = engine
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = True
    scene.render.image_settings.quality = out_quality
    scene.render.image_settings.file_format = out_format

    if engine.lower() == "cycles":
        scene.cycles.seed = 0
        scene.cycles.feature_set = "SUPPORTED"

        scene.cycles.samples = 4096
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.time_limit = 0

        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"

        scene.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
        scene.cycles.min_light_bounces = 0
        scene.cycles.min_transparent_bounces = 0
        scene.cycles.light_sampling_threshold = 0.01

        scene.cycles.max_bounces = 12
        scene.cycles.diffuse_bounces = 4
        scene.cycles.glossy_bounces = 4
        scene.cycles.transmission_bounces = 12
        scene.cycles.volume_bounces = 0
        scene.cycles.transparent_max_bounces = 8
        scene.cycles.sample_clamp_direct = 0
        scene.cycles.sample_clamp_indirect = 10
        scene.cycles.blur_glossy = 1

        scene.render.use_persistent_data = True

    if engine.lower() == "cycles" and device.lower() == "gpu":
        setup_gpu_cycles()


def load_gltf(file_path) -> None:
    """Loads gltf file into active scene.

    Args:
        file_path (str): Path the the gltf file.
    """
    bpy.ops.import_scene.gltf(filepath=file_path)

    bpy_world = bpy.context.scene.world
    if bpy_world is None:
        # create a new world
        new_world = bpy.data.worlds.new("World")
        new_world.use_nodes = True
        bpy.context.scene.world = new_world


def export_render_settings(out_path: str) -> None:
    """Exports the current render settings as json. file.

    Args:
        out_path (str): The path of the exported json file.
    """

    render_settings = {
        "engine": bpy.context.scene.render.engine,
        "resolution_x": bpy.context.scene.render.resolution_x,
        "resolution_y": bpy.context.scene.render.resolution_y,
        "film_transparent": bpy.context.scene.render.film_transparent,
        "quality": bpy.context.scene.render.image_settings.quality,
        "file_format": bpy.context.scene.render.image_settings.file_format,
        "cycles": {
            "seed": bpy.context.scene.cycles.seed,
            "feature_set": bpy.context.scene.cycles.feature_set,
            "samples": bpy.context.scene.cycles.samples,
            "use_adaptive_sampling": bpy.context.scene.cycles.use_adaptive_sampling,
            "adaptive_threshold": bpy.context.scene.cycles.adaptive_threshold,
            "time_limit": bpy.context.scene.cycles.time_limit,
            "use_denoising": bpy.context.scene.cycles.use_denoising,
            "denoiser": bpy.context.scene.cycles.denoiser,
            "denoising_input_passes": bpy.context.scene.cycles.denoising_input_passes,
            "min_light_bounces": bpy.context.scene.cycles.min_light_bounces,
            "min_transparent_bounces": bpy.context.scene.cycles.min_transparent_bounces,
            "light_sampling_threshold": bpy.context.scene.cycles.light_sampling_threshold,
            "max_bounces": bpy.context.scene.cycles.max_bounces,
            "diffuse_bounces": bpy.context.scene.cycles.diffuse_bounces,
            "glossy_bounces": bpy.context.scene.cycles.glossy_bounces,
            "transmission_bounces": bpy.context.scene.cycles.transmission_bounces,
            "volume_bounces": bpy.context.scene.cycles.volume_bounces,
            "transparent_max_bounces": bpy.context.scene.cycles.transparent_max_bounces,
            "sample_clamp_direct": bpy.context.scene.cycles.sample_clamp_direct,
            "sample_clamp_indirect": bpy.context.scene.cycles.sample_clamp_indirect,
            "blur_glossy": bpy.context.scene.cycles.blur_glossy,
            "use_persistent_data": bpy.context.scene.render.use_persistent_data,
        },
    }
    with open(out_path, "w") as outfile:
        json.dump(render_settings, outfile)


def render(
    scene: bpy.types.Scene,
    rcfg_part: dict,
    part_id: str,
    envmap_dir: str,
    out_dir: str,
) -> None:
    """Renders the given rcfg_part as defined in it's render_setups.

    Parses render_setups for the given rcfg_part and activates defined scene components
    for each specific render setup.

    Args:
        scene (bpy.types.Scene): The scene to render from.
        rcfg_part (dict): Machine part definition. Includes single_parts withmaterial definitions.
        part_id (str): Id of the part to render.
        envmap_dir (str): Directory containing envmap files.
        out_dir (str): Output directory.

    """
    # Load render setups
    render_setups = rcfg_part["scene"]["render_setups"]
    # Get cameras from gltf scene
    cameras = [obj for obj in scene.objects if obj.type == "CAMERA"]
    # Get lights from gltf scene
    lights = [obj for obj in scene.objects if obj.type == "LIGHT"]

    # Hide all lights
    objs_set_hide_render(lights, True)

    # DEPTH MAP RENDER SETUP
    depthmap_node_tree, depth_file_output_png, depth_file_output_exr = get_compositor_depthmap_node_tree()

    bpy.ops.object.select_by_type(extend=False, type="MESH")

    # scale all objects so largest dimension out of all objects equals 1
    # 1. Add selected objects to empty parent object
    parent_obj = bpy.data.objects.new("Empty", None)
    for obj in bpy.context.selected_objects:
        obj.parent = parent_obj
    # 2. Rescale mesh objects so largest dimension out of all objects equals 1
    max_xdim, max_ydim, max_zdim = 0, 0, 0
    for obj in parent_obj.children:
        max_xdim = obj.dimensions.x if obj.dimensions.x > max_xdim else max_xdim
        max_ydim = obj.dimensions.y if obj.dimensions.y > max_ydim else max_ydim
        max_zdim = obj.dimensions.z if obj.dimensions.z > max_zdim else max_zdim
    max_dim = max(max_xdim, max_ydim, max_zdim)
    parent_obj.scale = (1 / max_dim, 1 / max_dim, 1 / max_dim)

    # Render Loop
    for i, render_setup in enumerate(render_setups):
        # CAMERA: load, add to scene, zoom to object
        render_camera = cameras[render_setup["camera_i"]]
        scene.camera = render_camera
        bpy.ops.view3d.camera_to_view_selected()
        # Zoom in/out from 100% ?
        # translate_objects_by([cam], mathutils.Vector((0, 0, 0.5)))

        # LIGHTS: load, unhide
        render_lights = [lights[light_i] for light_i in render_setup["lights_i"]]
        objs_set_hide_render(render_lights, False)

        # ENVMAPS: load, add to blender, use as hdri envmap
        render_envmap_fn = f"{envmap_dir}/{render_setup['envmap_fname']}"
        add_image_to_blender(render_envmap_fn)
        add_hdri_map(render_envmap_fn)

        # RENDER
        scene.render.filepath = f"{out_dir}/render/rgb/{part_id}/{part_id}_{i:03d}"

        # Set up rendering of depth map files
        depth_file_output_png.base_path = f"{out_dir}/render/depth_png/{part_id}"
        depth_file_output_png.file_slots[0].path = f"{part_id}_{i:03d}_depth"

        depth_file_output_exr.base_path = f"{out_dir}/render/depth_exr/{part_id}"
        depth_file_output_exr.file_slots[0].path = f"{part_id}_{i:03d}_depth"

        bpy.ops.render.render(write_still=True)

        ## fix depth map filename by removing frame number
        os.rename(
            f"{depth_file_output_png.base_path}/{depth_file_output_png.file_slots[0].path}0001.png",
            f"{depth_file_output_png.base_path}/{depth_file_output_png.file_slots[0].path}.png",
        )
        os.rename(
            f"{depth_file_output_exr.base_path}/{depth_file_output_exr.file_slots[0].path}0001.exr",
            f"{depth_file_output_exr.base_path}/{depth_file_output_exr.file_slots[0].path}.exr",
        )

        ## CLEANUP
        # Hide lights again after rendered
        objs_set_hide_render(render_lights, True)


def get_args():
    """Returns script arguments as python variables."""
    parser = argparse.ArgumentParser()
    # Only consider script args, ignore blender args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index("--")
    script_args = all_arguments[double_dash_index + 1 :]

    parser.add_argument(
        "--gltf_dir",
        help="Directory with gltf files.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--material_dir",
        help="Data directory for materials.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--envmap_dir",
        help="Data directory for envmaps.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--rcfg_file",
        help="Render configuration file.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--out_dir",
        help="Directory to save the rendered images in.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--res_x",
        help="Pixel Resolution in X direction.",
        default=256,
        type=int,
    )
    parser.add_argument(
        "--res_y",
        help="Pixel Resolution in Y direction.",
        default=256,
        type=int,
    )
    parser.add_argument(
        "--out_quality",
        help="The output quality [0, 100].",
        default=100,
        type=int,
        metavar="[0, 100]",
        choices=range(0, 101),
    )
    parser.add_argument(
        "--out_format",
        help="Output image format",
        default="PNG",
        type=str,
        choices=["JPEG", "PNG"],
    )
    parser.add_argument(
        "--engine",
        help="Rendering engine",
        default="CYCLES",
        type=str,
    )
    parser.add_argument(
        "--device",
        help="The device used for rendering",
        default="GPU",
        type=str,
    )

    args, _ = parser.parse_known_args(script_args)
    return args


if __name__ == "__main__":
    tstart = time.time()
    args = get_args()
    print(f"Running Rendering with args:\n{args}")

    gltf_dir = args.gltf_dir
    material_dir = args.material_dir
    envmap_dir = args.envmap_dir
    rcfg_file = args.rcfg_file
    out_dir = args.out_dir
    res_x = args.res_x
    res_y = args.res_y
    out_format = args.out_format
    out_quality = args.out_quality
    engine = args.engine
    device = args.device

    # Load RCFG data
    with open(rcfg_file, "r") as rcfg_json:
        rcfg_data = json.load(rcfg_json)

    sorted_input_files = sorted(os.listdir(gltf_dir), key=lambda x: x.split("_")[0])

    for glb_fname in sorted_input_files:
        if not glb_fname.endswith(".glb"):
            continue
        new_empty_scene()
        load_gltf(os.path.join(gltf_dir, glb_fname))
        part_id = glb_fname[:-4]  # Remove .glb from glb filename
        scene = bpy.context.scene
        for part in rcfg_data["parts"]:
            if part["id"] == part_id:
                rcfg_part = part
                break

        if material_dir:
            bpy_materials = get_bpy_materials(material_dir)
            apply_materials(
                scene,
                rcfg_part,
                bpy_materials,
            )
        apply_render_settings(
            device=device,
            engine=engine,
            res_x=res_x,
            res_y=res_y,
            out_format=out_format,
            out_quality=out_quality,
        )
        render(
            scene,
            rcfg_part=rcfg_part,
            part_id=part_id,
            envmap_dir=envmap_dir,
            out_dir=out_dir,
        )

    # Export detailed render settings
    export_render_settings(out_path=f"{out_dir}/render_settings.json")
    tend = time.time() - tstart
    print(f"Rendered {len(os.listdir(gltf_dir))} imgs in {tend} seconds")
