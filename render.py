""" Render gltf files via Blender Software """
import argparse
import os
# blender api
import bpy

def clear_scene():
    bpy.ops.wm.read_homefile(use_empty=True)

def load_gltf(file_path):
    bpy.ops.import_scene.gltf(filepath=file_path)

def render(args, output_directory):
    # Scene setup
    scene = bpy.context.scene
    scene.render.engine = args.engine
    scene.render.image_settings.file_format = args.output_format
    scene.render.resolution_x = args.resolution_x
    scene.render.resolution_y = args.resolution_y
    scene.render.image_settings.quality = args.output_quality


    # render loop
    for obj in scene.objects:
        print(obj.name, obj.type)
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            file = os.path.join(output_directory, args.file_name + "_" + obj.name)
            bpy.context.scene.render.filepath = file
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
    parser.add_argument('-e', '--engine', type=str, required=False, default="BLENDER_EEVEE", help="rendering engine") #TODO add other engine options for blender (CYCLES)
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    input_directory = args.input_directory
    output_directory = args.output_directory
    for f in os.listdir(input_directory):
        if not f.endswith(".glb"):
            continue
        print("Rendering {0}".format(f))
        clear_scene()
        args.file_name = f
        load_gltf(os.path.join(input_directory, f))
        render(args, output_directory)


