""" Functions for material definition of single parts"""

import pandas as pd
import logging

from models.part import Part
from models.single_part import SinglePart
from utils import timer_utils

LOGGER = logging.getLogger(__name__)


def assign_materials_static(parts: list, metadata: 'pd.DataFrame'):
    """ Returns a list of Part objects with assigned materials of all SingleParts. 
    
        Args:
            parts (list<Part>): A list of Part objects.
            metdata (pd.DataFrame): Prepared metadata DataFrame 
    
    """

    # MATERIAL_MAP = {
    #     "default": ["-"],
    #     "brushed_steel": [
    #         "X5CrNi18-10",
    #         "X8CrNiS18-9",
    #         "Stahl",
    #         "38 Si 7",
    #         "Edelstahl",
    #         "X 10 CrNiS 18 9",
    #         "Ck45",
    #         "X 10CrNiS 18 9",
    #         "Stahl 8.8",
    #         "Silberstahl",
    #         "X20Cr13",
    #         "Stahl 9.8",
    #     ],
    #     "aluminium": ["AlMgSi1", "AlMg4,5Mn", "Al", "AlCuMgPb"],
    #     "brass": ["CuZn37", "CuZn40"],
    #     "plastic": ["PA12", "X 10 CrNi S 18 9", "Kunststoff", "Polycarbonat", "Polyamid", "Trespa"],
    # }

    # Map materials of metadata to predefined materials
    MATERIAL_MAP = {
        "-": "default",
        "X5CrNi18-10": "brushed_steel",
        "X8CrNiS18-9": "brushed_steel",
        "Stahl": "brushed_steel",
        "38 Si 7": "brushed_steel",
        "Edelstahl": "brushed_steel",
        "X 10 CrNiS 18 9": "brushed_steel",
        "Ck45": "brushed_steel",
        "X 10CrNiS 18 9": "brushed_steel",
        "Stahl 8.8": "brushed_steel",
        "Silberstahl": "brushed_steel",
        "X20Cr13": "brushed_steel",
        "Stahl 9.8": "brushed_steel",
        "AlMgSi1": "aluminium",
        "AlMg4,5Mn": "aluminium",
        "Al": "aluminium",
        "AlCuMgPb": "aluminium",
        "CuZn37": "brass",
        "CuZn40": "brass",
        "PA12": "plastic",
        "X 10 CrNi S 18 9": "plastic",
        "Kunststoff": "plastic",
        "Polycarbonat": "plastic",
        "Polyamid": "plastic",
        "Trespa": "plastic",
    }
    LOGGER.debug(f"--STATIC MATERIAL_MAP: {list(MATERIAL_MAP.keys())}")

    unmapped_metadata_materials = []
    for part in parts:
        for single_part in part.single_parts:
            # Get material for SinglePart from our metadata
            # NOTE: We assume, that same SingleParts always have the same material,
            #       so take only the first value for a SinglePart id.
            metadata_material = metadata.loc[metadata['part_id'] == single_part.id].loc[:, "part_material"].values[0]

            # Store metadata materials that are not in MATERIAL_MAP
            if metadata_material not in list(MATERIAL_MAP.keys()):
                unmapped_metadata_materials.append(metadata_material)
                single_part.material = "default"
            # Assign material from MATERIAL_MAP, whose key is the metadata_material
            else:
                single_part.material = MATERIAL_MAP[metadata_material]

            LOGGER.debug(f'{single_part.id}\n{metadata_material}\n{single_part.material}')
            LOGGER.debug('***' * 10)

    if unmapped_metadata_materials:
        LOGGER.warning(f'--UNMAPPED METADATA_MATERIALS: {unmapped_metadata_materials}')

    return parts