""" Utility functions for TOPEX METADATA preprocessing """
import pandas as pd


def prepare_metadata(metadata_file: str) -> 'pd.DataFrame':
    """ Returns a DataFrame that contains relevant metadata of machine parts.

        Args:
            metadata_file (str): .xlsx file of the metadata. 
    """
    raw_in = pd.read_excel(metadata_file)

    # PART_ID
    for p in raw_in.loc[:, 'Teilenummer']:
        raw_in['Teilenummer'] = raw_in['Teilenummer'].replace([p], str(p).replace(' ', '_').replace('/', '_'))
    part_ids = raw_in.loc[:, 'Teilenummer']
    # PART_NAME
    for name in raw_in.loc[:, 'Benennung']:
        raw_in['Benennung'] = raw_in['Benennung'].replace([name], str(name).replace(' ', '_').replace('/', '_'))
    part_names = raw_in.loc[:, 'Benennung']
    # PART_HIERARCHY
    part_hierarchy = raw_in.loc[:, 'Pos.-Nr.']
    # PART_MATERIAL
    part_materials = raw_in.loc[:, 'Werkstoff']
    part_materials.fillna('-', inplace=True)

    part_is_spare = []

    # Change Bem. values to Boolean that denotes whether part is spare or not
    # (V=Verschleißteil, E=Ersatzteil)
    for i, p in enumerate(raw_in.loc[:, 'Bem.']):
        if p.lower() == 'v' or p.lower() == 'e':
            part_is_spare.append(True)
        else:
            part_is_spare.append(False)

    df = pd.DataFrame(
        data={
            'part_id': part_ids,
            'part_name': part_names,
            'part_hierarchy': part_hierarchy,
            'part_material': part_materials,
            'part_is_spare': part_is_spare
        })

    return df