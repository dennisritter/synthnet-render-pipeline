""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""
import os
import logging
import pandas as pd

from preprocessing.utils.metadata import prepare_metadata
from preprocessing.utils.sampling import sphere_sampling_random
from preprocessing.parse_parts import parse_parts
from preprocessing import define_cameras, define_lights, define_materials, define_envmaps
from utils import timer_utils

LOGGER = logging.getLogger(__name__)
LOG_DELIM = '- ' * 20


class PreprocessingController:
    CAMERA_DEF_MODES = ['global-static']
    LIGHT_DEF_MODES = ['global-static']
    MATERIAL_DEF_MODES = ['static']
    ENVMAP_DEF_MODES = ['global-static']

    def __init__(
        self,
        metadata_file: str,
        blender_file: str,
        output_dir: str,
        n_images: int,
        camera_def_mode: str,
        light_def_mode: str,
        material_def_mode: str,
        envmap_def_mode: str,
    ):

        ## Validate parameters
        # validate metadata_file
        assert isinstance(metadata_file, str)
        assert os.path.isfile(metadata_file)
        # validate blender_file
        assert isinstance(blender_file, str)
        assert os.path.isfile(blender_file)
        # validate output_dir
        assert isinstance(output_dir, str)
        os.makedirs(output_dir, exist_ok=True)
        assert os.path.exists(output_dir)
        # validate n_images
        assert isinstance(n_images, int)
        assert n_images > 0
        # validate camera_def_mode
        assert isinstance(camera_def_mode, str)
        assert camera_def_mode.lower() in self.CAMERA_DEF_MODES
        # validate light_def_mode
        assert isinstance(light_def_mode, str)
        assert light_def_mode.lower() in self.LIGHT_DEF_MODES
        # validate material_def_mode
        assert isinstance(material_def_mode, str)
        assert material_def_mode.lower() in self.MATERIAL_DEF_MODES
        # validate envmap_def_mode
        assert isinstance(envmap_def_mode, str)
        assert envmap_def_mode.lower() in self.ENVMAP_DEF_MODES

        ## Assign options
        self.metadata_file = metadata_file
        self.blender_file = blender_file
        self.output_dir = output_dir
        self.n_images = n_images
        self.camera_def_mode = camera_def_mode.lower()
        self.light_def_mode = light_def_mode.lower()
        self.material_def_mode = material_def_mode.lower()
        self.envmap_def_mode = envmap_def_mode.lower()

        # Prepared metadata.xlsx file as pandas DataFrame
        # rows: parts
        # cols: part_id, part_name, part_hierarchy, part_material, part_is_spare
        self.metadata = prepare_metadata(metadata_file)

        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Parsing unique Parts and SingleParts from {metadata_file}')
        # List of all Parts to render
        self.parts = parse_parts(self.metadata)
        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')
        LOGGER.info(LOG_DELIM)

    def assign_materials(self):
        """ Assign materials to single parts depending on self.material_def_mode. """

        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Assigning materials [mode={self.material_def_mode}]')

        # static: Read metadata materials and apply our materials depending on a static metadata_material:our_material map
        if self.material_def_mode == 'static':
            self.parts = define_materials.assign_materials_static(self.parts, self.metadata)

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')
        LOGGER.info(LOG_DELIM)

    def assign_cameras(self):
        pass

    def assign_lights(self):
        pass

    def assign_envmaps(self):
        pass