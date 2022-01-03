""" Exports an OBJ file for each part"""

import os
from models.part import Part


def export_part_objs(parts: list, blend_file: str, out_dir: str):
    """ Exports an OBJ file to out_dir for each given part in blend_file 
    
        Args:
            parts (list): All parts of the machine to render (parsed from metadata.xlsx)
            blend_file (str): Path to blender file of the machine
            out_dir (str): Where to store exported OBJ files 
    """
