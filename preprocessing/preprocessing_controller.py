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
LOG_DELIM = "- " * 20

RCFG_VAL_SCHEMA_FILE_TOPEX = "./validation/schemas/rcfg_schema_topex.json"
RCFG_VAL_SCHEMA_FILE_OBJ = "./validation/schemas/rcfg_schema_obj.json"


class PreprocessingController:
    CAMERA_DEF_MODES = [
        "sphere-uniform",
        "sphere-equidistant",
        "circular",
        "isocahedral",
        "dodecahedral",
        "dodecahedral-16",
        "n-gonal-antiprism",
    ]
    LIGHT_DEF_MODES = ["sphere-uniform", "range-uniform"]
    MATERIAL_DEF_MODES = ["disabled", "static", "random"]
    ENVMAP_DEF_MODES = ["disabled", "white", "gray", "static"]

    def __init__(
        self,
        metadata_file: str,
        blend_file: str,
        materials_dir: str,
        obj_dir: str,
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
        assert (metadata_file and blend_file) or obj_dir, "Either metadata_file and blend_file or obj_dir must be set"
        if metadata_file and blend_file:
            # validate metadata_file
            assert isinstance(metadata_file, str)
            assert os.path.isfile(metadata_file)
            # validate blend_file
            assert isinstance(blend_file, str)
            assert os.path.isfile(blend_file)
        if materials_dir:
            # validate materials_dir
            assert isinstance(materials_dir, str)
            assert os.path.isdir(materials_dir)
        if obj_dir:
            # validate output_dir
            assert isinstance(obj_dir, str)
            assert os.path.isdir(obj_dir)
        assert isinstance(output_dir, str)
        os.makedirs(output_dir, exist_ok=True)
        assert os.path.exists(output_dir)
        # validate n_images
        assert isinstance(n_images, int)
        assert n_images > 0
        # validate camera_def_mode
        assert isinstance(camera_def_mode, str)
        assert camera_def_mode.lower() in self.CAMERA_DEF_MODES
        if camera_def_mode == "isocahedral":
            if n_images != 12:
                LOGGER.warn(
                    f"{n_images=} were entered, but in {camera_def_mode=} n_images is fixed to 12. Setting n_images to 12."
                )
                n_images = 12
        if camera_def_mode == "dodecahedral-16":
            if n_images != 16:
                LOGGER.warn(
                    f"{n_images=} were entered, but in {camera_def_mode=} n_images is fixed to 16. Setting n_images to 16."
                )
                n_images = 16
        if camera_def_mode == "dodecahedral":
            if n_images != 20:
                LOGGER.warn(
                    f"{n_images=} were entered, but in {camera_def_mode=} n_images is fixed to 20. Setting n_images to 20."
                )
            n_images = 20
        if camera_def_mode == "n-gonal-antiprism":
            if n_images % 2 != 0:
                LOGGER.warn(
                    f"With camera_def_mode {camera_def_mode}, an even value is needed for the value of images per part {n_images}. n_images={n_images + 1} is set instead."
                )
                n_images += 1
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
        self.materials_dir = materials_dir
        self.obj_dir = obj_dir
        self.output_dir = output_dir
        self.n_images = n_images
        self.camera_def_mode = camera_def_mode.lower()
        self.light_def_mode = light_def_mode.lower()
        self.material_def_mode = material_def_mode.lower()
        self.envmap_def_mode = envmap_def_mode.lower()
        self.camera_seed = camera_seed
        self.light_seed = light_seed

        # Topex: Prepare Metadata and get Machine parts
        if self.metadata_file and blend_file:
            self.rcfg_val_schema_file = RCFG_VAL_SCHEMA_FILE_TOPEX
            # Prepared metadata.xlsx file as pandas DataFrame
            # rows: parts
            # cols: part_id, part_name, part_hierarchy, part_material, part_is_spare
            self.metadata = prepare_metadata(metadata_file)

            # A scene described by Cameras, Lights and envmaps and render_setups, that is used for
            # all parts
            self.global_scene = None

            # Parse Parts
            tstart = timer_utils.time_now()
            LOGGER.info(LOG_DELIM)
            LOGGER.info(f"Parsing unique Parts and SingleParts from {metadata_file}")
            # List of all Parts to render
            self.parts = parse_parts(self.metadata)
            tend = timer_utils.time_since(tstart)
            LOGGER.info(f"Done in {tend}")

        # OBJ files: Parse directory structure
        # Structure is expected to be:
        #   - obj_dir/{split}/{label}/{obj_file}
        elif obj_dir:
            self.rcfg_val_schema_file = RCFG_VAL_SCHEMA_FILE_OBJ
            LOGGER.info(LOG_DELIM)
            LOGGER.info(f"Parsing OBJ files from directory: {self.obj_dir}")
            self.parts = []
            for split in os.listdir(f"{self.obj_dir}"):
                for label in os.listdir(f"{self.obj_dir}/{split}"):
                    render_samples = os.listdir(f"{self.obj_dir}/{split}/{label}")
                    for obj_file in render_samples:
                        if obj_file.endswith(".obj"):
                            part = {
                                "id": f'{split}_{obj_file.split(".")[0]}',
                                "path": f"{self.obj_dir}/{split}/{label}/{obj_file}",
                                "scene": None,
                            }
                            self.parts.append(part)

    def assign_materials(self):
        """Assign materials to single parts depending on self.material_def_mode."""

        tstart = timer_utils.time_now()
        LOGGER.info(LOG_DELIM)
        LOGGER.info(f"Assigning materials [mode={self.material_def_mode}]")

        # disabled: Do not add any materials (but 'none')
        if self.material_def_mode == "disabled":
            pass
        # static: Read metadata materials and apply our materials depending
        # on a static metadata_material:our_material map
        if self.material_def_mode == "static":
            self.parts = define_materials.assign_materials_static(
                self.parts,
                self.metadata,
                self.materials_dir,
            )
        # random: Assign a random material to each part
        if self.material_def_mode == "random":
            self.parts = define_materials.assign_materials_random(
                self.parts,
                self.metadata,
                self.materials_dir,
            )

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f"Done in {tend}")

    def _sample_cameras(self, n_images: int):
        """Assign Cameras to single parts depending on self.camera-def_mode."""
        # Add cameras - sphere uniform
        if self.camera_def_mode == "sphere-uniform":
            cameras = define_cameras.get_cameras_sphere_uniform(n=n_images, seed=self.camera_seed)
        if self.camera_def_mode == "sphere-equidistant":
            cameras = define_cameras.get_cameras_sphere_equidistant(n=n_images, seed=self.camera_seed)
        if self.camera_def_mode == "circular":
            cameras = define_cameras.get_cameras_circular(n=n_images)
        if self.camera_def_mode == "isocahedral":
            cameras = define_cameras.get_cameras_isocahedral()
        if self.camera_def_mode == "dodecahedral":
            cameras = define_cameras.get_cameras_dodecahedral()
        if self.camera_def_mode == "dodecahedral-16":
            cameras = define_cameras.get_cameras_dodecahedral_16()
        if self.camera_def_mode == "n-gonal-antiprism":
            cameras = define_cameras.get_cameras_n_agonal_antiprism(n_cameras=n_images)

        return cameras

    def _sample_lights(self, n_images: int):
        """Sample lightsetups depending on self.light_def_mode."""
        # Add lights - sphere uniform
        if self.light_def_mode == "sphere-uniform":
            lights = define_lights.get_lights_sphere_uniform(n=n_images, seed=self.light_seed)
        # Add lights - random within range
        if self.light_def_mode == "range-uniform":
            lights = define_lights.get_lights_range_uniform(n=n_images, seed=self.light_seed)
        return lights

    def _assign_envmaps(self, n_images: int):
        """Assign Environment Maps to single parts depending on self.envmap_def_mode."""
        # No envmaps
        if self.envmap_def_mode == "disabled":
            envmaps = []
        if self.envmap_def_mode == "white":
            envmaps = ["white.jpg" for _ in range(0, n_images)]
        if self.envmap_def_mode == "gray":
            envmaps = ["gray.png" for _ in range(0, n_images)]
        if self.envmap_def_mode == "static":
            envmaps = ["default.hdr" for _ in range(0, n_images)]
        return envmaps

    def _compose_render_setups(self, cameras: list, lights: list, envmaps: list):
        """Compose Render Setups from lists of cameras, lights and envmaps.

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
        LOGGER.info(f"Define Scenes")

        # Build scenes of for each part exclusively
        # self.n_images is equal to the number of cameras, lights and envmaps needed
        for part in self.parts:
            cameras = self._sample_cameras(self.n_images)
            lights = self._sample_lights(self.n_images)
            envmaps = self._assign_envmaps(self.n_images)
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
            if type(part) is dict:
                part["scene"] = scene
            else:
                part.scene = scene

        tend = timer_utils.time_since(tstart)
        LOGGER.info(f"Done in {tend}")

    def export_augmented_metadata(self, filename: str = "metadata", fileformats: list[str] = ["csv", "xlsx"]):
        if "csv" in fileformats:
            self.metadata.to_csv(path_or_buf=f"{self.output_dir}/{filename}.csv")
        if "xlsx" in fileformats:
            self.metadata.to_excel(excel_writer=f"{self.output_dir}/{filename}.xlsx")

    def export_rcfg_json(self, filename: str = "rcfg.json"):
        tstart = timer_utils.time_now()
        rcfg_path = f"{self.output_dir}/{filename}"

        assert isinstance(filename, str)
        assert filename.endswith(".json")

        LOGGER.info(LOG_DELIM)
        LOGGER.info(f"Exporting rcfg [path={rcfg_path}]")

        self.val_rcfg_json()
        rcfg = json.loads(self.get_rcfg_json())
        with open(f"{self.output_dir}/{filename}", "w") as f:
            json.dump(
                rcfg,
                f,
                default=lambda o: o.__dict__,
                indent=4,
                sort_keys=True,
            )
        tend = timer_utils.time_since(tstart)
        LOGGER.info(f"Done in {tend}")

    def get_rcfg_json(self):
        return json.dumps(
            {"parts": self.parts},
            default=lambda o: o.__dict__,
            indent=4,
            sort_keys=True,
        )

    def val_rcfg_json(self):
        with open(self.rcfg_val_schema_file, "r", encoding="UTF-8") as json_file:
            rcfg_schema = json.loads(json_file.read())
        rcfg = self.get_rcfg_json()
        try:
            jsonschema.validate(
                instance=json.loads(rcfg),
                schema=rcfg_schema,
            )
        except jsonschema.exceptions.ValidationError as err:
            LOGGER.error("Schema validation Error:", err)

        except jsonschema.exceptions.SchemaError as err:
            LOGGER.error("Schema Error:", err)
