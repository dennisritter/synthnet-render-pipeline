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


def render(glb_fname, output_directory):
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
    parser.add_argument('-i', '--input_directory', help="Ditrectory with gltf files.")
    parser.add_argument('-o', '--output_directory', help="Ditrectory to save the rendered images in.")
    parser.add_argument('-rx', '--resolution_x', help="Resolution in X", default=512)
    parser.add_argument('-ry', '--resolution_y', help="Resolution in Y", default=512)
    parser.add_argument('-oq', '--output_quality', help="Output Quality in range[1, 100]", default=100)
    parser.add_argument('-of', '--output_format', help="Output Format for images", default="JPEG")
    parser.add_argument('-e', '--engine', type=str, required=False, default="CYCLES", help="rendering engine")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    input_directory = args.input_directory
    output_directory = args.output_directory

    tstart = time.time()

    for glb_fname in os.listdir(input_directory):
        if not glb_fname.endswith(".glb"):
            continue
        clear_scene()
        load_gltf(os.path.join(input_directory, glb_fname))
        render(glb_fname, output_directory)

    tend = tstart - time.time()

    print(f"Rendered {len(os.listdir(input_directory))} imgs in {tend} seconds")
