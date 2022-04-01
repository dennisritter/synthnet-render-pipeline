""" Functions for material definition of single parts"""
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
    MATERIAL_MAP = {
        "nan": "default.blend",
        "-": "default.blend",
        "X5CrNi18-10": "steel.blend",
        "X8CrNiS18-9": "steel.blend",
        "Stahl": "steel.blend",
        "St 37-k": "steel.blend",
        "38 Si 7": "steel.blend",
        "Edelstahl": "steel.blend",
        "X 10 CrNiS 18 9": "steel.blend",
        "Ck45": "steel.blend",
        "X 10CrNiS 18 9": "steel.blend",
        "Stahl 8.8": "steel.blend",
        "115CrV3(Silberstahl)": "steel.blend",
        "Silberstahl": "steel.blend",
        "Stahlblech": "steel.blend",
        "X20Cr13": "steel.blend",
        "Stahl 9.8": "steel.blend",
        "16MnCr5": "steel.blend",
        "C45 o ä": "steel.blend",
        "C45W": "steel.blend",
        "C45W o.ä": "steel.blend",
        "C45W o.ä.": "steel.blend",
        "Starwelle": "steel.blend",
        "14301": "steel.blend",
        "Metallausführung": "steel.blend",
        "AlMgSi1": "aluminium.blend",
        "AlMg4,5Mn": "aluminium.blend",
        "Al": "aluminium.blend",
        "AlCuMgPb": "aluminium.blend",
        "CuZn37": "brass.blend",
        "CuZn40": "brass.blend",
        "Rotguß": "brass.blend",
        "PA12": "plastic.blend",
        "X 10 CrNi S 18 9": "plastic.blend",
        "Kunststoff": "plastic.blend",
        "Polycarbonat": "plastic.blend",
        "Polyamid": "plastic.blend",
        "Trespa": "plastic.blend",
        "Trespa nw": "plastic.blend",
        "Trespa nw 6mm": "plastic.blend",
        "Trespa nw; 6mm": "plastic.blend",
        "Trespa nw 10mm": "plastic.blend",
        "Makrolon farblos 099": "plastic.blend",
        "Makrolon farblos 6mm": "plastic.blend",
        "Makrolon 2760(grau 6mm)": "plastic.blend",
        "Makrolon": "plastic.blend",
        "Maaaggraaloooon :-)  farblos 6mm": "plastic.blend",
        "Schaumstoff": "plastic.blend",
        "PA": "plastic.blend",
        "PS": "plastic.blend",
        "PVC": "plastic.blend",
        "Silikon SI 50±5ShA": "plastic.blend",
        "POM weiss": "plastic.blend",
        "Delrin - POM": "plastic.blend",
        "Polycarbonat farblos 8mm": "plastic.blend",
        "Polycarbonat farblos 6mm": "plastic.blend",
        "Polycarbonat 6mm": "plastic.blend",
        "Murtfeld grün": "plastic.blend",
        "Murtfeld S grün": "plastic.blend",
        "Folie lila": "plastic.blend",
        "Fils 2,5mm": "plastic.blend",
    }
    LOGGER.debug(f"--STATIC MATERIAL_MAP: {list(MATERIAL_MAP.keys())}")

    unmapped_metadata_materials = []
    for part in parts:
        for single_part in part.single_parts:
            # Get material for SinglePart from our metadata
            # NOTE: We assume, that SingleParts with the same ID are also of the same material,
            #       so we lookup the material using the first occurence only.
            metadata_material = metadata.loc[metadata['part_id'] == single_part.id].loc[:, "part_material"].values[0]

            # Store metadata materials that are not in MATERIAL_MAP
            if metadata_material not in list(MATERIAL_MAP.keys()):
                unmapped_metadata_materials.append(metadata_material)
                single_part.material = "default.blend"
            # Assign material from MATERIAL_MAP, whose key is the metadata_material
            else:
                single_part.material = MATERIAL_MAP[metadata_material]

            LOGGER.debug(f'{single_part.id}\n{metadata_material}\n{single_part.material}')
            LOGGER.debug('***' * 10)

    if unmapped_metadata_materials:
        LOGGER.warning(f'--UNMAPPED METADATA_MATERIALS: {unmapped_metadata_materials}')

    return parts