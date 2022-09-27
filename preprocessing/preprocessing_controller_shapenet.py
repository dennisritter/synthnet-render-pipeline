""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""
import os
import logging
import json
import jsonschema
import random

from preprocessing import define_cameras, define_lights, define_materials
from preprocessing.models.scene import Scene
from utils import timer_utils

random.seed(42)

LOGGER = logging.getLogger(__name__)
LOG_DELIM = '- ' * 20

RCFG_VAL_SCHEMA_FILE = './validation/schemas/rcfg_schema_v3.json'


class PreprocessingControllerShapenet:
    """Preprocessing controller for shapenetcore dataset"""

    CAMERA_DEF_MODES = ['sphere-uniform', 'sphere-equidistant']
    LIGHT_DEF_MODES = ['sphere-uniform', 'range-uniform']
    MATERIAL_DEF_MODES = ['disabled', 'static', 'random']
    ENVMAP_DEF_MODES = ['disabled', 'white', 'gray', 'static']

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        n_images: int,
        camera_def_mode: str,
        light_def_mode: str,
        material_def_mode: str,
        envmap_def_mode: str,
        camera_seed: int,
        light_seed: int,
    ):

        ## Validate parameters
        # validate metadata_file
        assert isinstance(input_dir, str)
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
        # validate seeds
        assert isinstance(camera_seed, int)
        assert isinstance(light_seed, int)

        ## Assign options
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.n_images = n_images
        self.camera_def_mode = camera_def_mode.lower()
        self.light_def_mode = light_def_mode.lower()
        self.material_def_mode = material_def_mode.lower()
        self.envmap_def_mode = envmap_def_mode.lower()
        self.camera_seed = camera_seed
        self.light_seed = light_seed

        # Only parse synsets/labels present in ILSVRC dataset
        ILSVRC_SYNSETS = [
            '02747177', '02808440', '02843684', '02992529', '03085013', '03207941', '03337140', '03642806', '03691459',
            '03710193', '03759954', '03761084', '03938244', '03991062', '04074963', '04090263', '04330267', '04554684'
        ]

        # Parse Parts SHAPENET
        self.parts = []
        for label in os.listdir(f'{self.input_dir}/models'):
            if label in ILSVRC_SYNSETS:
                render_samples = random.sample(os.listdir(f'{self.input_dir}/models/{label}'), k=50)
                for entity in render_samples:
                    part = {
                        "id": entity,
                        "path": f'{self.input_dir}/{label}/{entity}/models/model_normalized.obj',
                        "scene": None,
                    }
                    self.parts.append(part)

    def _sample_cameras(self, n_images: int):
        """ Assign Cameras to single parts depending on self.camera-def_mode. """
        # Add cameras - sphere uniform
        if self.camera_def_mode == 'sphere-uniform':
            cameras = define_cameras.get_cameras_sphere_uniform(n=n_images, seed=self.camera_seed)
        if self.camera_def_mode == 'sphere-equidistant':
            cameras = define_cameras.get_cameras_sphere_equidistant(n=n_images, seed=self.camera_seed)

        return cameras

    def _sample_lights(self, n_images: int):
        """ Sample lightsetups depending on self.light_def_mode. """
        # Add lights - sphere uniform
        if self.light_def_mode == 'sphere-uniform':
            lights = define_lights.get_lights_sphere_uniform(n=n_images, seed=self.light_seed)
        # Add lights - random within range
        if self.light_def_mode == 'range-uniform':
            lights = define_lights.get_lights_range_uniform(n=n_images, seed=self.light_seed)
        return lights

    def _assign_envmaps(self, n_images: int):
        """ Assign Environment Maps to single parts depending on self.envmap_def_mode. """
        # No envmaps
        if self.envmap_def_mode == 'disabled':
            envmaps = []
        if self.envmap_def_mode == 'white':
            envmaps = ['white.jpg' for _ in range(0, n_images)]
        if self.envmap_def_mode == 'gray':
            envmaps = ['gray.png' for _ in range(0, n_images)]
        if self.envmap_def_mode == 'static':
            envmaps = ['default.hdr' for _ in range(0, n_images)]
        return envmaps

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
                "envmap_fname": envmaps[i] if len(envmaps) == len(cameras) else "none",
            }
            render_setups.append(render_setup)
        return render_setups

    def build_scenes(self):
        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Define Scenes')

        # Build scenes of for each part exclusively
        n_cameras = self.n_images
        n_lights = self.n_images
        n_envmaps = self.n_images

        for part in self.parts:
            cameras = self._sample_cameras(n_cameras)
            lights = self._sample_lights(n_lights)
            envmaps = self._assign_envmaps(n_envmaps)
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
            part["scene"] = scene

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f'Done in {tend}')

    # def export_augmented_metadata(self, filename: str = 'metadata', fileformats: list[str] = ['csv', 'xlsx']):
    #     if 'csv' in fileformats:
    #         self.metadata.to_csv(path_or_buf=f"{self.output_dir}/{filename}.csv")
    #     if 'xlsx' in fileformats:
    #         self.metadata.to_excel(excel_writer=f"{self.output_dir}/{filename}.xlsx")

    def export_rcfg_json(self, filename: str = 'rcfg.json'):
        tstart = timer_utils.time_now()
        rcfg_path = f'{self.output_dir}/{filename}'

        assert isinstance(filename, str)
        assert filename.endswith('.json')

        LOGGER.info(LOG_DELIM)
        LOGGER.info(f'Exporting rcfg [path={rcfg_path}]')

        # self.val_rcfg_json()
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
            {"parts": self.parts},
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
