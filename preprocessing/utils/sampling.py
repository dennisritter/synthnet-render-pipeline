""" Sampling algorithms to use for generating random scenes """

import math
import random
from typing import Tuple
import numpy as np
from numpy.core.fromnumeric import size


def sphere_uniform(n_samples=100):
    # TODO: Need object information to generate better zoom/pos
    """
    Generate random samples on the unit sphere
    :param number_of_samples:
    :return: points on unit sphere
    """
    points = []
    for i in range(n_samples):
        phi = random.uniform(0, 2 * math.pi)
        costheta = random.uniform(-1, 1)
        u = random.uniform(0, 1)
        theta = math.acos(costheta)
        r = 5 * u**(1. / 3.)  # 10 as radius
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        points.append([x, y, z])
    return points


def sphere_equidistant():
    # TODO implement
    pass


def range_uniform(
        n_samples: int = 100,
        xrange: Tuple[float, float] = (-1.0, 1.0),
        yrange: Tuple[float, float] = (-1.0, 1.0),
        zrange: Tuple[float, float] = (-1.0, 1.0),
):
    """ Return an array of points sampled on given ranges for each coordinate. 

        Args:
            n_samples (int): Number of samples
            xrange: min and max value for x coordinate
            yrange: min and max value for y coordinate
            zrange: min and max value for z coordinate
    """
    randx = np.random.uniform(low=xrange[0], high=xrange[1], size=(n_samples, 1))
    randy = np.random.uniform(low=yrange[0], high=yrange[1], size=(n_samples, 1))
    randz = np.random.uniform(low=zrange[0], high=zrange[1], size=(n_samples, 1))

    points = np.concatenate((randx, randy, randz), axis=1)
    return points
