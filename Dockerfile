# Base Image
FROM nytimes/blender:3.1-gpu-ubuntu18.04

ARG PYTHON_VERSION=3.9.18

# Install dependencies
RUN apt-get update \
    && apt-get -y install git \
    && apt-get -y install curl

ENV HOME="/root"
RUN curl https://pyenv.run | bash
ENV PYENV_ROOT="$HOME/.pyenv"
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"

RUN apt-get install -y build-essential zlib1g-dev libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev liblzma-dev \
    && pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION

RUN apt update \
    && pip install --upgrade pip \
    && pip install numpy \
    && pip install pandas \
    && pip install openpyxl \
    && pip install click \
    && pip install jsonschema==4.0.*
