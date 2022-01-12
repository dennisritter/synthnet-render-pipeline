RCFG_FILE=./cfg/rcfg_v2_test.json
BLEND_FILE=./data/drucker-example/drucker.blend
DATA_DIR=./data/drucker-example
OUT_DIR=./out/export_gltf_test


blender $BLEND_FILE --background --python ./render/export_gltfs.py -- \
 --rcfg_file $RCFG_FILE \
 --data_dir $DATA_DIR \
 --out_dir $OUT_DIR \