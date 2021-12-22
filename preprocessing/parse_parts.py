""" Identify all parts and their single parts """
import logging
import pandas as pd

from utils import timer_utils

LOGGER = logging.getLogger(__name__)


# TODO: Return whole part object instead of id only
def get_single_parts(metadata: 'pd.DataFrame', parent_part):
    """ Recursively iterates over children of the given parent_part until parent_part is a 
        single_part (has no child parts). Returns a list of the parent_parts' single_part children 
        or the parent_part itself if parent_part is a single_part already.  

        Args:
            metadata (pandas.DataFrame):
                A Pandas DataFrame containing cols [part_id, part_name, part_hierarchy, 
                part_material, part_is_spare]. Each row represents a part.
            parent_part (dict): The part to identify included single_parts for.
    
    """
    # All single_parts of parent_part are going to be stored here
    single_parts = []

    # Hierarchy Example: '1.2.5'
    # Every part that starts with the same hierarchy as parent_part and continue with a '.' are direct subparts of parent_part
    subparts = metadata.loc[metadata['part_hierarchy'].str.startswith(parent_part['part_hierarchy'] + '.')]

    # If parent_part has noch subparts, it is a single part itself
    # so add it to the single_parts list if it is not added already
    if len(subparts) == 0:
        parent_part_id = parent_part["part_id"]
        single_part_ids = [sp["part_id"] for sp in single_parts]
        if parent_part_id not in single_part_ids:
            single_parts.append(parent_part)
    # If paren_part has subparts, determine their subparts by calling this function again
    # with subpart being the new parent_part
    else:
        for _, subpart in subparts.iterrows():
            subpart_children = get_single_parts(metadata, parent_part=subpart)
            for child in subpart_children:
                child_id = child["part_id"]
                single_part_ids = [sp["part_id"] for sp in single_parts]
                if child_id not in single_part_ids:
                    single_parts.append(child)

    LOGGER.debug(f'PARENT: {parent_part["part_id"]}')
    LOGGER.debug(f'N_SUBPARTS:{len(single_parts)}')
    LOGGER.debug(f'N_SINGLE_PARTS:{len(single_parts)}')
    LOGGER.debug(f'SINGLE_PARTS: {single_parts}')
    LOGGER.debug('- ' * 10)
    return single_parts


def parse_parts(metadata: 'pd.DataFrame'):
    """ Returns all parts and included single part ids (unique) as a list of dictionaries.

        - Each part is added only once (no duplicates)
        - Each single_part of a part is added only once (no duplicates)
        
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

    part_template = {
        "part_id": '',
        "part_name": '',
        "part_hierarchy": '',
        "part_is_spare": False,
        "single_parts": [],
        "cameras": [],
        "lights": [],
        "envmaps": [],
    }
    sp_template = {
        "part_id": '',
        "part_name": '',
        "part_material": '',
    }
    part_objs = []
    part_ids = []
    part_duplicate_ids = []
    for i, row in metadata.iterrows():
        part_id = row['part_id']
        part_name = row['part_name']
        part_hierarchy = row['part_hierarchy']
        part_is_spare = row['part_is_spare']

        # The part is already stored, skip it.
        if part_id in part_ids:
            part_duplicate_ids.append(part_id)
            continue
        part_ids.append(part_id)

        LOGGER.debug('# ' * 10)
        LOGGER.debug(f'# Single parts for: {row["part_id"]}')
        LOGGER.debug('# ' * 10)
        single_parts = get_single_parts(metadata, row)

        part_obj = part_template
        print(part_template)
        part_obj["part_id"] = part_id
        part_obj["part_name"] = part_name
        part_obj["part_hierarchy"] = part_hierarchy
        part_obj["part_is_spare"] = part_is_spare
        # print(part_obj)
        for single_part in single_parts:
            sp_obj = sp_template
            sp_obj["part_id"] = single_part["part_id"]
            sp_obj["part_name"] = single_part["part_name"]
            sp_obj["part_material"] = single_part["part_material"]
            part_obj["single_parts"].append(sp_obj)
        part_objs.append(part_obj)

    tend = timer_utils.time_since(tstart)
    LOGGER.info(f'--Returning {len(part_objs)} part_objs')
    LOGGER.info(f'--Ignoring {len(part_duplicate_ids)} duplicates')
    LOGGER.debug('--Part Duplicate IDs')
    LOGGER.debug(f'{part_duplicate_ids}')
    LOGGER.info(f'Done in {tend}')
    return part_objs
