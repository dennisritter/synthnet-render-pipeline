""" Utility functions for TOPEX METADATA preprocessing """
import pandas as pd


def prepare_metadata(metadata_file: str) -> 'pd.DataFrame':
    """ Returns a DataFrame that contains relevant metadata of machine parts.

        Args:
            metadata_file (str): .xlsx file of the metadata. 
    """
    raw_in = pd.read_excel(metadata_file)

    # PART_NUMBER
    part_number = raw_in.loc[:, 'Teilenummer'].astype(str)
    # PART_ID
    # 1. remove spaces and special characters
    for p in raw_in.loc[:, 'Teilenummer']:
        raw_in['Teilenummer'] = raw_in['Teilenummer'].replace([p], str(p).replace(' ', '_').replace('/', '_'))
    part_ids = raw_in.loc[:, 'Teilenummer']
    # PART_NAME
    # 1. remove spaces and special characters
    for name in raw_in.loc[:, 'Benennung']:
        raw_in['Benennung'] = raw_in['Benennung'].replace([name], str(name).replace(' ', '_').replace('/', '_'))
    part_names = raw_in.loc[:, 'Benennung']
    # PART_HIERARCHY
    part_hierarchy = raw_in.loc[:, 'Pos.-Nr.'].astype(str)
    # PART_MATERIAL
    # 1. Replace NA values
    # 2. Simplify material, surface_treatment and color
    part_materials = raw_in.loc[:, 'Werkstoff'].astype(str)
    part_materials.fillna('-', inplace=True)
    part_materials = part_materials.replace('nan', '-')
    aluminium = ["AlMg4,5Mn", "Aluminium", "AlMgSi1"]
    steel = ["X5CrNi18-10", "X8CrNiS18-9", "X10CrNi188", "Federstahl", "Edelstahl", "115CrV3", "Stahl"]
    brass = ["CuZn37"]
    plastic = ["Kunststoff", "PA12", "Trespa", "ABS"]
    plexiglas = ["Acrylglas", "Polycarbonat"]
    part_materials = part_materials.replace(dict.fromkeys(steel, 'steel'))
    part_materials = part_materials.replace(dict.fromkeys(aluminium, 'aluminium'))
    part_materials = part_materials.replace(dict.fromkeys(brass, 'brass'))
    part_materials = part_materials.replace(dict.fromkeys(plastic, 'plastic'))
    part_materials = part_materials.replace(dict.fromkeys(plexiglas, 'plexiglas'))
    # PART SURFACE
    part_surface = raw_in.loc[:, ' Oberfläche'].astype(str)
    part_surface.fillna('-', inplace=True)
    part_surface = part_surface.replace('nan', '-')
    # PART_IS_SPARE (E = Ersatzteil)
    part_is_spare = [p.lower() == 'e' for p in raw_in.loc[:, 'Bem.'].astype(str)]
    # PART_IS_WEAR (V = Verschleißteil)
    part_is_wear = [p.lower() == 'v' for p in raw_in.loc[:, 'Bem.'].astype(str)]

    df = pd.DataFrame(
        data={
            'part_id': part_ids,
            'part_number': part_number,
            'part_name': part_names,
            'part_hierarchy': part_hierarchy,
            'part_material': part_materials,
            'part_surface': part_surface,
            'part_is_spare': part_is_spare,
            'part_is_wear': part_is_wear
        })

    return df
