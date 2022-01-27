""" Class model of a single part. (A part that has no sub-parts)"""
import logging

LOGGER = logging.getLogger(__name__)

CAMERA_TYPES = ['persp', 'ortho', 'pano']


class Camera:

    def __init__(
        self,
        position: list,
        type_camera: str = 'persp',
        focal_length: float = 50.0,
        target: list = [0, 0, 0],
        local_rotation: list[float] = [0.0, 0.0, 0.0],
    ):

        ## Validate parameters
        # Validate position
        assert isinstance(position, list)
        assert len(position) == 3
        # Validate type
        assert isinstance(type_camera, str)
        assert type_camera.lower() in CAMERA_TYPES
        # Validate focal_length
        assert isinstance(focal_length, float)
        assert focal_length > 0
        # Validate target
        assert isinstance(target, list)
        assert len(target) == 3

        ## Assign properties
        self.position = position
        self.type_camera = type_camera
        self.focal_length = focal_length
        self.local_rotation = local_rotation
        self.target = target

    def __str__(self):
        result_str = f'{self.__class__}\n'
        for key, value in self.__dict__.items():
            result_str += f'    {str(key)}: {str(value)}\n'
        return result_str
