""" Render gltf files via Blender Software """
import argparse
import os
import time
import bpy

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


def clear_scene():
    bpy.ops.wm.read_homefile(use_empty=True)


def load_gltf(file_path):
    bpy.ops.import_scene.gltf(filepath=file_path)


def render(glb_fname,
           out_dir,
           res_x: int = 256,
           res_y: int = 256,
           out_format: str = "JPEG",
           out_quality: int = 100,
           engine: str = "CYCLES"):
    # Scene setup
    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.image_settings.quality = out_quality
    scene.render.image_settings.file_format = out_format
    scene.render.engine = engine
    cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']

    # render loop
    for i, cam in enumerate(cameras):
        bpy.context.scene.camera = cam
        # Change camera zoom to see whole object
        bpy.ops.object.select_by_type(extend=False, type='MESH')
        bpy.ops.view3d.camera_to_view_selected()

        bpy.context.scene.render.filepath = f"{out_dir}/{glb_fname}_{i}"
        bpy.ops.render.render(write_still=True)


def get_args():
    parser = argparse.ArgumentParser()
    # Only consider script args, ignore blender args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    parser.add_argument(
        '--in_dir',
        help="Directory with gltf files.",
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
        default="JPEG",
        type=str,
        choices=["JPEG", "PNG"],
    )
    parser.add_argument(
        '--engine',
        help="Rendering engine",
        default="CYCLES",
        type=str,
    )

    args, _ = parser.parse_known_args(script_args)
    return args


if __name__ == '__main__':
    tstart = time.time()
    args = get_args()
    print(f"Running Rendering with args:\n{args}")

    in_dir = args.in_dir
    out_dir = args.out_dir
    res_x = args.res_x
    res_y = args.res_y
    out_format = args.out_format
    out_quality = args.out_quality
    engine = args.engine

    sorted_input_files = sorted(os.listdir(in_dir), key=lambda x: x.split("_")[0])
    for glb_fname in sorted_input_files:
        if not glb_fname.endswith(".glb"):
            continue
        clear_scene()
        load_gltf(os.path.join(in_dir, glb_fname))
        render(
            glb_fname=glb_fname,
            out_dir=out_dir,
            res_x=res_x,
            res_y=res_y,
            out_format=out_format,
            out_quality=out_quality,
            engine=engine,
        )

    tend = time.time() - tstart
    print(f"Rendered {len(os.listdir(in_dir))} imgs in {tend} seconds")
