""" Functions for material definition of single parts"""
import random
from timeit import default_timer
import pandas as pd
import logging
import os

from preprocessing.models.part import Part

LOGGER = logging.getLogger(__name__)


def assign_materials_static(parts: list, metadata: 'pd.DataFrame', materials_dir: str) -> list[Part]:
    """ Returns a list of Part objects with assigned materials of all SingleParts. 
    
        Args:
            parts (list<Part>): A list of Part objects.
            metdata (pd.DataFrame): Prepared metadata DataFrame 
    
    """

    # Map materials of metadata to predefined materials
    unmapped_metadata_materials = []
    default_material = "synthnet_steel_brushed_natural.blend"
    for part in parts:
        for single_part in part.single_parts:
            md_singlepart = metadata.loc[metadata['part_id'] == single_part.id]
            md_material = md_singlepart.loc[:, ["part_material"]].values[0][0]
            md_surface = md_singlepart.loc[:, ["part_surface"]].values[0][0]
            md_color = md_singlepart.loc[:, ["part_color"]].values[0][0]
            material_name = f'synthnet_{md_material}_{md_surface}_{md_color}.blend'
            single_part.material = material_name
            LOGGER.debug(f'\n{single_part.id}\n{material_name}')
            LOGGER.debug('***' * 10)
            if single_part.material not in os.listdir(materials_dir):
                unmapped_metadata_materials.append((single_part.id, single_part.material))
                single_part.material = default_material

    for unmapped in unmapped_metadata_materials:
        LOGGER.info(f'UNMAPPED MATERIALS (using default: {default_material}): {unmapped}')

    return parts


def assign_materials_random(
    parts: list,
    metadata: 'pd.DataFrame',
    materials_dir: str,
    seed: int = 42,
) -> list[Part]:
    """ Returns a list of Part objects with assigned materials of all SingleParts. 
    
        Args:
            parts (list<Part>): A list of Part objects.
            metdata (pd.DataFrame): Prepared metadata DataFrame 
    
    """
    materials = os.listdir(materials_dir)
    random.seed(seed)
    for part in parts:
        for single_part in part.single_parts:
            single_part.material = random.choice(materials)

    return parts
