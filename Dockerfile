# Base Image
FROM nytimes/blender:3.1-gpu-ubuntu18.04

# Install dependencies
RUN apt update && \
    pip install numpy \
    pip install pandas \
    pip install openpyxl \
    pip install click \
    pip install jsonschema

RUN apt-get -y install git



# ENV PATH="/root/miniconda3/bin:${PATH}"
# ARG PATH="/root/miniconda3/bin:${PATH}"

# RUN rm /etc/apt/sources.list.d/cuda.list
# RUN rm /etc/apt/sources.list.d/nvidia-ml.list

# RUN apt-get update
# RUN apt-get install curl -y
# RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
# RUN wget \
#     https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#     && mkdir /root/.conda \
#     && bash Miniconda3-latest-Linux-x86_64.sh -b \
#     && rm -f Miniconda3-latest-Linux-x86_64.sh
# RUN conda --version

# # Install gcloud CLI
# RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-cli -y

# # # Change working directory
# # WORKDIR /workspace
# # # Copy project files into workspace
# # COPY . .

# # Install dependencies
# RUN conda env create --file environment.yml
# # Activate environment on shell init
# RUN echo "conda activate py39-synthnet-rendering-pipeline" >> ~/.bashrc
# RUN conda activate py39-synthnet-render-pipeline

# ENV PYTHONPATH "${PYTHONPATH}:/workspace"
