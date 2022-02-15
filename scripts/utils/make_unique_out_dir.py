""" Just create and return (print) a unique dir name. Should be called from shell script"""

import sys
import os
import re


def get_unique_dirname(parent_dir: str, dir_name: str):
    """ Returns a unique directory name following the pattern ID-DIR_NAME

        Args:
            parent_dir (str): The parent directory of the directory we determine the name for
            dir_name (str): Name of the dir, which is returned with prepended ID 
    
    """
    return f'{get_dir_id(parent_dir=parent_dir)}-{dir_name}'


def get_dir_id(parent_dir: str):
    """ Returns a continuous ID (int) based on other dirs in the given parent_dir.

        Will look for run directories in the given outdir and check their ids. 
        Then add 1 and return. 
    
        Args:
            paren_dir (str): The 

    """
    prev_run_dirs = []
    if os.path.isdir(parent_dir):
        prev_run_dirs = [x for x in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, x))]
    prev_run_ids = [re.match(r'^\d+', x) for x in prev_run_dirs]
    prev_run_ids = [int(x.group()) for x in prev_run_ids if x is not None]
    cur_run_id = max(prev_run_ids, default=-1) + 1

    return cur_run_id


if __name__ == '__main__':
    parent_dir = sys.argv[1]
    out_dir_name = sys.argv[2]

    unique_out_dir_name = get_unique_dirname(parent_dir=parent_dir, dir_name=out_dir_name)

    out_dir = f'{parent_dir}/{unique_out_dir_name}'
    os.makedirs(out_dir, exist_ok=True)
    print(out_dir)
    sys.exit(0)
