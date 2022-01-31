""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""
import os
import logging
import json
import jsonschema

from preprocessing.utils.metadata import prepare_metadata
from preprocessing.parse_parts import parse_parts
from preprocessing import define_cameras, define_lights, define_materials
from preprocessing.models.scene import Scene
from utils import timer_utils

LOGGER = logging.getLogger(__name__)
LOG_DELIM = '- ' * 20

RCFG_VAL_SCHEMA_FILE = './validation/schemas/rcfg_schema_v2.json'


class PreprocessingController:
    SCENE_MODES = ['global', 'exclusive']
    CAMERA_DEF_MODES = ['sphere-uniform']
    LIGHT_DEF_MODES = ['sphere-uniform', 'range-uniform']
    MATERIAL_DEF_MODES = ['static']
    ENVMAP_DEF_MODES = ['static']

    def __init__(
        self,
        metadata_file: str,
        blend_file: str,
        output_dir: str,
        n_images: int,
        scene_mode: str,
        camera_def_mode: str,
        light_def_mode: str,
        material_def_mode: str,
        envmap_def_mode: str,
        camera_seed: int,
        light_seed: int,
    ):

        ## Validate parameters
        # validate metadata_file
        assert isinstance(metadata_file, str)
        assert os.path.isfile(metadata_file)
        # validate blend_file
        assert isinstance(blend_file, str)
        assert os.path.isfile(blend_file)
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
        # validate seeds
        assert isinstance(camera_seed, int)
        assert isinstance(light_seed, int)

        ## Assign options
        self.metadata_file = metadata_file
        self.blend_file = blend_file
        self.output_dir = output_dir
        self.n_images = n_images
        self.scene_mode = scene_mode.lower()
        self.camera_def_mode = camera_def_mode.lower()
        self.light_def_mode = light_def_mode.lower()
        self.material_def_mode = material_def_mode.lower()
        self.envmap_def_mode = envmap_def_mode.lower()
        self.camera_seed = camera_seed
        self.light_seed = light_seed

        # Prepared metadata.xlsx file as pandas DataFrame
        # rows: parts
        # cols: part_id, part_name, part_hierarchy, part_material, part_is_spare
        self.metadata = prepare_metadata(metadata_file)

        # A scene described by Cameras, Lights and envmaps and render_setups, that is used for
        # all parts
        self.global_scene = None

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

        # Add cameras - sphere uniform
        if self.camera_def_mode == 'sphere-uniform':
            cameras = define_cameras.get_cameras_sphere_uniform(n=n_images, seed=self.camera_seed)

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

        return cameras

    # TODO: Add functionality to specify a range for number of lights per scene
    #       => Add param n_lights_per_scene: Tuple = (1, 1)
    def _sample_lights(self, n_images: int):
        """ Sample lightsetups depending on self.light_def_mode. """
        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Sampling lights [mode={self.light_def_mode}]')

        # Add lights - sphere uniform
        if self.light_def_mode == 'sphere-uniform':
            lights = define_lights.get_lights_sphere_uniform(n=n_images, seed=self.light_seed)
        # Add lights - random within range
        if self.light_def_mode == 'range-uniform':
            lights = define_lights.get_lights_range_uniform(n=n_images, seed=self.light_seed)

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

        return lights

    def assign_envmaps(self):
        """ Assign Environment Maps to single parts depending on self.envmap_def_mode. """
        pass

    # TODO: Refactor / WIP
    # TODO: Add parameter to better define lightsetups?
    # TODO: Add parameter(s) to specify how to combine items of cameras, lights, envmaps.
    def _compose_render_setups(self, cameras: list, lights: list, envmaps: list):
        """ Compose Render Setups from lists of cameras, lights and envmaps.

            Returns a dictionary that contains camera_i, lights_i and envmaps_fname keys, 
            which reference an item in the respective list by its index (camera, lights) or filename (envmaps).

            Args:
                cameras (list): List of cameras 
                lights (list): List of lights
                envmaps (list): List of envmaps (filenames)
        
        """
        render_setups = []
        for i, _ in enumerate(cameras):
            render_setup = {
                "camera_i": i,
                "lights_i": [i],
                "envmap_fname": "default.hdr",
            }
            render_setups.append(render_setup)
        return render_setups

    # TODO: Add envmap support
    def build_scenes(self):
        if self.scene_mode == 'global':
            # Build scenes to use for each part
            # TODO: Add arguments for number of cameras and lights
            n_cameras = self.n_images
            n_lights = self.n_images

            cameras = self._sample_cameras(n_cameras)
            lights = self._sample_lights(n_lights)
            envmaps = ["default.hdr"]  # self.assign_envmaps()
            render_setups = self._compose_render_setups(
                cameras=cameras,
                lights=lights,
                envmaps=envmaps,
            )
            global_scene = Scene()
            global_scene.cameras = cameras
            global_scene.lights = lights
            global_scene.envmaps = envmaps
            global_scene.render_setups = render_setups
            self.global_scene = global_scene
        if self.scene_mode == 'exclusive':
            # Build scenes of for each part exclusively
            # TODO: Add arguments for number of cameras and lights
            n_cameras = self.n_images
            n_lights = self.n_images

            for part in self.parts:
                cameras = self._sample_cameras(n_cameras)
                lights = self._sample_lights(n_lights)
                envmaps = ["default.hdr"]  # self.assign_envmaps()
                render_setups = self._compose_render_setups(
                    cameras=cameras,
                    lights=lights,
                    envmaps=envmaps,
                )
                scene = Scene()
                scene.cameras = cameras
                scene.lights = lights
                scene.envmaps = envmaps
                scene.render_setups = render_setups
                part.scene = scene
            pass

    def export_rcfg_json(self, filename: str = 'rcfg.json'):
        tstart = timer_utils.time_now()
        rcfg_path = f'{self.output_dir}/{filename}'

        assert isinstance(filename, str)
        assert filename.endswith('.json')

        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Exporting rcfg [path={rcfg_path}]')

        self.val_rcfg_json()
        rcfg = json.loads(self.get_rcfg_json())
        with open(f'{self.output_dir}/{filename}', 'w') as f:
            json.dump(
                rcfg,
                f,
                default=lambda o: o.__dict__,
                indent=4,
                sort_keys=True,
            )
        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

    def get_rcfg_json(self):

        return json.dumps(
            {
                "global_scene": self.global_scene,
                "parts": self.parts
            },
            default=lambda o: o.__dict__,
            indent=4,
            sort_keys=True,
        )

    def val_rcfg_json(self):
        with open(RCFG_VAL_SCHEMA_FILE, 'r', encoding='UTF-8') as json_file:
            rcfg_schema = json.loads(json_file.read())
        rcfg = self.get_rcfg_json()
        try:
            jsonschema.validate(
                instance=json.loads(rcfg),
                schema=rcfg_schema,
            )
        except jsonschema.exceptions.ValidationError as err:
            LOGGER.error('Schema validation Error:', err)

        except jsonschema.exceptions.SchemaError as err:
            LOGGER.error('Schema Error:', err)
