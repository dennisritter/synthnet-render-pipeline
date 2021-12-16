""" Sampling algorithms to use for generating random scenes """

import math
import random

def sphere_sampling(number_of_samples=100):
    """
    Generate random samples on the unit sphere
    :param number_of_samples:
    :return: points on unit sphere
    """
    points = []
    for i in range(number_of_samples):
        phi = random.uniform(0, 2*math.pi)
        costheta = random.uniform(-1, 1)
        u = random.uniform(0, 1)
        theta = math.acos(costheta)
        r = 1 * u ** (1./3.)  # 1 as radius
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        points.append([x, y, z])
    return points