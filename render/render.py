""" Render gltf files via Blender Software """
import argparse
import os
import time
# blender api
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

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument('-i', '--in_dir', help="Directory with gltf files.", type=str)
    parser.add_argument('-o', '--out_dir', help="Directory to save the rendered images in.", type=str)
    parser.add_argument('-rx', '--resolution_x', help="Resolution in X", default=512, type=int)
    parser.add_argument('-ry', '--resolution_y', help="Resolution in Y", default=512, type=int)
    parser.add_argument('-oq', '--output_quality', help="Output Quality in range[1, 100]", default=100, type=int)
    parser.add_argument('-of', '--output_format', help="Output Format for images", default="JPEG", type=str)
    parser.add_argument('-e', '--engine', help="rendering engine", default="CYCLES", type=str)
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    in_dir = args.in_dir
    out_dir = args.out_dir

    print(args)
    tstart = time.time()

    sorted_input_files = sorted(os.listdir(in_dir), key=lambda x: x.split("_")[0])

    for glb_fname in sorted_input_files:
        if not glb_fname.endswith(".glb"):
            continue
        clear_scene()
        load_gltf(os.path.join(in_dir, glb_fname))
        render(glb_fname, out_dir, args)

    tend = time.time() - tstart

    print(f"Rendered {len(os.listdir(in_dir))} imgs in {tend} seconds")
