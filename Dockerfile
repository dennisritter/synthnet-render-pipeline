# Base Image
FROM nytimes/blender:3.0-gpu-ubuntu18.04


ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN apt-get update
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

# Change working directory
WORKDIR /workspace
# Copy project files into workspace
COPY . .

# Install dependencies
RUN conda env create --file environment.yml
# Activate environment on shell init
RUN echo "conda activate py39-synthnet-render-pipeline" >> ~/.bashrc
# RUN conda activate py39-synthnet-render-pipeline

# ENV PYTHONPATH "${PYTHONPATH}:/workspace"
