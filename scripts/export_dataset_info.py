""" Just create and return (print) a unique dir name. Should be called from shell script"""
from email.policy import default
import click
import sys
import os
import re


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
    '--renders_dir',
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
def main():
    pass


if __name__ == '__main__':
    main()
