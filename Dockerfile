# Base Image
FROM nytimes/blender:3.0-gpu-ubuntu18.04

# Install dependencies
RUN apt update && \
    pip install numpy==1.22.* \
    pip install pandas==1.4.* \
    pip install openpyxl==3.0.* \
    pip install click==8.0.* \
    pip install jsonschema==4.0.*

# Change working directory
WORKDIR /workspace
# Copy project files into workspace
COPY . .
# ENV PYTHONPATH "${PYTHONPATH}:/workspace/src"
