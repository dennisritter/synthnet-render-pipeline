""" Functions for camera definition """
import numpy as np
import math
import preprocessing.utils.sampling as sampling
from preprocessing.models.camera import Camera


def get_cameras_sphere_uniform(n: int, seed: int) -> list[Camera]:
    """Returns a list of cameras that were sampled on a sphere surface.

    Args:
        n (int): Number of cameras to sample
    """
    cam_positions = sampling.sphere_uniform(n_samples=n, seed=seed)
    roll_angles = np.linspace(start=0.0, stop=math.radians(90), num=n, endpoint=False)
    return [
        Camera(position=cam_pos, local_rotation=[0.0, 0.0, roll_angles[i]]) for i, cam_pos in enumerate(cam_positions)
    ]


def get_cameras_sphere_equidistant(n: int, seed: int) -> list[Camera]:
    """Returns a list of cameras that were sampled on a sphere surface and
    share roughly the same distance to each their neighbours.

    Args:
        n (int): Number of cameras to sample
    """
    cam_positions = sampling.sphere_equidistant(n_samples=n, seed=seed)
    roll_angles = np.linspace(start=0.0, stop=math.radians(90), num=n, endpoint=False)
    return [
        Camera(position=cam_pos, local_rotation=[0.0, 0.0, roll_angles[i]]) for i, cam_pos in enumerate(cam_positions)
    ]


def get_cameras_circular(n: int) -> list[Camera]:
    """Returns a list of cameras equidistant to each other on a circle around the origin.
    They are elevated by 30 degrees.

    Args:
        n (int): Number of cameras to sample.

    Returns:
        list: List of sampled cameras.
    """
    cam_positions = sampling.circular(n_cameras=n, elev_angle=30)
    return [Camera(position=cam_pos.tolist()) for cam_pos in cam_positions]


def get_cameras_isocahedral(radius: float = 1.0, center: list[float] = [0.0, 0.0, 0.0]) -> list[Camera]:
    """Returns a list of cameras located on the 12 vertices of a regular isocahedron,
    with its center of mass being center.

    Args:
        radius (float): Radius of the isocahedron. Defaults to 1.
        center (float): Center of mass of the isocahedron. Defaults to [0., 0., 0.].

    Returns:
        list: List of sampled cameras.
    """
    cam_positions = sampling.isocahedral(radius=radius, center=center)
    return [Camera(position=cam_pos.tolist()) for cam_pos in cam_positions]


def get_cameras_dodecahedral(
    radius: float = 1.0, center: list[float] = [0.0, 0.0, 0.0], points_to_exclude: list = []
) -> np.ndarray:
    """Returns a list of cameras located on the 20 vertices of a regular dodecahedron,
    with its center of mass being center.

    Args:
        radius (float): Radius of the dodecahedron. Defaults to 1.
        center (float): Center of mass of the dodecahedron. Defaults to [0., 0., 0.].
        points_to_exclude (list, optional): List of integer indices of 0-19 vertices of this dodecahedron. These vertices are excluded from the result. Defaults to [].

    Returns:
        list: List of sampled cameras.
    """
    cam_positions = sampling.dodecahedral(radius=radius, center=center, points_to_exclude=points_to_exclude)
    return [Camera(position=cam_pos.tolist()) for cam_pos in cam_positions]


def get_cameras_dodecahedral_16(
    radius: float = 1.0, center: list[float] = [0.0, 0.0, 0.0], points_to_exclude: list = [11, 14, 16, 19]
) -> np.ndarray:
    """Returns a list of cameras located on 16 of the 20 vertices of a regular dodecahedron,
    with its center of mass being center.

    Args:
        radius (float): Radius of the dodecahedron. Defaults to 1.
        center (float): Center of mass of the dodecahedron. Defaults to [0., 0., 0.].
        points_to_exclude (list, optional): List of integer indices of 0-19 vertices of this dodecahedron. These vertices are excluded from the result. Defaults to [11, 14, 16, 19].

    Returns:
        list: List of sampled cameras.
    """
    cam_positions = sampling.dodecahedral(radius=radius, center=center, points_to_exclude=points_to_exclude)
    return [Camera(position=cam_pos.tolist()) for cam_pos in cam_positions]


def get_cameras_octagonal_antiprism(
    radius: float = 1.5, height: float = 2.0, center: list[float] = [0.0, 0.0, 0.0]
) -> np.ndarray:
    """Returns a list of cameras located on the 16 vertices of a uniform octagonal antiprism,
    with its center of mass being center.

    Args:
        radius (float): Radius of the antiprism. Defaults to 1.5
        height (float): Height of the antiprism. Defaults to 2.
        center (float): Center of mass of the antiprism. Defaults to [0., 0., 0.].

    Returns:
        list: List of sampled cameras.
    """
    cam_positions = sampling.n_gonal_antiprism(n_base_verts=8, radius=radius, height=height, center=center)
    return [Camera(position=cam_pos.tolist()) for cam_pos in cam_positions]


def get_cameras_n_agonal_antiprism(
    n_cameras: int, radius: float = 1.5, height: float = 2.0, center: list[float] = [0.0, 0.0, 0.0]
) -> np.ndarray:
    """Returns a list of cameras located on the ⌈n_cameras / 2⌉ vertices of a uniform n-gonal antiprism,
    with its center of mass being center.

    Args:
        n_cameras (int): Number of cameras to generate. If odd, n_cameras + 1 is used.
        radius (float): Radius of the antiprism. Defaults to 1.5
        height (float): Height of the antiprism. Defaults to 2.
        center (float): Center of mass of the antiprism. Defaults to [0., 0., 0.].

    Returns:
        list: List of sampled cameras.
    """
    n_base_verts = math.ceil(n_cameras / 2)
    cam_positions = sampling.n_gonal_antiprism(n_base_verts=n_base_verts, radius=radius, height=height, center=center)
    return [Camera(position=cam_pos.tolist()) for cam_pos in cam_positions]


def get_cameras_importance(n: int) -> list[Camera]:
    pass
    # TODO: Sample cameras that show significant/important object information
