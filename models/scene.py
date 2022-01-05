""" Class model of a single part. (A part that has no sub-parts)"""
import logging
from models.camera import Camera

LOGGER = logging.getLogger(__name__)


class Scene:
    def __init__(
        self,
        cameras: list = [],
        lights: list = [],
        envmaps: list = [],
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
        self.camera = cameras
        self.lights = lights
        self.envmap = envmaps
        self.render_setups = render_setups

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str