# SynthNet Rendering Pipeline

The purpose of the rendering pipeline is to parse a Blender file and export gltf-scenes for each of a machines' assemblys and single components to render multiple images for each part in order to create an image based search index from them.

## Getting Started

## Configuration

The configuration determines the scene setup for each machine part. It describes cameras, lights and materials. A configuration file must follow the [Config Schema](https://gitlab.beuth-hochschule.de/iisy/SynthNet/rendering-pipeline/-/blob/main/schemas/schema_cfg.json). 

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

## Rendering

The rendering pipeline starts with an exported .blend file containing the hierarchy of a given machine or machine part and a config file containing
different options to create scenes. The output are the gltf files.

``` blender -b -P ./export_gltfs.py -- --config /path/to/config --output_directory path/to/output```

We then render the gltf files by simply importing them and rendering assuming we have the correct lighting in each.

``` blender -b -P ./render.py -- --input_directory /path/to/gltf_files --output_directory /path/to/output_dir --resolution_x 512 --resolution_y 512 --output_quality 100 --output_format JPEG --engine BLENDER_EEVEE```
