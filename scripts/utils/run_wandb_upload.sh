#!/bin/bash

RUN_NAME="1-900841-00.00.00_drucker_su_su_disabled_gray_256_12"
DATASET_DIR="out/$RUN_NAME"

python scripts/utils/upload_dataset_info_wandb.py \
--dataset_info_file "$DATASET_DIR/dataset_info.json" \
--dataset_render_dir "$DATASET_DIR/render" \
--wandb_project "synthnet-datasets" \
--wandb_entity "dritter" \
--wandb_name $RUN_NAME