""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""


class PreprocessingController:

    def __init__(
        self,
        metadata_file: str,
        blender_file: str,
        output_dir: str,
        n_images: int,
        camera_sampling: str,
        light_sampling: str,
        material_assign: str,
        environment_maps: str,
    ):
        self.metadata_file = metadata_file
        self.blender_file = blender_file
        self.output_dir = output_dir
        self.n_images = n_images
        self.camera_sampling = camera_sampling
        self.light_sampling = light_sampling
        self.material_assign = material_assign
        self.environment_maps = environment_maps
