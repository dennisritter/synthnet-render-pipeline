""" Sampling algorithms to use for generating random scenes """

import math
import random
from typing import Tuple
import numpy as np


def sphere_uniform(
    n_samples: int = 100,
    r_factor: float = 10.0,
    seed: int = 42,
) -> list[list]:
    """Returns a list of random points sampled on the unit sphere.

    Args:
        n_samples (int): Number of points to sample.
        r_factor (float): Radius factor to control the distance of objects to the sphere center.
    """
    np.random.seed(seed)
    random.seed(seed)
    points = []
    for i in range(n_samples):
        phi = random.uniform(0, 2 * math.pi)
        costheta = random.uniform(-1, 1)
        u = random.uniform(0, 1)
        theta = math.acos(costheta)
        r = r_factor * u ** (1.0 / 3.0)
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        points.append([x, y, z])
    return points


def sphere_equidistant(
    n_samples: int = 100,
    r_factor=1.0,
    seed: int = 42,
) -> list[list]:
    """Returns a list of regularly sampled points on the unit sphere using fibonacci lattice/ golden spiral
    Args:
        n_samples (int): Number of points to sample.. Defaults to 100.
        r_factor (float): Radius factor to control the distance of objects to the sphere center.
    Returns:
        list: list of sampled points
    """
    np.random.seed(seed)
    random.seed(seed)
    points = []
    # golden angle 3d
    phi = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n_samples):
        # golden angle increment
        theta = phi * i
        # y goes from 1 to -1
        y = 1 - (i / float(n_samples - 1)) * 2 if n_samples > 1 else 0
        # radius at y
        r = math.sqrt(1 - y * y)
        x = r * math.cos(theta)
        z = r * math.sin(theta)
        points.append([x * r_factor, y * r_factor, z * r_factor])
    return points


def range_uniform(
    n_samples: int = 100,
    xrange: Tuple[float, float] = (-1.0, 1.0),
    yrange: Tuple[float, float] = (-1.0, 1.0),
    zrange: Tuple[float, float] = (-1.0, 1.0),
    seed: int = 42,
) -> "np.ndarray":
    """Return an array of points sampled on given ranges for each coordinate.

    Args:
        n_samples (int): Number of samples
        xrange (Tuple): min and max value for axis
        yrange (Tuple): min and max value for axis
        zrange (Tuple): min and max value for axis
    """
    np.random.seed(seed)
    random.seed(seed)
    randx = np.random.uniform(low=xrange[0], high=xrange[1], size=(n_samples, 1))
    randy = np.random.uniform(low=yrange[0], high=yrange[1], size=(n_samples, 1))
    randz = np.random.uniform(low=zrange[0], high=zrange[1], size=(n_samples, 1))

    points = np.concatenate((randx, randy, randz), axis=1)
    return points


def cartesian_to_spherical(point_cart: list) -> tuple[float, float, float]:
    """Converts a cartesian 3D point to spherical notation
    See http://www.vias.org/comp_geometry/math_coord_convert_3d.htm

    Args:
        point_cart (list): cartesian 3D point in the form of a list, meaning [x, y, z]

    Returns:
        float, float, float: point converted to spherical notation, meaning (azimuth, inclination, radius)
    """
    x, y, z = point_cart
    r = math.sqrt(x**2 + y**2 + z**2)
    theta = math.acos(z / r)
    phi = math.atan2(y, x)
    return theta, phi, r


def spherical_to_cartesian(
    theta: float,
    phi: float,
    r: float,
) -> list[float, float, float]:
    """Converts a 3D point in spherical notation to cartesian
    See http://www.vias.org/comp_geometry/math_coord_convert_3d.htm

    Args:
        theta (float): azimuth
        phi (float): inclination
        r (float): radius

    Returns:
        list: cartesian point represented as a list [x, y, z]
    """
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    return [x, y, z]


def move_spherical_by_deg_angle(
    theta: float,
    phi: float,
    r: float,
    angle: float,
) -> tuple[float, float, float]:
    """Function rotates a point in spherical notation (azimuth, inclination, radius) counterclockwise
    by subtracting a given angle from the azimuth.

    Args:
        theta (float): azimuth
        phi (float): inclination
        r (float): radius
        angle (float): angle to rotate the point by

    Returns:
        float, float, float: rotated point in spherical notation, meaning (azimuth, inclination, radius)
    """
    rad_angle = math.radians(angle)
    return theta - rad_angle, phi, r


def point_2D_on_circle(
    angle: float,
    radius: float,
) -> tuple[float, float]:
    """Get the position of a point on a circle around the origin rotated by the given angle angle.

    Args:
        angle (float): angle by which the point is rotated
        radius (float): distance between the point and the origin

    Returns:
        tuple: new point, meaning (x, y)
    """
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return x, y


def add_points(
    p1: list[float, float, float],
    p2: list[float, float, float],
) -> list[float, float, float]:
    """Add to 3D points, represented as lists in order of [x, y, z], together and return the resulting point.

    Args:
        p1 (list): Point 1.
        p2 (list): Point 2.

    Returns:
        list: Resulting 3D point.
    """
    return [p1[i] + p2[i] for i in range(len(p1))]


def scale_point(p: list, factor: float) -> list:
    """Scale a point p by factor factor"""
    return [p[i] * factor for i in range(len(p))]


def circular(
    n_cameras: int,
    elev_angle: float,
    radius: float = 1.0,
    center: list[float] = [0.0, 0.0, 0.0],
) -> np.ndarray:
    """Function returns n_camera many 3D points, which are evenly spaced around the origin with a distance of radius
    and elevated by elev_angle degrees in z direction.
    See https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9947327

    Args:
        n_cameras (int): Number of cameras, meaning points, to arange around the origin
        elev_angle (float): angle to elevate the points by in degrees. 0 for no elevation.
        radius (float, optional): Distance from the origin to the points. Defaults to 1.
        center (list, optional): List representing a point to be the center, meaning [x, y, z]. Defaults to [0., 0., 0.].

    Returns:
        np.ndarray: array containing the points
    """
    # Slicing the circle in n_cameras parts for even spacing
    theta = 2 * math.pi / n_cameras
    points = []
    for i in range(n_cameras):
        # Calculate point on circular orbit for camera i
        x, y = point_2D_on_circle(theta * i, radius)
        z = 0.0
        p = [x, y, z]
        # Convert the point to spherical notation, rotate by elev_angle and convert back to cartesian
        sph_theta, sph_phi, sph_r = cartesian_to_spherical(p)
        sph_theta, sph_phi, sph_r = move_spherical_by_deg_angle(sph_theta, sph_phi, sph_r, elev_angle)
        p_cart = spherical_to_cartesian(sph_theta, sph_phi, sph_r)
        p_cart = add_points(p_cart, center)
        points.append(p_cart)
    return np.array(points)


def isocahedral(
    radius: float = 1.0,
    center: list[float] = [0.0, 0.0, 0.0],
) -> np.ndarray:
    """Function calculates the 12 vertices, meaning corners, of a regular isocahedron. Its center of mass is "center",
    its radius is r and two of the faces are parallel to the x-y plane.

    Args:
        radius (int, optional): Scaling factor. Defaults to 1.
        center (list, optional): List representing a point to be the center, meaning [x, y, z]. Defaults to [0., 0., 0.].

    Returns:
        np.ndarray: array containing the points
    """
    phi = (1 + 5**0.5) / 2  # Golden ratio

    # Source of coordinates: https://en.wikipedia.org/wiki/Regular_icosahedron#Cartesian_coordinates
    unit_coordinates = [
        [0, 1, phi],
        [0, -1, phi],
        [0, 1, -phi],
        [0, -1, -phi],
        [1, phi, 0],
        [-1, phi, 0],
        [1, -phi, 0],
        [-1, -phi, 0],
        [phi, 0, 1],
        [-phi, 0, 1],
        [phi, 0, -1],
        [-phi, 0, -1],
    ]

    for i in range(len(unit_coordinates)):
        coord = unit_coordinates[i]
        coord = scale_point(coord, radius)
        coord = add_points(coord, center)
        unit_coordinates[i] = coord
    return np.array(unit_coordinates)


def dodecahedral(
    radius: float = 1.0,
    center: list[float] = [0.0, 0.0, 0.0],
    points_to_exclude: list[int] = [],
) -> np.ndarray:
    """Function calculates the 20 vertices, meaning corners, of a regular dodecahedron. Its center of mass is "center",
    its radius is r and two of the faces are parallel to the x-y plane.

    Visualization of vertex indices, top down view, meaning in -z direction. Use these to identify which cameras to exlude if needed. (cannot exclude all/point at 0)
        ------------------------------------------------------------------------------------------>
        x         ,'. 7         y|          , - ~ 15 ~ - ,
                ,'   `.          |      16                 14
              ,'       `.        |    ,   `-. 3 _____ 2 .-'   ,
            8 \ bottom  / 6      |  17         /     \         13
               \       /         |  ,         /       \         ,
                \_____/          |  ,        /   top   \        ,
               9       5         |  18 .-' 4 `.       ,' 1 `-. 12
                                 |   ,         `.   ,'         ,
                                 |    ,          '.' 0        ,
                                 |     19         |        11'
                                 \/       ' - , _ 10 _ , '

    ASCII-Art based on: https://ascii.co.uk/art/

    Args:
        radius (int, optional): Scaling factor. Defaults to 1.
        center (list, optional): List representing a point to be the center, meaning [x, y, z]. Defaults to [0., 0., 0.].
        points_to_exclude (list, optional): List of integer indices of 0-19 vertices of this dodecahedron. These vertices are excluded from the result. Defaults to [].

    Returns:
        np.ndarray: Array containing the points
    """
    assert all(
        [item > 0 and item < 20 for item in points_to_exclude]
    ), f"Cannot exclude one or more points in the points_to_exclude list: {points_to_exclude}"

    phi = (1 + 5**0.5) / 2  # Golden ratio

    # Source of coordinates: https://en.wikipedia.org/wiki/Regular_dodecahedron#Cartesian_coordinates
    unit_coordinates = [
        [0, 1 / phi, phi],  # 0
        [0, -1 / phi, phi],  # 1
        [-1, -1, 1],  # 2
        [-phi, 0, 1 / phi],  # 3
        [-1, 1, 1],  # 4
        [phi, 0, -1 / phi],  # 5
        [1, -1, -1],  # 6
        [0, -1 / phi, -phi],  # 7
        [0, 1 / phi, -phi],  # 8
        [1, 1, -1],  # 9
        [1, 1, 1],  # 10
        [phi, 0, 1 / phi],  # 11
        [1, -1, 1],  # 12
        [1 / phi, -phi, 0],  # 13
        [-1 / phi, -phi, 0],  # 14
        [-1, -1, -1],  # 15
        [-phi, 0, -1 / phi],  # 16
        [-1, 1, -1],  # 17
        [-1 / phi, phi, 0],  # 18
        [1 / phi, phi, 0],  # 19
    ]
    # Remove unwanted points
    for idx in sorted(points_to_exclude, reverse=True):
        del unit_coordinates[idx]

    # Supplied coordinates do not have the top and bottom face parallel with the x-y plane
    # First rotate around the y axis, resulting in two faces being parallel
    theta = math.atan(1 / phi)
    rotation_y = np.array(
        [
            [math.cos(theta), 0, math.sin(theta), 0],
            [0, 1, 0, 0],
            [-math.sin(theta), 0, math.cos(theta), 0],
            [0, 0, 0, 1],
        ]
    )

    y_rotated_coords = []
    for c in unit_coordinates:
        c_ = np.array([c[0], c[1], c[2], 1])
        c_ = np.matmul(rotation_y, c_)
        y_rotated_coords.append(c_[:3])

    # Get the 5 corners, which have the highest z value, meaning they make up the top face.
    # Then take the corner farthest in y direction and convert it to spherical coordinates.
    top_5_in_z_dir = sorted(y_rotated_coords, key=lambda p: p[2], reverse=True)[:5]
    top_1_in_y_dir = sorted(top_5_in_z_dir, key=lambda p: p[1], reverse=True)[0]
    theta_top1, _, _ = cartesian_to_spherical(top_1_in_y_dir)

    # Use the azimuth angle of the spherical point, which indicates how much it has been rotated from 0 degrees.
    # We want to rotate firsty back to 0 degrees and then to 90 degrees to align the dodecahedron
    z_ang = theta_top1 - math.pi / 2
    rotation_z = np.array(
        [
            [math.cos(-z_ang), -math.sin(-z_ang), 0, 0],
            [math.sin(-z_ang), math.cos(-z_ang), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )

    z_rotated_coords = []
    for c in y_rotated_coords:
        c_ = np.array([c[0], c[1], c[2], 1])
        c_ = np.matmul(rotation_z, c_)
        z_rotated_coords.append(c_[:3])

    unit_coordinates = z_rotated_coords

    for i in range(len(unit_coordinates)):
        coord = unit_coordinates[i]
        coord = scale_point(coord, radius)
        coord = add_points(coord, center)
        unit_coordinates[i] = coord
    return np.array(unit_coordinates)


def n_gonal_antiprism(
    n_base_verts: int,
    radius: float = 1.0,
    height: float = 1.0,
    center: list[float] = [0.0, 0.0, 0.0],
) -> np.ndarray:
    """Function calculates the n_base_verts*2 vertices of a uniform n-gonal antiprism. Its radius is radius and its heigth is height.
    The n-gonal faces are parallel with the x-y plane.
    See https://en.wikipedia.org/wiki/Antiprism

    Args:
        n_base_verts (int): Used to construct the n-gonal polygons used as top and bottom cap. Has to be >= 2.
        radius (float, optional): The radius, meaning the distance between any point and the origin. Defaults to 1.0.
        height (float, optional): The height, meaning the distance between both octagonal faces. Defaults to 1.0.
        center (list, optional): List representing a point to be the center, meaning [x, y, z]. Defaults to [0., 0., 0.].

    Returns:
        np.ndarray: array containing the points
    """
    assert n_base_verts >= 2, f"Function cannot construct an n-gon with {n_base_verts} vertices, has to be >= 2"
    # Slicing the circle in 8 parts for even spacing
    angle = 2 * math.pi / n_base_verts
    points = []
    # For each iteration, calculate a point on the top n-gon and the bottom n-gon.
    # The point on the bottom n-gon is shifted by angle / 2, resulting in triangular faces
    for i in range(n_base_verts):
        top_angle = angle * i
        t_x, t_y = point_2D_on_circle(top_angle, radius)
        t_p = [t_x, t_y, height / 2]
        t_p = add_points(t_p, center)

        bottom_angle = top_angle + angle / 2
        b_x, b_y = point_2D_on_circle(bottom_angle, radius)
        b_p = [b_x, b_y, -height / 2]
        b_p = add_points(b_p, center)

        points.extend([t_p, b_p])
    return np.array(points)
