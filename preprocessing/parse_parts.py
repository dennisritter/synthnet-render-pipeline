""" Identify all parts and their single parts """
import logging
import pandas as pd

from utils import timer_utils

LOGGER = logging.getLogger(__name__)


def parse_parts(metadata: 'pd.DataFrame'):
    tstart = timer_utils.time_now()
    LOGGER.info(f'\n')
    LOGGER.info(f'Parsing Metadata...')
    LOGGER.debug(f'{metadata.info()}')
    LOGGER.debug(f'{metadata.describe()}')

    # TODO ADD LOGIC

    tend = timer_utils.time_since(tstart)
    LOGGER.info(f'Done in {tend}')
