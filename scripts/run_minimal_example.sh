#!/bin/bash
# IMPORTANT: Run this script from project root to function properly!
SECONDS=0

# NOTE: param $1 defines the RUN_MODE:
#   1 = Preprocessing only
#   2 = Preprocessing and GLTF Export
#   3 = Preprocessing, GLTF Export and Rendering
#   default=3

# Set run mode by args or set default
RUN_MODE="${1}"
if [ -z "$1" ]; then
    RUN_MODE=3
fi
# Set camera seed by Args or set default
CAMERA_SEED="${2}"
if [ -z "$2" ]; then
    CAMERA_SEED=42
fi
# Set light seed by Args or set default
LIGHT_SEED="${3}"
if [ -z "$3" ]; then
    LIGHT_SEED=43
fi

# Shell script to trigger a SynthNet Render Pipeline run using a minimal example
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
RESOURCE_DIR="./data/mini_example"
TOPEX_METADATA_FILE="${RESOURCE_DIR}/mini_example.xlsx"
TOPEX_BLENDER_FILE="${RESOURCE_DIR}/mini_example.blend"
MATERIALS_DIR="${RESOURCE_DIR}/materials"
ENVMAPS_DIR="${RESOURCE_DIR}/envmaps"

##### OUTPUTS
# Specify output root directory and a run description to create a unique output directory
OUT_ROOT_DIR="./out"
RUN_DESCRIPTION="mini-example"
# will return a dir path like '$OUT_ROOT_DIR/$ID-$RUN_DESCRIPTION -> ./out/1-my-run
OUT_DIR=$(python scripts/utils/make_unique_out_dir.py "$OUT_ROOT_DIR" "$RUN_DESCRIPTION")
echo "Created output directory: $OUT_DIR"
# Copy input data into the out dir
cp -R $RESOURCE_DIR "${OUT_DIR}/input_data"
###################################

########## PREPROCESSING ##########
N_IMAGES_PER_PART=3
CAMERA_DEF_MODE='sphere-equidistant'
LIGHT_DEF_MODE='sphere-uniform'
MATERIAL_DEF_MODE='static'
ENVMAP_DEF_MODE='static'

PREPROCESSING_SECONDS_START=$SECONDS
python preprocessing.py \
    --topex_metadata_file $TOPEX_METADATA_FILE \
    --topex_blend_file $TOPEX_BLENDER_FILE \
    --materials_dir $MATERIALS_DIR \
    --out_dir $OUT_DIR \
    --n_images_per_part $N_IMAGES_PER_PART \
    --camera_def_mode $CAMERA_DEF_MODE \
    --light_def_mode $LIGHT_DEF_MODE \
    --material_def_mode $MATERIAL_DEF_MODE \
    --envmap_def_mode $ENVMAP_DEF_MODE \
    --camera_seed $CAMERA_SEED \
    --light_seed $LIGHT_SEED
PREPROCESSING_SECONDS_END=$(($SECONDS - $PREPROCESSING_SECONDS_START))
###################################

########## EXPORT GLTFs ###########
if [[ $RUN_MODE -ge 2 ]]; then
    RCFG_NAME="rcfg.json"
    RCFG_FILE="$OUT_DIR/$RCFG_NAME"
    GLTF_DIR="$OUT_DIR/gltf"

    # Run Export GLTFs
    EXPORT_SECONDS_START=$SECONDS
    blender $TOPEX_BLENDER_FILE --background --python ./bpy_modules/export_gltfs.py -- \
        --rcfg_file $RCFG_FILE \
        --out_dir $GLTF_DIR
    EXPORT_SECONDS_END=$(($SECONDS - $EXPORT_SECONDS_START))
fi
###################################

############# RENDER ##############
if [[ $RUN_MODE -ge 3 ]]; then
    # Set options
    RES_X=256
    RES_Y=256
    OUT_QUALITY=100
    OUT_FORMAT="PNG"
    ENGINE="CYCLES"
    DEVICE="GPU"
    RENDER_SECONDS_START=$SECONDS
    blender --background --python ./bpy_modules/render.py -- \
        --gltf_dir $GLTF_DIR \
        --material_dir $MATERIALS_DIR \
        --envmap_dir $ENVMAPS_DIR \
        --out_dir $OUT_DIR \
        --rcfg_file="$OUT_DIR/$RCFG_NAME" \
        --res_x $RES_X \
        --res_y $RES_Y \
        --out_quality $OUT_QUALITY \
        --out_format $OUT_FORMAT \
        --engine $ENGINE \
        --device $DEVICE
    RENDER_SECONDS_END=$(($SECONDS - $RENDER_SECONDS_START))
fi

echo "Time Measures:"
echo "Total time (s): $SECONDS"
echo "Preprocessing time (s): $PREPROCESSING_SECONDS_END"
echo "GLTF Export time (s): $EXPORT_SECONDS_END"
echo "Render time (s): $RENDER_SECONDS_END"
