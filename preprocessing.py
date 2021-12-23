import sys
import os
from types import SimpleNamespace
import logging
import click

from utils import logger_utils, timer_utils
from preprocessing.preprocessing_controller import PreprocessingController


# yapf: disable
# TODO: Improve option definitions -> metavar, show_default, type, required
@click.command()
@click.option('-metaf', '--metadata_file', help='Path to metadata file (machine-metadata.xlsx)')
@click.option('-blendf', '--blender_file', help='Path to blender file (machine.blend)')
@click.option('-out', '--output_dir', help='Output root directory', default='./gltf-export-configurations')
@click.option('-n', '--n_images', help='Number of images to render for each part', default=10)
@click.option('-cams', '--camera_def_mode', help='Camera definition mode', default='global-static')
@click.option('-lights', '--light_def_mode', help='Light definition mode', default='global-static')
@click.option('-mats', '--material_def_mode', help='Material definition mode', default='static')
@click.option('-envmaps', '--envmap_def_mode', help='Environment Map definition mode', default='global-static')
# yapf: enable
def main(**kwargs):
    args = SimpleNamespace(**kwargs)

    metadata_file = args.metadata_file
    blender_file = args.blender_file
    output_dir = args.output_dir
    n_images = args.n_images
    camera_def_mode = args.camera_def_mode
    light_def_mode = args.light_def_mode
    material_def_mode = args.material_def_mode
    envmap_def_mode = args.envmap_def_mode

    # Init Logger
    LOGGER = logging.getLogger(__name__)
    os.makedirs(output_dir, exist_ok=True)
    logger_utils.init_logger(output_path=output_dir)

    # Print run args
    LOGGER.info('\n')
    LOGGER.info('Preprocessing options:')
    LOGGER.info(args)

    ppc = PreprocessingController(
        metadata_file,
        blender_file,
        output_dir,
        n_images,
        camera_def_mode,
        light_def_mode,
        material_def_mode,
        envmap_def_mode,
    )
    ppc.assign_materials()
    ppc.assign_cameras()


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
