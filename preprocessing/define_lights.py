""" Functions for light definition """
from preprocessing.utils import sampling
from models.light import Light
import numpy as np


def get_lights_range(
        n: int,
        xrange=(-1.0, 1.0),
        yrange=(-1.0, 1.0),
        zrange=(1.0, 1.0),
):
    light_positions = sampling.range_uniform(
        n_samples=n,
        xrange=xrange,
        yrange=yrange,
        zrange=zrange,
    )
    return [Light(position=light_pos.tolist()) for light_pos in light_positions]