""" Class model of a single part. (A part that has no sub-parts)"""
import logging
from preprocessing.models.camera import Camera
from preprocessing.models.light import Light

LOGGER = logging.getLogger(__name__)


class Scene:

    def __init__(
        self,
        cameras: list[Camera] = [],
        lights: list = [Light],
        envmaps: list = ["default.hdr"],
        render_setups: list = [],
    ):

        ## Validate parameters
        # Validate cameras
        assert isinstance(lights, list)
        # Validate lights
        assert isinstance(cameras, list)
        # Validate envmaps
        assert isinstance(envmaps, list)
        # Validate render_setups
        assert isinstance(render_setups, list)

        ## Assign properties
        self.cameras = cameras
        self.lights = lights
        self.envmaps = envmaps
        self.render_setups = render_setups

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str