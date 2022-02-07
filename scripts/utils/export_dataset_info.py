"""Export some info about a generated dataset."""

import os
import json
import click
from types import SimpleNamespace


@click.command()
@click.option(
    '--out_dir',
    help='Output directory',
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    required=True,
)
@click.option(
    '--run_description',
    help='short descriptive name of the this dataset',
    type=str,
    required=True,
)
@click.option(
    '--camera_seed',
    help='initial random seed for camera sampling',
    type=int,
    required=True,
)
@click.option(
    '--light_seed',
    help='initial random seed for light sampling',
    type=int,
    required=True,
)
@click.option(
    '--n_images_per_part',
    help='How many images were rendered for each part/class',
    type=int,
    required=True,
)
@click.option(
    '--scene_mode',
    help='Were scenes samples global (all parts same scene) or exclusive (all parts exclusive scene)',
    type=str,
    required=True,
)
@click.option(
    '--camera_def_mode',
    help='How cameras were sampled/defined during preprocessing',
    type=str,
    required=True,
)
@click.option(
    '--light_def_mode',
    help='How lights were sampled/defined during preprocessing',
    type=str,
    required=True,
)
@click.option(
    '--material_def_mode',
    help='How materials were picked/defined/generated/mapped during preprocessing',
    type=str,
    required=True,
)
@click.option(
    '--envmap_def_mode',
    help='How envmaps were picked/defined/generated during preprocessing',
    type=str,
    required=True,
)
@click.option(
    '--rcfg_version',
    help='What version of the render config schema has been used',
    type=str,
    required=True,
)
@click.option(
    '--rcfg_file',
    help='Path to the Render Config file.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
)
@click.option(
    '--render_dir',
    help='Renders directory',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    required=True,
)
@click.option(
    '--render_res_x',
    help='Render resolution X',
    type=int,
    required=True,
)
@click.option(
    '--render_res_y',
    help='Render resolution Y',
    type=int,
    required=True,
)
@click.option(
    '--render_quality',
    help='Render quality',
    type=int,
    required=True,
)
@click.option(
    '--render_format',
    help='Render image format',
    type=str,
    required=True,
)
@click.option(
    '--render_engine',
    help='Render engine',
    type=str,
    required=True,
)
@click.option(
    '--comment',
    help='(optional) Any kind of additional information about the dataset or the idea behind it',
    type=str,
    default='No comment',
    required=False,
)
def main(**kwargs):
    args = SimpleNamespace(**kwargs)

    run_description = args.run_description
    camera_seed = args.camera_seed
    light_seed = args.light_seed
    n_images_per_part = args.n_images_per_part
    scene_mode = args.scene_mode
    camera_def_mode = args.camera_def_mode
    light_def_mode = args.light_def_mode
    material_def_mode = args.material_def_mode
    envmap_def_mode = args.envmap_def_mode
    rcfg_version = args.rcfg_version
    rcfg_file = args.rcfg_file
    render_dir = args.render_dir
    render_res_x = args.render_res_x
    render_res_y = args.render_res_y
    render_quality = args.render_quality
    render_format = args.render_format
    render_engine = args.render_engine
    comment = args.comment

    with open(rcfg_file, 'r') as f:
        rcfg = json.load(f)

    n_parts_total = len(rcfg["parts"])
    n_images_total = len(os.listdir(render_dir))
    n_rendered_parts = int(n_images_total / n_images_per_part)
    n_unidentified_parts = int(n_parts_total - n_rendered_parts)

    dataset_info = {
        "run_description": run_description,
        "n_images_total": n_images_total,
        "n_parts_total": n_parts_total,
        "n_images_per_part": n_images_per_part,
        "n_rendered_parts": n_rendered_parts,
        "n_unidentified_parts": n_unidentified_parts,
        "comment": comment,
        "preprocessing": {
            "camera_seed": camera_seed,
            "light_seed": light_seed,
            "scene_mode": scene_mode,
            "camera_def_mode": camera_def_mode,
            "light_def_mode": light_def_mode,
            "material_def_mode": material_def_mode,
            "envmap_def_mode": envmap_def_mode,
            "rcfg_version": rcfg_version,
        },
        "rendering": {
            "render_res_x": render_res_x,
            "render_res_y": render_res_y,
            "render_quality": render_quality,
            "render_format": render_format,
            "render_engine": render_engine,
        },
    }
    out_fname = "dataset_info.json"
    with open(f'{args.out_dir}/{out_fname}', 'w', encoding='utf-8') as f:
        json.dump(dataset_info, f, ensure_ascii=False, indent=4)

    print("- " * 20)
    print(f'Saved {out_fname}')
    print(json.dumps(dataset_info, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    main()
