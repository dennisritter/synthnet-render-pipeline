""" Takes Metadata, blender file and configuration arguments to prepare a configuration file for GLTF-Scene-Exports of machine parts."""
import os
import logging
import pandas as pd

from preprocessing.utils import prepare_metadata
from preprocessing.parse_parts import parse_parts
from preprocessing import define_cameras, define_lights, define_materials, define_envmaps

LOGGER = logging.getLogger(__name__)


class Part:

    def __init__(
        self,
        id: str,
        name: str,
        hierarchy: str,
        is_spare: bool = False,
        single_parts: list = [],
        cameras: list = [],
        lights: list = [],
        envmaps: list = [],
    ):

        ## Validate parameters
        assert isinstance(id, str)
        assert isinstance(name, str)
        assert isinstance(hierarchy, str)
        assert isinstance(is_spare, bool)
        assert isinstance(single_parts, list)
        assert isinstance(cameras, list)
        assert isinstance(lights, list)
        assert isinstance(envmaps, list)

        ## Assign properties
        self.id = id
        self.name = name
        self.hierarchy = hierarchy
        self.is_spare = is_spare
        self.single_parts = single_parts
        self.cameras = cameras
        self.lights = lights
        self.envmaps = envmaps
