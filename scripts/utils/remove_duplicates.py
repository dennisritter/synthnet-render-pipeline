"""Export some info about a generated dataset."""

import os
import json
import click
from types import SimpleNamespace

# @click.command()
# @click.option(
#     '--dataset_dir',
#     help='Dataset root directory',
#     type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
#     required=True,
# )
# @click.option(
#     '--remove_ids',
#     help='IDs to remove from the dataset',
#     type=str,
#     required=True,
# )

DATASET_DIRS = [
    "./out/900841-00.00.00_drucker_se_su_st_st_256_32",
    "./out/900841-00.00.00_drucker_se_su_disabled_gray_256_32",
    "./out/900841-00.00.00_drucker_se_su_rdm_st_256_32",
    "./out/900841-00.00.00_drucker_se_su_st_gray_256_32",
]

REMOVE_IDS = ["900841-00.93.00", "900841-00.94.00", "418mm_D4_-_montiert_v2"]
N_IMGS_PER_PART = 32


def main(**kwargs):
    # args = SimpleNamespace(**kwargs)

    # Remove files for defined ids
    for root in DATASET_DIRS:
        gltf_dir = os.listdir(f"{root}/gltf")
        render_dir = os.listdir(f"{root}/render")
        with open(f'{root}/dataset_info.json', 'r', encoding='utf-8') as dataset_info_json:
            dataset_info = json.load(dataset_info_json)

        for f in gltf_dir:
            for id in REMOVE_IDS:
                if id in f:
                    print(f"removing {f}")
                    os.remove(f"{root}/gltf/{f}")
        for f in render_dir:
            for id in REMOVE_IDS:
                if id in f:
                    print(f"removing {f}")
                    os.remove(f"{root}/render/{f}")

        n_images_total = len(os.listdir(f"{root}/render"))
        n_rendered_parts = len(os.listdir(f"{root}/gltf"))
        print("-" * 20)
        print(f"New n_images_total: {n_images_total}")
        print(f"New n_rendered_parts: {n_rendered_parts}")

        dataset_info["n_images_total"] = n_images_total
        dataset_info["n_rendered_parts"] = n_rendered_parts
        dataset_info["comment"] += f"--- Removed duplicates: {REMOVE_IDS}"

        with open(f'{root}/dataset_info.json', 'w', encoding='utf-8') as dataset_info_json:
            json.dump(dataset_info, dataset_info_json, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
