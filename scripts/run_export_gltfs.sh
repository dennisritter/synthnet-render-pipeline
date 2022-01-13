RCFG_FILE=./out/11-testrun-n3/rcfg_v2.json
BLEND_FILE=./data/drucker-example/drucker.blend
DATA_DIR=./data/drucker-example
OUT_DIR=./out/export_gltf_test_n3


blender $BLEND_FILE --background --python ./render/export_gltfs.py -- \
 --rcfg_file $RCFG_FILE \
 --data_dir $DATA_DIR \
 --out_dir $OUT_DIR \