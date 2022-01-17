""" Render gltf files via Blender Software """
import argparse
import os
import time
import bpy


def clear_scene():
    bpy.ops.wm.read_homefile(use_empty=True)


def load_gltf(file_path):
    bpy.ops.import_scene.gltf(filepath=file_path)


def render(glb_fname, output_directory, args):
    # Scene setup
    scene = bpy.context.scene
    scene.render.engine = args.engine
    scene.render.image_settings.file_format = args.output_format
    scene.render.resolution_x = args.resolution_x
    scene.render.resolution_y = args.resolution_y
    scene.render.image_settings.quality = args.output_quality
    cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']

    # render loop
    for i, cam in enumerate(cameras):
        bpy.context.scene.camera = cam
        out_path = f"{output_directory}/{glb_fname}_{i}"
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)


def get_args():
    parser = argparse.ArgumentParser()

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
        default=512,
        type=int,
    )
    parser.add_argument(
        '--res_y',
        help="Pixel Resolution in Y direction.",
        default=512,
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

    # Only consider script args, ignore blender args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]
    args, _ = parser.parse_known_args(script_args)
    return args


if __name__ == '__main__':
    tstart = time.time()
    args = get_args()
    print(f"Running Rendering with args:\n{args}")

    in_dir = args.in_dir
    out_dir = args.out_dir
    sorted_input_files = sorted(os.listdir(in_dir), key=lambda x: x.split("_")[0])

    for glb_fname in sorted_input_files:
        if not glb_fname.endswith(".glb"):
            continue
        clear_scene()
        load_gltf(os.path.join(in_dir, glb_fname))
        render(glb_fname, out_dir, args)

    tend = time.time() - tstart
    print(f"Rendered {len(os.listdir(in_dir))} imgs in {tend} seconds")
