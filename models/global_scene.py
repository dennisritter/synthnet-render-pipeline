""" Class model of a single part. (A part that has no sub-parts)"""
import logging

LOGGER = logging.getLogger(__name__)


class GlobalScene:
    def __init__(
        self,
        cameras: list = [],
        lights: list = [],
    ):

        ## Validate parameters
        # Validate cameras
        assert isinstance(lights, list)
        # Validate lights
        assert isinstance(cameras, list)

        ## Assign properties
        self.cameras = cameras
        self.lights = lights

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str