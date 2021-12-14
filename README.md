# SynthNet Rendering Pipeline

The purpose of the rendering pipeline is to parse a Blender file and export gltf-scenes for each of a machines' assemblys and single components to render multiple images for each part in order to create an image based search index from them.

## Getting Started

## Configuration

The configuration determines the scene setup for each machine part. It describes cameras, lights and materials. A configuration file must follow the [Config Schema](https://gitlab.beuth-hochschule.de/iisy/SynthNet/rendering-pipeline/-/blob/main/schemas/schema_cfg.json). 