"""Upload info about a generated dataset to wandb"""

import os
import json
import click
import wandb
from types import SimpleNamespace


@click.command()
@click.option(
    '--dataset_info_file',
    help='Path to dataset info file',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    '--dataset_render_dir',
    help='Directory to rendered images',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
)
@click.option(
    '--wandb_project',
    help='Path to dataset info file',
    type=str,
    default='synthnet-datasets',
)
@click.option(
    '--wandb_entity',
    help='Path to dataset info file',
    type=str,
    default='dritter',
)
@click.option('--wandb_name', help='wandb name for this upload', type=str, required=True)
def main(**kwargs):
    args = SimpleNamespace(**kwargs)

    dataset_info_file = args.dataset_info_file
    dataset_render_dir = args.dataset_render_dir
    wandb_project = args.wandb_project
    wandb_entity = args.wandb_entity
    wandb_name = args.wandb_name

    with open(dataset_info_file, 'r') as f:
        dataset_info = json.load(f)
    wandb.init(project=wandb_project, entity=wandb_entity, name=wandb_name, config=dataset_info)

    # Save first, last and middle image from renders
    render_fnames = os.listdir(dataset_render_dir)
    img1 = f"{dataset_render_dir}/{render_fnames[0]}"
    img2 = f"{dataset_render_dir}/{render_fnames[-1]}"
    img3 = f"{dataset_render_dir}/{render_fnames[int(len(render_fnames) / 2)]}"
    wandb.log({"examples": [wandb.Image(img1), wandb.Image(img2), wandb.Image(img3)]})


if __name__ == '__main__':
    main()
