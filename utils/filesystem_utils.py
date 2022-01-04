""" Utilit functions for operations with the local filesystem """

import os
import re


def get_run_id(outdir: str):
    """ Returns a continuous run ID (int) for the given directory.

        Will look for run directories in the given outdir and check their ids. 
        Then add 1 and return. 
    
        Args:
            outdir (str): The 

    """
    prev_run_dirs = []
    if os.path.isdir(outdir):
        prev_run_dirs = [
            x for x in os.listdir(outdir)
            if os.path.isdir(os.path.join(outdir, x))
        ]
    prev_run_ids = [re.match(r'^\d+', x) for x in prev_run_dirs]
    prev_run_ids = [int(x.group()) for x in prev_run_ids if x is not None]
    cur_run_id = max(prev_run_ids, default=-1) + 1

    return cur_run_id
