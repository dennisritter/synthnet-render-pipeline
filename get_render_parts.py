""" Parse scene hierarchy and export objects """
from typing import Generator
import bpy
import json
import argparse


def get_render_parts(part_ids: list, root_collection) -> list[tuple]:
    """ returns a list of tuples.

        Args:
            part_ids (list<str>): A list of part IDs .
            root_collection (bpy_types.Collection): A blender collection that should contain machine parts subcollections.
    """
    print(f'- ' * 20)
    print(f'Matching (part_id, bpy_object) pairs')

    matches = []
    # validate whether part_ids match with first part of collection names
    for part_id in part_ids:
        # Get collections
        for coll in get_scene_collections(root_collection):
            coll.name = coll.name.replace(" ", "_")
            if coll.name.startswith(part_id) and part_id not in [m[0] for m in matches]:
                matches.append((part_id, coll))

            for obj in coll.objects:
                obj.name = obj.name.replace(" ", "_")
                if obj.name.startswith(part_id) and part_id not in [m[0] for m in matches]:
                    matches.append((part_id, obj))

    # Assert
    # get matched part ids
    matched_part_ids = [part_id[0] for part_id in matches]
    unmatched_part_ids = [part_id for part_id in part_ids if part_id not in matched_part_ids]
    # assert no duplicates
    assert len(matched_part_ids) == len(set(matched_part_ids))

    # # Debug
    # for match in matches:
    #     print(f'{match[0], match[1].name}')
    # for nomatch in unmatched_part_ids:
    #     print(nomatch)

    print('---')
    print(f'root collection: {root_collection.name}')
    print(f'part_ids: {len(part_ids)}')
    print(f'matched: {len(matches)}')
    print(f'unmatched: {len(unmatched_part_ids)}')
    print(f'- ' * 20)


def get_scene_collections(parent_coll: bpy.types.Collection) -> Generator:
    """ Recursively walks through the bpy collections tree and.
        Returns a generator for scene collections.

        Args:
            parent_coll (bpy.types.Collection): The bpy collection to get children from
        Return:
            Generator<bpy.types.Collection>
    """
    yield parent_coll
    for child_coll in parent_coll.children:
        yield from get_scene_collections(child_coll)


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

    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


if __name__ == '__main__':
    args = get_args()
    rcfg_file = args.rcfg_file
    with open(rcfg_file) as f:
        rcfg = json.load(f)

    part_ids = [part["id"] for part in rcfg["parts"]]
    root_collection = [ob for ob in bpy.context.scene.collection.children if ob.name.endswith(".hierarchy")][0]
    get_parts(part_ids=part_ids, root_collection=root_collection)