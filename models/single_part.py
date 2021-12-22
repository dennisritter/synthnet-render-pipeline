""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""
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
