""" Class model of a single part. (A part that has no sub-parts)"""
import logging

LOGGER = logging.getLogger(__name__)

LIGHT_TYPES = ['point', 'sun', 'spot', 'area']


class Light:

    def __init__(
        self,
        position: list,
        type_light: str = 'point',
        intensity: int = 100,
        target: list = [0, 0, 0],
    ):

        ## Validate parameters
        # Validate position
        assert isinstance(position, list)
        assert len(position) == 3
        # Validate type
        assert isinstance(type_light, str)
        assert type_light.lower() in LIGHT_TYPES
        # Validate focal_length
        assert isinstance(intensity, int)
        assert intensity > 0
        # Validate target
        assert isinstance(target, list)
        assert len(target) == 3

        ## Assign properties
        self.position = position
        self.type_light = type_light
        self.intensity = intensity
        self.target = target

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str