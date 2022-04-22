""" Class model of a part."""
import logging

from preprocessing.models.single_part import SinglePart
from preprocessing.models.scene import Scene

LOGGER = logging.getLogger(__name__)


class Part:

    def __init__(
        self,
        id: str,
        name: str,
        hierarchy: str,
        is_spare: bool = False,
        single_parts: list[SinglePart] = [],
        scene: Scene = None,
    ):

        ## Validate parameters
        assert isinstance(id, str)
        assert isinstance(name, str)
        assert isinstance(hierarchy, str)
        assert isinstance(is_spare, bool)
        assert isinstance(single_parts, list)
        assert isinstance(scene, Scene) or scene is None

        ## Assign properties
        self.id = id
        self.name = name
        self.hierarchy = hierarchy
        self.single_parts = single_parts
        self.is_spare = is_spare
        self.scene = None

    def __eq__(self, other):
        if not isinstance(other, Part):
            return NotImplementedError

        return self.id == other.id

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str
