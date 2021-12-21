""" Identify all parts and their single parts """
import logging
import pandas as pd

from utils import timer_utils

LOGGER = logging.getLogger(__name__)


# TODO: Return whole part object instead of id only
def get_single_parts(metadata: 'pd.DataFrame', parent_part):
    """ Recursively iterates over children of the given parent_part until parent_part is a 
        single_part (has no child parts). Returns a list of the parent_parts' "single part children ids" 
        or the "parent_part id" itself if parent_part is a single_part already.  
    
    """
    single_parts = []
    subparts = metadata.loc[metadata['part_hierarchy'].str.startswith(
        parent_part['part_hierarchy'] + '.')]

    if len(subparts) == 0:
        parent_part_id = parent_part["part_id"]
        if parent_part_id not in single_parts:
            single_parts.append(parent_part_id)
    else:
        for _, sp in subparts.iterrows():
            sp_children = get_single_parts(metadata, sp)
            for child in sp_children:
                if child not in single_parts:
                    single_parts.append(child)

    LOGGER.debug(f'PARENT: {parent_part["part_id"]}')
    LOGGER.debug(f'N_SUBPARTS:{len(single_parts)}')
    LOGGER.debug(f'N_SINGLE_PARTS:{len(single_parts)}')
    LOGGER.debug(f'SINGLE_PARTS: {single_parts}')
    LOGGER.debug('- ' * 10)
    return single_parts


def parse_parts(metadata: 'pd.DataFrame'):
    """ Returns all parts and included single part ids (unique)
        
        Args:
            metadata (pandas.DataFrame):
                A Pandas DataFrame containing cols [part_id, part_name, part_hierarchy, 
                part_material, part_is_spare]. Each row represents a part.

    """
    tstart = timer_utils.time_now()
    LOGGER.info('\n')
    LOGGER.info('Parsing Metadata...')
    LOGGER.debug(f'{metadata.info()}')
    LOGGER.debug(f'{metadata.describe()}')

    # part_ids = metadata.loc[:, 'part_id']
    part_template = {
        "part_id": '',
        "part_name": '',
        "part_hierarchy": '',
        "part_is_spare": False,
        "single_parts": [],
        "cameras": [],
        "lights": []
    }
    sp_template = {
        "part_id": '',
        "part_name": '',
        "material": '',
    }
    part_objs = []
    part_ids = []
    single_parts = []
    for i, row in metadata.iterrows():
        part_id = row['part_id']
        part_name = row['part_name']
        part_hierarchy = row['part_hierarchy']
        part_is_spare = row['part_is_spare']

        # The part is already stored, skip it.
        if part_id in part_ids:
            continue

        part_ids.append(part_id)

        LOGGER.debug('# ' * 10)
        LOGGER.debug(f'# Single parts for: {row["part_id"]}')
        LOGGER.debug('# ' * 10)
        single_parts.append(get_single_parts(metadata, row))

        part_obj = part_template
        part_obj["part_id"] = part_id
        part_obj["part_name"] = part_name
        part_obj["part_hierarchy"] = part_hierarchy
        part_obj["part_is_spare"] = part_is_spare
        for single_part in single_parts:
            sp_obj = sp_template
            sp_obj["part_id"] = single_part["part_id"]
            sp_obj["part_name"] = single_part["part_name"]
            sp_obj["part_material"] = single_part["part_material"]
            part_obj["single_parts"].append(sp_obj)

    tend = timer_utils.time_since(tstart)
    LOGGER.info(f'Done in {tend}')
