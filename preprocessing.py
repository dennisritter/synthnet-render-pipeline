import sys
import os
from types import SimpleNamespace
import logging
import click

from utils import logger_utils, timer_utils, filesystem_utils
from preprocessing.preprocessing_controller import PreprocessingController


# yapf: disable
# TODO: Improve option definitions -> metavar, show_default, type, required
@click.command()
@click.option('-metaf', '--metadata_file', help='Path to metadata file (machine-metadata.xlsx)')
@click.option('-blendf', '--blend_file', help='Path to blender file (machine.blend)')
@click.option('-out', '--output_dir', help='Output root directory', default='./out')
@click.option('-desc', '--run_description', help='Description for this run', default='nodesc')
@click.option('-n', '--n_images', help='Number of images to render for each part', default=10)
@click.option('-cams', '--camera_def_mode', help='Camera definition mode', default='global-static')
@click.option('-lights', '--light_def_mode', help='Light definition mode', default='global-static')
@click.option('-mats', '--material_def_mode', help='Material definition mode', default='static')
@click.option('-envmaps', '--envmap_def_mode', help='Environment Map definition mode', default='global-static')
# yapf: enable
def main(**kwargs):
    args = SimpleNamespace(**kwargs)

    metadata_file = args.metadata_file
    blend_file = args.blend_file
    output_dir = args.output_dir
    run_description = args.run_description
    n_images = args.n_images
    camera_def_mode = args.camera_def_mode
    light_def_mode = args.light_def_mode
    material_def_mode = args.material_def_mode
    envmap_def_mode = args.envmap_def_mode

    # Get Run ID and create output root folder for this run
    run_id = filesystem_utils.get_run_id(outdir=output_dir)
    run_dir = f'{output_dir}/{run_id}-{run_description}'
    output_dir = run_dir
    os.makedirs(output_dir, exist_ok=True)

    # Init Logger
    LOGGER = logging.getLogger(__name__)
    log_dir = f'{output_dir}/logs'
    os.makedirs(log_dir, exist_ok=True)
    logger_utils.init_logger(output_path=log_dir)

    # Print run args
    LOGGER.info('\n')
    LOGGER.info('Preprocessing options:')
    LOGGER.info(args)

    ppc = PreprocessingController(
        metadata_file=metadata_file,
        blend_file=blend_file,
        output_dir=output_dir,
        n_images=n_images,
        camera_def_mode=camera_def_mode,
        light_def_mode=light_def_mode,
        material_def_mode=material_def_mode,
        envmap_def_mode=envmap_def_mode,
    )
    ppc.assign_materials()
    ppc.assign_cameras()
    ppc.assign_lights()


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
