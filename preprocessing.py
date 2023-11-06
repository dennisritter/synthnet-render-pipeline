import os
from types import SimpleNamespace
import logging
import click

from utils import logger_utils, timer_utils
from preprocessing.preprocessing_controller import PreprocessingController

LOG_DELIM = "* " * 20


@click.command()
@click.option(
    "--topex_metadata_file",
    help="Path to xlsx metadata file for topex metadata (machine-metadata.xlsx)",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    default=None,
)
@click.option(
    "--topex_blend_file",
    help="Path to blender file from topex (machine.blend)",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    default=None,
)
@click.option(
    "--materials_dir",
    help="Path to blender materials directory for topex machine parts",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    default=None,
)
@click.option(
    "--obj_dir",
    help="Input directory for .obj files for data not related to topex. (e.g. ModelNet)",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    show_default=True,
    default=None,
)
@click.option(
    "--out_dir",
    help="Output root directory (created if not existent)",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    show_default=True,
    default="./out",
)
@click.option(
    "--n_images_per_part",
    help="Number of images to render for each part",
    type=click.INT,
    show_default=True,
    default=10,
)
@click.option(
    "--camera_def_mode",
    help="Camera definition mode",
    type=click.Choice(choices=PreprocessingController.CAMERA_DEF_MODES),
    show_default=True,
    show_choices=True,
    default=PreprocessingController.CAMERA_DEF_MODES[0],
)
@click.option(
    "--light_def_mode",
    help="Light definition mode",
    type=click.Choice(choices=PreprocessingController.LIGHT_DEF_MODES),
    show_default=True,
    show_choices=True,
    default=PreprocessingController.LIGHT_DEF_MODES[0],
)
@click.option(
    "--material_def_mode",
    help="Material definition mode",
    type=click.Choice(choices=PreprocessingController.MATERIAL_DEF_MODES),
    show_default=True,
    show_choices=True,
    default=PreprocessingController.MATERIAL_DEF_MODES[0],
)
@click.option(
    "--envmap_def_mode",
    help="Environment Map definition mode",
    type=click.Choice(choices=PreprocessingController.ENVMAP_DEF_MODES),
    show_default=True,
    show_choices=True,
    default=PreprocessingController.ENVMAP_DEF_MODES[0],
)
@click.option(
    "--camera_seed",
    help="Random camera seed for reproducibility",
    type=int,
    show_default=True,
    default=42,
)
@click.option(
    "--light_seed",
    help="Random light seed for reproducibility",
    type=int,
    show_default=True,
    default=43,
)
def main(**kwargs):
    args = SimpleNamespace(**kwargs)

    metadata_file = args.topex_metadata_file
    blend_file = args.topex_blend_file
    materials_dir = args.materials_dir
    obj_dir = args.obj_dir
    out_dir = args.out_dir
    n_images_per_part = args.n_images_per_part
    camera_def_mode = args.camera_def_mode
    light_def_mode = args.light_def_mode
    material_def_mode = args.material_def_mode
    envmap_def_mode = args.envmap_def_mode
    camera_seed = args.camera_seed
    light_seed = args.light_seed

    # Init Logger
    LOGGER = logging.getLogger(__name__)
    log_dir = f"{out_dir}/logs"
    os.makedirs(log_dir, exist_ok=True)
    logger_utils.init_logger(output_path=log_dir)

    # Print run args
    tstart = timer_utils.time_now()
    LOGGER.info("Start preprocessing with options:")
    LOGGER.info(args)

    ##### Start Actual Preprocessing
    ppc = PreprocessingController(
        metadata_file=metadata_file,
        blend_file=blend_file,
        materials_dir=materials_dir,
        obj_dir=obj_dir,
        output_dir=out_dir,
        n_images=n_images_per_part,
        camera_def_mode=camera_def_mode,
        light_def_mode=light_def_mode,
        material_def_mode=material_def_mode,
        envmap_def_mode=envmap_def_mode,
        camera_seed=camera_seed,
        light_seed=light_seed,
    )
    if materials_dir:
        ppc.assign_materials()
    ppc.build_scenes()
    ppc.export_rcfg_json(filename="rcfg.json")
    if metadata_file:
        ppc.export_augmented_metadata(filename="metadata", fileformats=["csv", "xlsx"])

    # Log preprocessing time
    tend = timer_utils.time_since(tstart)
    LOGGER.info(f"Preprocessing finished in {tend}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
