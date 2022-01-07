# SynthNet Rendering Pipeline

The purpose of the rendering pipeline is to parse a Blender file and export gltf-scenes for each of a machines' assemblys and single components to render multiple images for each part in order to create an image based search index from them.

## Getting Started

TODO: Add tutorial

## Usage

A full process, from preprocessing to rendered images involves three essential steps.
1. **Preprocessing** to create the render configuration JSON file (RCFG).
2. **GLTF Export** to export GLTF files that describes a scene for each machine part according to the RCFG.
3. **Rendering** to read each parts GLTF files and render multiple images from it.

### Preprocessing
The [preprocessing](./preprocessing.py) script creates a render configuration according to a [json schema](./schemas/rcfg_schema_v2). The created RCFG lists every machine part that must be rendered and defines all lights, cameras, materials and environment maps used. Further it defines render setups, that describe which of the scene components are used for each particular render.

Run the command below to see all options for the preprocessing script.
```shell
python preprocessing.py --help
```
Also check the [example run script](./scripts/run_preprocessing_example)

---
### GLTF Export
The [GLTF Export]() reads the RCFG created by the preprocessing step and a structured .blend file of a machine. Then it uses the [Blender API](https://docs.blender.org/api/current/index.html) to create cameras and lights, assigns materials to single parts and loads environment maps according to the RCFG. Further, an animation is created where keyframes define which of the created scene parts are used for one render. Finally, a GLTF file including all scene components and the *render animation keyframes* is exported.

See the example shell script below
```shell
blender -b -P ./export_gltfs.py -- --config /path/to/config --output_directory path/to/output
```
---
### Rendering
The [Rendering]() process reads GLTF files exported by the *GLTF Export* and simply renders the images as defined by the *render animation keyframes*.

See the example shell script below
```shell
blender -b -P ./render.py -- --input_directory /path/to/gltf_files --output_directory /path/to/output_dir --resolution_x 512 --resolution_y 512 --output_quality 100 --output_format JPEG --engine BLENDER_EEVEE
```

## Render Configuration (RCFG)

The render configuration (RCFG) is a JSON file that determines the scene components and render setups for each machine part. This includes cameras, lights, materials and environment maps. The RCFG file must follow the [Config Schema](./schemas/rcfg_schema_v2.json). 

---
TODO: Update and use a real RCFG example

Attributes per object in Configuration:

Cameras:

- type: type of the camera [PERSP, ORTHO, PANO]
- position: position of the camera in the scene in world coordinates
- focal_length: focal length of the camera (default: 50)
- target: target the camera is aiming at (default: [0,0,0])

Lights:
- type: type of the ligh [POINT, SUN, SPOT, AREA]
- position: position of the light in the scene in world coordinates
- intensity: intensity of the light (default: 1000)
- target: target the light is aiming at [only useful for directional lights](default: [0,0,0]) 