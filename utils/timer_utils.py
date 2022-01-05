"""Contains code for displaying time."""

import math
import time


def time_now() -> float:
    """Method computes current time as seconds.

    Returns:
        time (float): Current time in seconds since Epoch.
    """
    return time.time()


def as_hms(seconds: float) -> str:
    """Converts seconds to hours mins seconds.

    Args:
        seconds (float): Seconds to convert to H M S.

    Returns:
        time (str): String representation of H M S.
    """
    minutes, sseconds = math.floor(seconds / 60), seconds % 60
    hours, minutes = math.floor(minutes / 60), minutes % 60
    return f"{hours:3}h {minutes:2}m {sseconds:5.2f}s"


def remaining(start_time: float, current_percent: float) -> str:
    """Computes remaining time.

    Args:
        start_time (float): Starting time in seconds.
        current_percent (float): Current percentage - range(0.0, 1.0).
    """
    now = time.time()
    elapsed_sec = now - start_time
    estimated_remaining_sec = (elapsed_sec / (current_percent)) - elapsed_sec
    return as_hms(estimated_remaining_sec)


def time_since(start_time: float) -> str:
    """Computes time (H M S) since given seconds and estimates remaining time.

    Args:
        start_time (float): Starting time in seconds.
        percent (float): Current percentage - range(0.0, 1.0)

    Returns:
        time (str): Time since start and estimated remaining time as str.
    """
    now = time.time()
    elapsed_sec = now - start_time
    return f"{as_hms(elapsed_sec)}"
