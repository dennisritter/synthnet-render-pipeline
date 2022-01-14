INPUT_DIR=./out/export_gltf_test_n3
OUTPUT_DIR=./out/render_test_n3


blender --background --python ./render/render.py -- \
 --input_directory $INPUT_DIR \
 --output_directory $OUTPUT_DIR \
