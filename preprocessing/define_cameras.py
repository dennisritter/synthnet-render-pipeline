""" Functions for camera definition """
import numpy as np
import preprocessing.utils.sampling as sampling
from preprocessing.models.camera import Camera


def get_cameras_sphere_uniform(n: int) -> list[Camera]:
    """ Returns a list of cameras that were sampled on a sphere surface.

        Args:
            n (int): Number of cameras to sample
    """
    cam_positions = sampling.sphere_uniform(n)
    roll_angles = np.linspace(start=0, stop=90, num=n, endpoint=False)
    return [Camera(position=cam_pos, roll_angle=roll_angles[i]) for i, cam_pos in enumerate(cam_positions)]


def get_cameras_equidistant(n: int) -> list[Camera]:
    """ Returns a list of cameras that were sampled on a sphere surface and 
        share roughly the same distance to each their neighbours.
     
        Args:
            n (int): Number of cameras to sample
    """
    pass
    # TODO: Add preprocessing.utils.sampling.sphere_equidistant function


def get_cameras_importance(n: int) -> list[Camera]:
    pass
    # TODO: Sample cameras that show significant/important object information