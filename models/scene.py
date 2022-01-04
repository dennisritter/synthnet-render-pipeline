""" Class model of a single part. (A part that has no sub-parts)"""
import logging
from models.camera import Camera

LOGGER = logging.getLogger(__name__)


class Scene:

    def __init__(
        self,
        camera,
        lights,
        envmap,
    ):

        ## Validate parameters
        # Validate cameras
        assert isinstance(lights, list)
        # Validate lights
        assert isinstance(camera, Camera)
        # Validate lights
        assert isinstance(envmap, str)

        ## Assign properties
        self.camera = camera
        self.lights = lights
        self.envmap = envmap

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str