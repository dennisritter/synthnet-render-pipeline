#!/bin/bash

DATASET_DIR="out/9-drucker_se_su_static_static_256_12_png"

python scripts/utils/upload_dataset_info_wandb.py \
--dataset_info_file "$DATASET_DIR/dataset_info.json" \
--dataset_render_dir "$DATASET_DIR/render" \
--wandb_project "synthnet-datasets" \
--wandb_entity "dritter" \
--wandb_name "drucker_se_su_static_static_256_12"