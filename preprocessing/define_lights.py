""" Functions for light definition """
from preprocessing.utils import sampling
from preprocessing.models.light import Light


def get_lights_range_uniform(n: int,
                             xrange=(-1.0, 1.0),
                             yrange=(-1.0, 1.0),
                             zrange=(1.0, 1.0),
                             seed: int = 42) -> list[Light]:
    """ Returns a list of lights with positions sampled from the given ranges.

        Args:
            n (int): Number of lights
            xrange (Tuple): Defines (min, max) range for axis
            yrange (Tuple): Defines (min, max) range for axis
            zrange (Tuple): Defines (min, max) range for axis
    """
    light_positions = sampling.range_uniform(
        n_samples=n,
        xrange=xrange,
        yrange=yrange,
        zrange=zrange,
        seed=seed,
    )
    return [Light(position=light_pos.tolist()) for light_pos in light_positions]


def get_lights_sphere_uniform(n: int, seed: int = 42) -> list[Light]:
    """ Returns a list of lights that were sampled on a sphere surface.

        Args:
            n (int): Number of lights to sample
    """
    light_positions = sampling.sphere_uniform(n_samples=n, seed=seed)
    return [Light(position=light_pos) for light_pos in light_positions]