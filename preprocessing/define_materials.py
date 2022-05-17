""" Functions for material definition of single parts"""
import random
from timeit import default_timer
import pandas as pd
import logging

from preprocessing.models.part import Part

LOGGER = logging.getLogger(__name__)


def assign_materials_static(parts: list, metadata: 'pd.DataFrame') -> list[Part]:
    """ Returns a list of Part objects with assigned materials of all SingleParts. 
    
        Args:
            parts (list<Part>): A list of Part objects.
            metdata (pd.DataFrame): Prepared metadata DataFrame 
    
    """

    # Map materials of metadata to predefined materials

    # material map for customized materialiq materials
    # 900841-00.00.00_drucker
    default_material = "synthnet_steel_brushed.blend"
    MATERIAL_MAP = {
        "-:-": default_material,
        "nan:nan": default_material,
        "AlMgSi1:Natur eloxiert": "synthnet_aluminium_anodized.blend",
        "AlMg4,5Mn:Natur eloxiert": "synthnet_aluminium_anodized.blend",
        "Aluminium:Natur eloxiert": "synthnet_aluminium_anodized.blend",
        "AlMgSi1:Blank": "synthnet_aluminium_anodized.blend",
        "AlMgSi1:-": "synthnet_aluminium_anodized.blend",
        "AlMgSi1:RAL 7015 eloxiert": "synthnet_aluminium_anodized_ral7015.blend",
        "AlMg4,5Mn:Schwarz eloxiert": "synthnet_aluminium_anodized_black.blend",
        "AlMgSi1:topex-lila eloxiert": "synthnet_aluminium_anodized_purple.blend",
        "AlMgSi1:Hartcoatiert": "synthnet_aluminium_hardcoated.blend",
        "-:RAL 7015 eloxiert": "synthnet_aluminium_anodized_ral7015.blend",
        "-:topex-lila eloxier": "synthnet_aluminium_anodized_purple.blend",
        "X5CrNi18-10:Blank": "synthnet_steel_brushed.blend",
        "X8CrNiS18-9:Blank": "synthnet_steel_brushed.blend",
        "X10CrNi188:Blank": "synthnet_steel_brushed.blend",
        "Federstahl:Blank": "synthnet_steel_brushed.blend",
        "Edelstahl:Blank": "synthnet_steel_brushed.blend",
        "115CrV3:Blank": "synthnet_steel_brushed.blend",
        "Stahl:Blank": "synthnet_steel_brushed.blend",
        "X5CrNi18-10:Sandgestrahlt": "synthnet_steel_sandblasted.blend",
        "Stahl:Verzinkt": "synthnet_steel_galvanized.blend",
        "Stahl:Vernickelt": "synthnet_steel_nickelcoated.blend",
        "Stahl:Schwarz": "synthnet_steel_burnished.blend",
        "CuZn37:Blank": "synthnet_brass.blend",
        "Kunststoff:-": "synthnet_plastic_matte_black.blend",
        "PA12:Schwarz eingefärbt": "synthnet_plastic_matte_black.blend",
        "PA12:schwarz eingefärbt": "synthnet_plastic_matte_black.blend",
        "Kunststoff:Schwarz": "synthnet_plastic_matte_black.blend",
        "-:Schwarz": "synthnet_plastic_matte_black.blend",
        "Trespa:Neutralweiss": "synthnet_plastic_matte_white.blend",
        "ABS:Grau": "synthnet_plastic_matte_grey.blend",
        "-:Grün": "synthnet_plastic_matte_green.blend",
        "Acrylglas:Transparent": "synthnet_plastic_glossy_grey.blend",  # Transparent material shows envmap
        "Polycarbonat:transparent": "synthnet_plastic_glossy_grey.blend"  # Transparent material shows envmap
    }

    LOGGER.debug(f"--STATIC MATERIAL_MAP: {list(MATERIAL_MAP.keys())}")

    unmapped_metadata_materials = []
    for part in parts:
        for single_part in part.single_parts:
            # Get material for SinglePart from our metadata
            # NOTE: We assume, that SingleParts with the same ID are also of the same material,
            #       so we lookup the material using the first occurence only.
            metadata_material = metadata.loc[metadata['part_id'] == single_part.id].loc[:,
                                                                                        ["part_material"]].values[0][0]
            metadata_surface = metadata.loc[metadata['part_id'] == single_part.id].loc[:, ["part_surface"]].values[0][0]
            metadata_material_surface = f'{metadata_material}:{metadata_surface}'
            print(f'METADATA MATERIAL: {metadata_material_surface}')
            # Store metadata materials that are not in MATERIAL_MAP
            if metadata_material_surface not in list(MATERIAL_MAP.keys()):
                unmapped_metadata_materials.append(metadata_material_surface)
                single_part.material = default_material
            # Assign material from MATERIAL_MAP, whose key is the metadata_material
            else:
                single_part.material = MATERIAL_MAP[metadata_material_surface]

            LOGGER.debug(f'{single_part.id}\n{metadata_material_surface}\n{single_part.material}')
            LOGGER.debug('***' * 10)

    if unmapped_metadata_materials:
        LOGGER.warning(f'--UNMAPPED METADATA_MATERIALS: {unmapped_metadata_materials}')

    return parts


def assign_materials_random(parts: list,
                            metadata: 'pd.DataFrame',
                            materials: list = ["default.blend", "steel.blend", "brass.blend", "plastic.blend"],
                            seed: int = 42) -> list[Part]:
    """ Returns a list of Part objects with assigned materials of all SingleParts. 
    
        Args:
            parts (list<Part>): A list of Part objects.
            metdata (pd.DataFrame): Prepared metadata DataFrame 
    
    """
    random.seed(seed)
    for part in parts:
        for single_part in part.single_parts:
            single_part.material = random.choice(materials)

    return parts
