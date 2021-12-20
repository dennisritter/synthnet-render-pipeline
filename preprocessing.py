import os
import argparse


def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument('-metaf', '--metadata_file', help='Path to metadata file (machine-metadata.xlsx)')
    parser.add_argument('-blendf', '--blender_file', help='Path to blender file (machine.blend)')
    parser.add_argument('-out', '--output_directory', help='Output root directory', default='./gltf-export-configurations')
    parser.add_argument('-n', '--n_images', help='Number of images to render for each part', default=10)
    parser.add_argument('-lights', '--light_sampling', help='Light sampling method', default='global-static')
    parser.add_argument('-cams', '--camera_sampling', help='Camera sampling method', default='global-static')
    parser.add_argument('-envmaps', '--environment_maps', help='Environment Map selection', default='global-static')
    parser.add_argument('-mats', '--camera_sampling', help='Material selection', default='static')
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

if __name__ == '__main__':
    args = get_args()
    input_directory = args.input_directory
    output_directory = args.output_directory