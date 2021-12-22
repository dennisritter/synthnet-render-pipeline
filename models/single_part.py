""" Class model of a single part. (A part that has no sub-parts)"""
import logging

LOGGER = logging.getLogger(__name__)


class SinglePart:

    def __init__(
        self,
        id: str,
        name: str,
        material: str = 'default',
    ):

        ## Validate parameters
        assert isinstance(id, str)
        assert isinstance(name, str)
        assert isinstance(material, str)

        ## Assign properties
        self.id = id
        self.name = name
        self.material = material

    def __eq__(self, other):
        if not isinstance(other, SinglePart):
            return NotImplementedError
        return self.id == other.id