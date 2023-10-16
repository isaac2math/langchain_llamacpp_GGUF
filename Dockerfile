FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Create working directory
WORKDIR /root/langchain_llama2

# Git clone all the files into docker container
RUN apt-get -y update && apt-get install -y software-properties-common git cmake wget pkg-config tree

# ADD scripts to docker container
COPY . .

# install libs from apt
RUN  add-apt-repository --yes ppa:deadsnakes/ppa && apt install -y python3.10 python3-pip build-essential libssl-dev libffi-dev python3-venv
RUN pip install --upgrade pip

RUN echo $'export LLAMA_CUBLAS=1 \n' >> /root/.bashrc && bash ./setup.sh

ENTRYPOINT ["python3", "src/main.py"]