""" Identify all parts and their single parts """
import logging
import pandas as pd

from preprocessing.models.part import Part
from preprocessing.models.single_part import SinglePart
from utils import timer_utils

LOGGER = logging.getLogger(__name__)


def get_unique_single_parts(metadata: "pd.DataFrame", parent_part: Part):
    """Recursively iterates over children of the given parent_part until parent_part is a
    single_part (has no sub-parts).

    Returns a list of the parent_parts' single parts or the parent_part itself
    if parent_part is a single_part already.

    Args:
        metadata (pandas.DataFrame):
            A Pandas DataFrame containing cols [part_id, part_name, part_hierarchy,
            part_material, part_is_spare]. Each row represents a part.
        parent_part (Part): The part to identify included single_parts for.

    """

    # Hierarchy Example: '1.2.5'
    # Every part that starts with the same hierarchy as parent_part and continue with a '.' are direct subparts of parent_part
    subparts = metadata.loc[metadata["part_hierarchy"].str.startswith(parent_part.hierarchy + ".")]

    # All single_parts of parent_part are going to be stored here
    single_parts_unique = []
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
                id=subpart["part_id"],
                name=subpart["part_name"],
                hierarchy=subpart["part_hierarchy"],
                is_spare=subpart["part_is_spare"],
            )
            single_parts = get_unique_single_parts(metadata, parent_part=part)
            for single_part in single_parts:
                if single_part not in single_parts_unique:
                    single_parts_unique.append(single_part)

    LOGGER.debug(f"PARENT: {parent_part.id}")
    LOGGER.debug(f"N_SUBPARTS:{len(subparts)}")
    LOGGER.debug(f"N_SINGLE_PARTS:{len(single_parts_unique)}")
    LOGGER.debug(f"SINGLE_PARTS: {[sp.id for sp in single_parts_unique]}")
    LOGGER.debug("- " * 10)
    return single_parts_unique


def parse_parts(metadata: "pd.DataFrame"):
    """Returns list of Parts and each included SinglePart (unique) as a list of Part objects.

    - Each part is added only once (no duplicates, key = Part.id)
    - Each SinglePart of a Part is added only once (SinglePart.id)

    Args:
        metadata (pandas.DataFrame):
            A Pandas DataFrame containing cols [part_id, part_name, part_hierarchy,
            part_material, part_is_spare]. Each row represents a part.

    """
    parts = []
    part_duplicates = []

    for i, row in metadata.iterrows():
        # Init Part (without single_parts)
        part = Part(
            id=row["part_id"],
            name=row["part_name"],
            hierarchy=row["part_hierarchy"],
            is_spare=row["part_is_spare"],
        )

        # Check if part is duplicate
        if part in parts:
            part_duplicates.append(part)
            continue

        # Get single parts for current part
        LOGGER.debug("# " * 10)
        LOGGER.debug(f'# Single parts for: {row["part_id"]}')
        LOGGER.debug("# " * 10)
        single_parts = get_unique_single_parts(metadata, part)
        part.single_parts = single_parts

        parts.append(part)

    LOGGER.debug(f"--Returning {len(parts)} parts")
    LOGGER.debug(f"--Ignoring {len(part_duplicates)} duplicates")
    LOGGER.debug("--Part Duplicate IDs")
    LOGGER.debug(f"{[p.id for p in part_duplicates]}")

    return parts
