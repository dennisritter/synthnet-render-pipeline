""" Parse scene hierarchy and export objects """
import bpy
import mathutils

import json
import argparse
import os


def get_parts(part_ids: list, root_collection):
    """ returns a list of parts.

        Args:
            part_ids (list<str>): A list of part IDs .
            root_collection (bpy_types.Collection): A blender collection that should contain machine parts subcollections.
    """
    # n = 0
    # for part_id in part_ids:
    #     if part_id.startswith('900841'):
    #         n += 1
    #         print(part_id, n)

    # Get all collections
    collections = [coll for coll in get_collections(root_collection)]

    match = False
    matches = []

    # validate whether part_ids match with first part of collection names
    assemblies = [root_collection]
    for part_id in part_ids:
        for coll in collections:
            coll.name = coll.name.replace(" ", "_")
            if coll.name.startswith(part_id) and part_id not in [pid[0] for pid in matches]:
                matches.append((part_id, coll.name))
                assemblies.append(coll)

    single_parts = []
    for part_id in part_ids:
        for coll in assemblies:
            for obj in coll.objects:
                obj.name = obj.name.replace(" ", "_")
                if obj.name.startswith(part_id) and part_id not in [pid[0] for pid in matches]:
                    matches.append((part_id, obj.name))
                    single_parts.append(obj)

    for match in matches:
        print(match)

    match_parts = [pid[0] for pid in matches]
    match_objs = [pid[1] for pid in matches]
    unmatched = []
    for part_id in part_ids:
        if part_id not in match_parts:
            unmatched.append(part_id)

    for nomatch in unmatched:
        print(nomatch)

    print('-' * 20)
    print(f'root collection: {root_collection.name}')
    print(f'part_ids: {len(part_ids)}')
    print(f'matches: {len(matches)}')
    print(f'unmatched: {len(unmatched)}')


def get_collections(parent_coll):
    yield parent_coll
    for child_coll in parent_coll.children:
        yield from get_collections(child_coll)


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

    # Get all part ids from rcfg
    part_ids = [part["id"] for part in rcfg["parts"]]
    # locate root collection (where to search for part ids)
    scene_coll = bpy.context.scene.collection
    for coll in scene_coll.children:
        if coll.name.endswith(".hierarchy"):
            for subcoll in coll.children:
                root_collection = subcoll
    # root_collection = [ob for ob in bpy.context.scene.collection.children if ob.name.endswith(".hierarchy")][0]
    get_parts(part_ids=part_ids, root_collection=root_collection)