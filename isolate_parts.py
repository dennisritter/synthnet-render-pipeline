""" Parse scene hierarchy and export objects """
import bpy
import mathutils

import json
import argparse
import os


def get_parts(part_ids: list):
    """ returns a list of parts.

        Args:
            part_ids (list<str>): A list of part IDs .
    """

    for part_id in part_ids:
        print(part_id)

    # hierarchy_root = [ob for ob in bpy.context.scene.collection.children if ob.name.endswith(".hierarchy")][0]


def get_args():
    parser = argparse.ArgumentParser()

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

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
    rcfg_file = args.rcfg_file
    output_dir = args.output_dir
    with open(rcfg_file) as f:
        rcfg = json.load(f)

    part_ids = [part["id"] for part in rcfg["parts"]]
    get_parts(part_ids=part_ids)