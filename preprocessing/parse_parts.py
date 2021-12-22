""" Identify all parts and their single parts """
import logging
import pandas as pd

from models.part import Part
from models.single_part import SinglePart
from utils import timer_utils

LOGGER = logging.getLogger(__name__)


def get_unique_single_parts(metadata: 'pd.DataFrame', parent_part: Part):
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
    single_parts_unique = []

    # Hierarchy Example: '1.2.5'
    # Every part that starts with the same hierarchy as parent_part and continue with a '.' are direct subparts of parent_part
    subparts = metadata.loc[metadata['part_hierarchy'].str.startswith(parent_part.hierarchy + '.')]

    # If parent_part has no subparts, it is a single part itself
    # so add it to the single_parts list if it is not added already
    if len(subparts) == 0:
        single_part = SinglePart(id=parent_part.id, name=parent_part.name)
        if single_part not in single_parts_unique:
            single_parts_unique.append(single_part)

    # If paren_part has subparts, determine their subparts by calling this function again
    # with subpart being the new parent_part
    else:
        for _, subpart in subparts.iterrows():
            part = Part(
                id=subpart['part_id'],
                name=subpart['part_name'],
                hierarchy=subpart['part_hierarchy'],
                is_spare=subpart['part_is_spare'],
            )
            single_parts = get_unique_single_parts(metadata, parent_part=part)
            for single_part in single_parts:
                if single_part not in single_parts_unique:
                    single_parts_unique.append(single_part)

    LOGGER.debug(f'PARENT: {parent_part.id}')
    LOGGER.debug(f'N_SUBPARTS:{len(subparts)}')
    LOGGER.debug(f'N_SINGLE_PARTS:{len(single_parts_unique)}')
    LOGGER.debug(f'SINGLE_PARTS: {[sp.id for sp in single_parts_unique]}')
    LOGGER.debug('- ' * 10)
    return single_parts_unique


def parse_parts(metadata: 'pd.DataFrame'):
    """ Returns list of Parts and each included SinglePart (unique)  as a list of Part objects.

        - Each part (key: part_id) is added only once (no duplicates)
        - Each SinglePart (key: part_id) of a Part is added only once (no duplicates)
        
        Args:
            metadata (pandas.DataFrame):
                A Pandas DataFrame containing cols [part_id, part_name, part_hierarchy, 
                part_material, part_is_spare]. Each row represents a part.

    """
    tstart = timer_utils.time_now()
    LOGGER.info('\n')
    LOGGER.info('- ' * 20)
    LOGGER.info('Parsing unique Parts from metadata.xlsx')
    # LOGGER.debug(f'{metadata.info()}')
    # LOGGER.debug(f'{metadata.describe()}')

    parts = []
    part_duplicates = []

    for i, row in metadata.iterrows():
        # Init Part (without single_parts)
        part = Part(
            id=row['part_id'],
            name=row['part_name'],
            hierarchy=row['part_hierarchy'],
            is_spare=row['part_is_spare'],
        )

        # Check if part is duplicate
        # True -> skip this part, remember in duplicate list
        # False -> Add to part to parts
        if part in parts:
            part_duplicates.append(part)
            continue

        # Get single parts for current part
        LOGGER.debug('# ' * 10)
        LOGGER.debug(f'# Single parts for: {row["part_id"]}')
        LOGGER.debug('# ' * 10)
        single_parts = get_unique_single_parts(metadata, part)
        part.single_parts = single_parts

        parts.append(part)

    tend = timer_utils.time_since(tstart)
    LOGGER.info(f'--Returning {len(parts)} parts')
    LOGGER.info(f'--Ignoring {len(part_duplicates)} duplicates')
    LOGGER.debug('--Part Duplicate IDs')
    LOGGER.debug(f'{[p.id for p in part_duplicates]}')
    LOGGER.info(f'Done in {tend}')
    LOGGER.info('- ' * 20)

    return parts
