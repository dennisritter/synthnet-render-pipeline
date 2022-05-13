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


def translate_objects_by(objects: list, translate_by: mathutils.Vector):
    """Translate objects by given vector

    Args:
        objects (list): objects to translate
        translate_by (mathutils.Vector): vector to translate by
    """
    for ob in objects:
        ob.location += translate_by


def clear_scene():
    bpy.ops.wm.read_homefile(use_empty=True)


def objs_set_hide_render(objs: list, hide_render: bool):
    for obj in objs:
        obj.hide_render = hide_render


def setup_gpu_cycles():
    # Render settings CYCLES GPU rendering
    # Set the device_type
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    # Set the device and feature set
    bpy.context.scene.cycles.device = 'GPU'
    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons['cycles'].preferences.get_devices()
    for d in bpy.context.preferences.addons['cycles'].preferences.devices:
        for k in d.keys():
            print(f'{k}: {d[k]}')
        print('---')
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
):
    scene = bpy.context.scene

    scene.render.engine = engine
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = True
    scene.render.image_settings.quality = out_quality
    scene.render.image_settings.file_format = out_format

    if engine.lower() == 'cycles':
        scene.cycles.seed = 0
        scene.cycles.feature_set = 'SUPPORTED'

        scene.cycles.samples = 4096
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.time_limit = 0

        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'

        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
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

    if engine.lower() == 'cycles' and device.lower() == 'gpu':
        setup_gpu_cycles()


def load_gltf(file_path):
    bpy.ops.import_scene.gltf(filepath=file_path)

    bpy_world = bpy.context.scene.world
    if bpy_world is None:
        # create a new world
        new_world = bpy.data.worlds.new("World")
        new_world.use_nodes = True
        bpy.context.scene.world = new_world

    # NOTE: Hack to load envmap path from extras data of first camera
    # camera_with_envmap = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA'][0]
    # if "ud_envmap" in camera_with_envmap.data.keys():
    #     envmap = camera_with_envmap.data["ud_envmap"]
    #     print(f"Adding Envmap: {envmap}")
    #     bpy_envmap = add_image_to_blender(envmap)
    #     add_hdri_map(envmap)


def apply_materials(rcfg_data: dict):
    pass


def render(
    rcfg_data: dict,
    part_id: str,
    material_dir: str,
    envmap_dir: str,
    out_dir: str,
):
    # # Scene setup
    scene = bpy.context.scene

    cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']
    lights = [obj for obj in scene.objects if obj.type == 'LIGHT']

    for part in rcfg_data["parts"]:
        if part["id"] == part_id:
            render_setups = part["scene"]["render_setups"]
            break

    # Hide all lights
    objs_set_hide_render(lights, True)
    # Render Loop
    for i, render_setup in enumerate(render_setups):
        render_camera = cameras[render_setup["camera_i"]]
        render_lights = [lights[light_i] for light_i in render_setup["lights_i"]]
        # Activate lights for this render
        objs_set_hide_render(render_lights, False)
        render_envmap_fn = f"{envmap_dir}/{render_setup['envmap_fname']}"
        add_image_to_blender(render_envmap_fn)
        add_hdri_map(render_envmap_fn)

        bpy.context.scene.camera = render_camera
        # Change camera zoom to see whole object
        bpy.ops.object.select_by_type(extend=False, type='MESH')
        bpy.ops.view3d.camera_to_view_selected()
        # Zoom out a little
        # translate_objects_by([cam], mathutils.Vector((0, 0, 0.5)))

        bpy.context.scene.render.filepath = f"{out_dir}/render/{part_id}_{i}"
        bpy.ops.render.render(write_still=True)

        # Hide lights again after rendered
        objs_set_hide_render(render_lights, True)
    # Write render settings into object and export as json
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
        }
    }
    with open(f'{out_dir}/render_settings.json', 'w') as outfile:
        json.dump(render_settings, outfile)


def get_args():
    parser = argparse.ArgumentParser()
    # Only consider script args, ignore blender args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    parser.add_argument(
        '--gltf_dir',
        help="Directory with gltf files.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--material_dir',
        help="Data directory for materials.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--envmap_dir',
        help="Data directory for envmaps.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--out_dir',
        help="Directory to save the rendered images in.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--rcfg_file',
        help="Render configuration file.",
        type=str,
        required=True,
    )
    parser.add_argument(
        '--res_x',
        help="Pixel Resolution in X direction.",
        default=256,
        type=int,
    )
    parser.add_argument(
        '--res_y',
        help="Pixel Resolution in Y direction.",
        default=256,
        type=int,
    )
    parser.add_argument(
        '--out_quality',
        help="The output quality [0, 100].",
        default=100,
        type=int,
        metavar="[0, 100]",
        choices=range(0, 101),
    )
    parser.add_argument(
        '--out_format',
        help="Output image format",
        default="PNG",
        type=str,
        choices=["JPEG", "PNG"],
    )
    parser.add_argument(
        '--engine',
        help="Rendering engine",
        default="CYCLES",
        type=str,
    )
    parser.add_argument(
        '--device',
        help="The device used for rendering",
        default="GPU",
        type=str,
    )

    args, _ = parser.parse_known_args(script_args)
    return args


if __name__ == '__main__':
    tstart = time.time()
    args = get_args()
    print(f"Running Rendering with args:\n{args}")

    gltf_dir = args.gltf_dir
    material_dir = args.material_dir
    envmap_dir = args.envmap_dir
    out_dir = args.out_dir
    rcfg_file = args.rcfg_file
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
        clear_scene()
        load_gltf(os.path.join(gltf_dir, glb_fname))
        part_id = glb_fname[:-4]  # Remove .glb from glb filename

        apply_materials(part_id)
        apply_render_settings(
            device=device,
            engine=engine,
            res_x=res_x,
            res_y=res_y,
            out_format=out_format,
            out_quality=out_quality,
        )
        render(
            rcfg_data=rcfg_data,
            part_id=part_id,
            envmap_dir=envmap_dir,
            material_dir=material_dir,
            out_dir=out_dir,
        )

    tend = time.time() - tstart
    print(f"Rendered {len(os.listdir(gltf_dir))} imgs in {tend} seconds")
