#!/bin/bash
# IMPORTANT: Run this script from project root to function properly!

# NOTE: param $1 defines the RUN_MODE:
#   1 = Preprocessing only
#   2 = Preprocessing and GLTF Export
#   3 = Preprocessing, GLTF Export and Rendering
#   default=3

# Set run mode by args or set default
RUN_MODE="${1}"
if [ -z "$1" ]
    then
        RUN_MODE=3
fi
# Set camera seed by Args or set default
CAMERA_SEED="${2}"
if [ -z "$2"]
    then
        CAMERA_SEED=42
fi
# Set light seed by Args or set default
LIGHT_SEED="${3}"
if [ -z "$3"]
    then
        LIGHT_SEED=43
fi

# Shell script to trigger a SynthNet Rendering Pipeline run using a minimal example
#
# 1. Preprocessing to generate a render config (rcfg)
# 2. Export GLTF-scenes based on the RCFG from preprocessing and CAD data
# 3. Render all GLTFs 

echo "- - - - - - - - - - - - - - - - - - - - "
echo "Starting SynthNet Rendering Pipeline run."
echo "RUN_MODE: ${RUN_MODE}"
echo "  1 = Preprocessing only"
echo "  2 = Preprocessing and GLTF Export"
echo "  3 = Preprocessing, GLTF Export and Rendering"
echo "- - - - - - - - - - - - - - - - - - - - "

##### RESOURCES
# Resource directory path. Contains Environment maps, materials, CAD data and metadata. 
# (relative to project root)
RESOURCE_DIR="./data/drucker_example"
TOPEX_METADATA_FILE="${RESOURCE_DIR}/drucker.xlsx"
TOPEX_BLENDER_FILE="${RESOURCE_DIR}/drucker.blend"
MATERIALS_DIR="${RESOURCE_DIR}/materials"
ENVMAPS_DIR="${RESOURCE_DIR}/envmaps"

##### OUTPUTS
# Specify output root directory and a run description to create a unique output directory
OUT_ROOT_DIR="./out"
RUN_DESCRIPTION="drucker_example"
# will return a dir path like '$OUT_ROOT_DIR/$ID-$RUN_DESCRIPTION -> ./out/1-my-run
OUT_DIR=`python scripts/make_unique_out_dir.py "$OUT_ROOT_DIR" "$RUN_DESCRIPTION"`
echo "Created output directory: $OUT_DIR"

########## PREPROCESSING ##########
# Set options
N_IMAGES_PER_PART=3
SCENE_MODE='exclusive'
CAMERA_DEF_MODE='sphere-uniform'
LIGHT_DEF_MODE='sphere-uniform'
MATERIAL_DEF_MODE='static'
ENVMAP_DEF_MODE='static'

# Run Preprocessing
python preprocessing.py \
--metadata_file $TOPEX_METADATA_FILE \
--blend_file $TOPEX_BLENDER_FILE \
--out_dir $OUT_DIR \
--n_images_per_part $N_IMAGES_PER_PART \
--scene_mode $SCENE_MODE \
--camera_def_mode $CAMERA_DEF_MODE \
--light_def_mode $LIGHT_DEF_MODE \
--material_def_mode $MATERIAL_DEF_MODE \
--envmap_def_mode $ENVMAP_DEF_MODE \
--camera_seed $CAMERA_SEED \
--light_seed $LIGHT_SEED
###################################

########## EXPORT GLTFs ##########
if [[ $RUN_MODE -ge 2 ]]; then
    # Set options
    RCFG_NAME="rcfg_v2.json"
    RCFG_FILE="$OUT_DIR/$RCFG_NAME"
    GLTF_DIR="$OUT_DIR/gltf"

    # Run Export GLTFs
    blender $TOPEX_BLENDER_FILE --background --python ./bpy_modules/export_gltfs.py -- \
    --rcfg_file $RCFG_FILE \
    --data_dir $RESOURCE_DIR \
    --out_dir $GLTF_DIR 
fi
###################################

########## RENDER ##########
if [[ $RUN_MODE -ge 3 ]]; then
    # Set options
    RES_X=256
    RES_Y=256
    OUT_QUALITY=100
    OUT_FORMAT="JPEG"
    ENGINE="CYCLES"
    # Run Export GLTFs
    blender --background --python ./bpy_modules/render.py -- \
    --in_dir $GLTF_DIR \
    --out_dir $OUT_DIR/render \
    --res_x $RES_X \
    --res_y $RES_Y \
    --out_quality $OUT_QUALITY \
    --out_format $OUT_FORMAT \
    --engine $ENGINE
fi
############################