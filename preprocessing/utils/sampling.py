""" Sampling algorithms to use for generating random scenes """

import math
import random
from typing import Tuple
import numpy as np


def sphere_uniform(n_samples: int = 100, r_factor: float = 10.0, seed: int = 42) -> list:
    """ Returns a list of random points sampled on the unit sphere.
    
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
        r = r_factor * u**(1. / 3.)
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        points.append([x, y, z])
    return points


def sphere_equidistant(n_samples: int = 100, seed: int = 42) -> list:
    np.random.seed(seed)
    random.seed(seed)
    # TODO implement
    pass


def range_uniform(
        n_samples: int = 100,
        xrange: Tuple[float, float] = (-1.0, 1.0),
        yrange: Tuple[float, float] = (-1.0, 1.0),
        zrange: Tuple[float, float] = (-1.0, 1.0),
        seed: int = 42,
) -> 'np.ndarray':
    """ Return an array of points sampled on given ranges for each coordinate. 

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
