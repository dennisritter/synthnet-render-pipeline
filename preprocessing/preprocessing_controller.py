""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""
import os
import logging
import json
import jsonschema
from jsonschema.exceptions import SchemaError
import pandas as pd
from typing import Tuple

from preprocessing.utils.metadata import prepare_metadata
from preprocessing.parse_parts import parse_parts
from preprocessing import define_cameras, define_lights, define_materials, define_envmaps, export_objs
from models.scene import Scene
from utils import timer_utils

LOGGER = logging.getLogger(__name__)
LOG_DELIM = '- ' * 20


class PreprocessingController:
    SCENE_MODES = ['global', 'part']
    CAMERA_DEF_MODES = ['sphere-uniform']
    LIGHT_DEF_MODES = ['range-uniform']
    MATERIAL_DEF_MODES = ['static']
    ENVMAP_DEF_MODES = ['static']

    def __init__(
        self,
        metadata_file: str,
        blend_file: str,
        ecfg_schema_file: str,
        output_dir: str,
        n_images: int,
        scene_mode: str,
        camera_def_mode: str,
        light_def_mode: str,
        material_def_mode: str,
        envmap_def_mode: str,
    ):

        ## Validate parameters
        # validate metadata_file
        assert isinstance(metadata_file, str)
        assert os.path.isfile(metadata_file)
        # validate blend_file
        assert isinstance(blend_file, str)
        assert os.path.isfile(blend_file)
        # Validate gltf export config validation JSON Schema file
        assert isinstance(ecfg_schema_file, str)
        assert os.path.isfile(ecfg_schema_file)
        # validate output_dir
        assert isinstance(output_dir, str)
        os.makedirs(output_dir, exist_ok=True)
        assert os.path.exists(output_dir)
        # validate n_images
        assert isinstance(n_images, int)
        assert n_images > 0
        # validate scene_mode
        assert isinstance(camera_def_mode, str)
        assert camera_def_mode.lower() in self.CAMERA_DEF_MODES
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
        self.blend_file = blend_file
        self.ecfg_schema_file = ecfg_schema_file
        self.output_dir = output_dir
        self.n_images = n_images
        self.scene_mode = scene_mode.lower()
        self.camera_def_mode = camera_def_mode.lower()
        self.light_def_mode = light_def_mode.lower()
        self.material_def_mode = material_def_mode.lower()
        self.envmap_def_mode = envmap_def_mode.lower()

        # Prepared metadata.xlsx file as pandas DataFrame
        # rows: parts
        # cols: part_id, part_name, part_hierarchy, part_material, part_is_spare
        self.metadata = prepare_metadata(metadata_file)

        # Add empty Scene
        #   Scene holds cameras and/or lights that are used if we
        #   don't specify cameras/lights for each part respectively
        self.global_scenes = []

        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Parsing unique Parts and SingleParts from {metadata_file}')
        # List of all Parts to render
        self.parts = parse_parts(self.metadata)
        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

    def assign_materials(self):
        """ Assign materials to single parts depending on self.material_def_mode. """

        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Assigning materials [mode={self.material_def_mode}]')

        # static: Read metadata materials and apply our materials depending
        # on a static metadata_material:our_material map
        if self.material_def_mode == 'static':
            self.parts = define_materials.assign_materials_static(self.parts, self.metadata)

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

    def _sample_cameras(self, n_images: int):
        """ Assign Cameras to single parts depending on self.camera-def_mode. """
        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Sampling cameras [mode={self.camera_def_mode}]')

        # Add cameras with random uniform pos to Scene
        if self.camera_def_mode == 'sphere-uniform':
            cameras = define_cameras.get_cameras_sphere_uniform(n_images)

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

        return cameras

    # TODO: Add functionality to specify a range for number of lights per scene
    #       => Add param n_lights_per_scene: Tuple = (1, 1)
    def _sample_lightsetups(self, n_images: int):
        """ Sample lightsetups depending on self.light_def_mode. """
        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Sampling lights [mode={self.light_def_mode}]')

        # Add lights with random pos to Scene
        if self.light_def_mode == 'range-uniform':
            lights = define_lights.get_lightsetups_range_uniform(n_images)

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

        return lights

    def assign_envmaps(self):
        """ Assign Environment Maps to single parts depending on self.envmap_def_mode. """
        pass

    # TODO: Add envmap support
    def build_scenes(self):
        if self.scene_mode == 'global':
            # Build scenes to use for each part
            cameras = self._sample_cameras(self.n_images)
            lightsetups = self._sample_lightsetups(self.n_images)
            for i in range(0, self.n_images):
                camera = cameras[i]
                lights = lightsetups[i]
                scene = Scene(camera=camera, lights=lights, envmap='')
                self.global_scenes.append(scene)
            pass
        if self.scene_mode == 'part':
            # Build scenes of for each part exclusively
            pass

    def export_ecfg_json(self, filename: str = 'ecfg.json'):
        tstart = timer_utils.time_now()
        ecfg_path = f'{self.output_dir}/{filename}'

        assert isinstance(filename, str)
        assert filename.endswith('.json')

        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Exporting ecfg [path={ecfg_path}]')

        self.val_ecfg_json()
        ecfg = json.loads(self.get_ecfg_json())
        with open(f'{self.output_dir}/{filename}', 'w') as f:
            json.dump(
                ecfg,
                f,
                default=lambda o: o.__dict__,
                indent=4,
                sort_keys=True,
            )
        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

    def get_ecfg_json(self):

        return json.dumps(
            {
                "global_scenes": self.global_scenes,
                "parts": self.parts
            },
            default=lambda o: o.__dict__,
            indent=4,
            sort_keys=True,
        )

    def val_ecfg_json(self):
        with open(self.ecfg_schema_file, 'r', encoding='UTF-8') as json_file:
            ecfg_schema = json.loads(json_file.read())
        ecfg = self.get_ecfg_json()
        try:
            jsonschema.validate(
                instance=json.loads(ecfg),
                schema=ecfg_schema,
            )
        except jsonschema.exceptions.ValidationError as err:
            LOGGER.error('Schema validation Error:', err)

        except jsonschema.exceptions.SchemaError as err:
            LOGGER.error('Schema Error:', err)

    # TODO: Implement using blender as a module
    # ? NOTE: Couldn't manage to build Blender on my machines to use it as a python module (Ubuntu 18.04, WSL2 Ubuntu 18.04)
    # def export_part_objs(self):
    #     """ Export OBJ file for each part in self.parts """
    #     obj_dir = f'{self.output_dir}/part_objs'
    #     export_objs.export_part_objs(
    #         parts=self.parts,
    #         blend_file=self.blend_file,
    #         out_dir=obj_dir,
    #     )
