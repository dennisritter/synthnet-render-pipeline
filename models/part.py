""" Class model of a part."""
import logging

from models.single_part import SinglePart

LOGGER = logging.getLogger(__name__)


class Part:

    def __init__(
        self,
        id: str,
        name: str,
        hierarchy: str,
        is_spare: bool = False,
        single_parts: list = [],
        # cameras: list = [],
        # lights: list = [],
        # envmaps: list = [],
    ):

        ## Validate parameters
        assert isinstance(id, str)
        assert isinstance(name, str)
        assert isinstance(hierarchy, str)
        assert isinstance(is_spare, bool)
        assert isinstance(single_parts, list)
        # assert isinstance(cameras, list)
        # assert isinstance(lights, list)
        # assert isinstance(envmaps, list)

        ## Assign properties
        self.id = id
        self.name = name
        self.hierarchy = hierarchy
        self.is_spare = is_spare
        self.single_parts = single_parts
        # self.cameras = cameras
        # self.lights = lights
        # self.envmaps = envmaps

    def __eq__(self, other):
        if not isinstance(other, Part):
            return NotImplementedError
        return self.id == other.id