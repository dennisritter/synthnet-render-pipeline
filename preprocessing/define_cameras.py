""" Functions for camera definition """
import preprocessing.utils.sampling as sampling
from models.camera import Camera


def get_cameras_sphere_uniform(n: int):
    cam_positions = sampling.sphere_uniform(n)
    return [Camera(position=cam_pos) for cam_pos in cam_positions]


def get_cameras_equidistant(n: int):
    pass
    # TODO: Add preprocessing.utils.sampling.sphere_equidistant function