""" Utility functions for preprocessing """
import pandas as pd


def prepare_metadata(metadata_file: str):
    raw_in = pd.read_excel(metadata_file)
    part_ids = raw_in.loc[:, 'Teilenummer']
    part_names = raw_in.loc[:, 'Benennung']
    part_hierarchy = raw_in.loc[:, 'Pos.-Nr.']
    part_materials = raw_in.loc[:, 'Werkstoff']
    part_is_spare = []

    # Change Bem. values to Boolean that denotes whether part is spare or not
    # (V=Verschleißteil, E=Ersatzteil)
    for i, p in enumerate(raw_in.loc[:, 'Bem.']):
        if p == 'V' or p == 'E':
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
    # print(f'Item example:\n{df.iloc[42]}')