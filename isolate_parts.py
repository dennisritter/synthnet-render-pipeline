""" Parse scene hierarchy and export objects """
import bpy
import mathutils

import json
import argparse
import os


def get_parts(config):
    """ returns a list of parts.

        Args:
            config (object): Render configuration file.
    """
    parts = []
    for part in config["parts"]:
        id = part["part_id"]


def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument(
        '--rcfg_file',
        help="A Render Configuration JSON file that describes all parts and scenes to generate and export.",
        default="./cfg/rcfg_test_v2.json")
    parser.add_argument(
        '--output_dir',
        help="Root directory for all outputs",
        default="./out",
    )
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    config_file = args.config
    output_directory = args.output_directory
    print(config_file)
    with open(config_file) as cfile:
        settings = json.load(cfile)
    get_parts(settings, output_directory)