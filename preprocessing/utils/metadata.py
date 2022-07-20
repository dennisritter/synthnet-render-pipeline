""" Utility functions for TOPEX METADATA preprocessing """
import pandas as pd


def prepare_metadata(metadata_file: str) -> 'pd.DataFrame':
    """ Returns a DataFrame that contains relevant metadata of machine parts.

        Args:
            metadata_file (str): .xlsx file of the metadata. 
    """
    raw_in = pd.read_excel(metadata_file)

    # Remove SolidWorks Toolbox parts
    raw_in = raw_in.drop(raw_in[raw_in["Benennung 2"] == "SolidWorks Toolbox"].index).reset_index(drop=True)

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
    # PART_IS_SPARE (E = Ersatzteil)
    part_is_spare = [p.lower() == 'e' for p in raw_in.loc[:, 'Bem.'].astype(str)]
    # PART_IS_WEAR (V = Verschleißteil)
    part_is_wear = [p.lower() == 'v' for p in raw_in.loc[:, 'Bem.'].astype(str)]

    # PART_MATERIAL
    # 1. To lower case
    # 2. Replace NA values
    # 3. Simplify material, surface_treatment and color
    part_materials = raw_in.loc[:, 'Werkstoff'].astype(str)
    part_materials = part_materials.str.lower()
    part_materials.fillna('-', inplace=True)
    part_materials = part_materials.replace('nan', '-')
    aluminium = ["AlMg4,5Mn", "Aluminium", "AlMgSi1"]
    steel = ["X5CrNi18-10", "X8CrNiS18-9", "X10CrNi188", "Federstahl", "Edelstahl", "115CrV3", "Stahl"]
    brass = ["CuZn37"]
    plastic = [
        "Kunststoff", "kunststoff matt", "kunststoff glänzend", "polycord", "PA12", "Trespa", "ABS",
        "Kunststoff u. Gewebe"
    ]
    plexiglas = ["Acrylglas", "Polycarbonat"]

    # PART SURFACE & COLOR
    # 1. to lower case
    # 2. Replace NA values
    # 3. Re-Map and split surface and color values
    part_surface = raw_in.loc[:, ' Oberfläche'].astype(str)
    part_surface = part_surface.str.lower()
    part_surface.fillna('-', inplace=True)
    part_surface = part_surface.replace('nan', '-')
    part_color = part_surface.copy()
    # SURFACE
    anodized = ["schwarz eloxiert", "ral 7015 eloxiert", "topex-lila eloxiert", "natur eloxiert", "eloxiert"]
    hardcoated = ["hartcoatiert"]
    sandblasted = ["sandgestrahlt"]
    nickelcoated = ["vernickelt"]
    galvanized = ["verzinkt"]
    brushed = ["blank"]
    burnished = ["brüniert"]
    glossy = ["Kunststoff glänzend", "Trespa"]
    matte = ["Kunststoff matt", "Polycord", "PA12", "ABS"]
    # COLOR
    black = ["schwarz", "schwarz eingefärbt", "schwarz eloxiert"]
    grey = ["grau"]
    ral7015 = ["ral 7015 eloxiert"]
    green = ["grün"]
    yellow = ["gelb"]
    orange = ["orange"]
    purple = ["topex-lila eloxiert"]
    white = ["neutralweiss"]
    natural = ["natur eloxiert", "sandgestrahlt", "hartcoatiert", "vernickelt", "verzinkt", "blank", "brüniert"]
    transparent = ["transparent"]

    # NOTE: Replace Add surface info matte/glossy for plastics depending on material (before remapping)
    glossy = [x.lower() for x in ["Kunststoff glänzend", "Trespa"]]
    matte = [x.lower() for x in ["Kunststoff", "Kunststoff matt", "Kunststoff u. Gewebe", "Polycord", "PA12", "ABS"]]
    glossy_idx = part_materials[part_materials.isin(glossy)].index
    matte_idx = part_materials[part_materials.isin(matte)].index
    part_surface[glossy_idx] = "glossy"
    part_surface[matte_idx] = "matte"

    # material replace
    material_mapping = [
        [aluminium, 'aluminium'],
        [steel, 'steel'],
        [brass, 'brass'],
        [plastic, 'plastic'],
        [plexiglas, 'plexiglas'],
    ]
    for mm in material_mapping:
        mm[0] = [x.lower() for x in mm[0]]
        part_materials = part_materials.replace(dict.fromkeys(mm[0], mm[1]))
    # surface replace
    surface_mapping = [
        [anodized, "anodized"],
        [hardcoated, "hardcoated"],
        [sandblasted, "sandblasted"],
        [nickelcoated, "nickelcoated"],
        [galvanized, "galvanized"],
        [brushed, "brushed"],
        [burnished, "burnished"],
        [glossy, "glossy"],
        [matte, "matte"],
    ]
    for sm in surface_mapping:
        sm[0] = [x.lower() for x in sm[0]]
        part_surface = part_surface.replace(dict.fromkeys(sm[0], sm[1]))
    # color replace
    colors_mapping = [
        [black, "black"],
        [grey, "grey"],
        [ral7015, "ral7015"],
        [green, "green"],
        [yellow, "yellow"],
        [orange, "orange"],
        [purple, "purple"],
        [white, "white"],
        [natural, "natural"],
        [transparent, "transparent"],
    ]
    for cm in colors_mapping:
        cm[0] = [x.lower() for x in cm[0]]
        part_color = part_color.replace(dict.fromkeys(cm[0], cm[1]))

    df = pd.DataFrame(
        data={
            'part_id': part_ids,
            'part_number': part_number,
            'part_name': part_names,
            'part_hierarchy': part_hierarchy,
            'part_material': part_materials,
            'part_surface': part_surface,
            'part_color': part_color,
            'part_is_spare': part_is_spare,
            'part_is_wear': part_is_wear
        })
    # Set defaults for material, surface, color
    DEFAULT_MATERIAL = "steel"
    DEFAULT_COLOR = "natural"
    DEFAULT_SURFACE = {
        "steel": "brushed",
        "aluminium": "anodized",
        "brass": "brushed",
        "plastic": "matte",
        "plexiglas": "glossy"
    }

    df["part_material"].replace('-', DEFAULT_MATERIAL, inplace=True)
    df["part_color"].replace('-', DEFAULT_COLOR, inplace=True)
    for material, surface in DEFAULT_SURFACE.items():
        df.loc[df.part_material == material, "part_surface"] = df.loc[df.part_material == material,
                                                                      "part_surface"].replace('-',
                                                                                              surface,
                                                                                              inplace=False)

    return df
