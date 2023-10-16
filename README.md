<h3 align="center"> LLM: deployment refactorization for GGUF quantization</h3>
<h4 align="center"> Isaac W. N. Xu and Rui Cheng</h4>

### File structure

```txt
├── data
│   ├── feature
│   │   └── os-1.txt
│   ├── raw
│   │   └── os-1.pdf
│   ├── READEME.md
│   └── transform
├── db
│   └── 648a1b18-a507-40c3-8cf6-c417c2675127
├── docker
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── model
│   ├── model_download.sh
│   └── README.md
├── notebook
│   └── trial.ipynb
├── params.yaml
├── README.md
├── requirements_dev.txt
├── requirements_GGML.txt
├── setup.sh
└── src
    ├── app.py
    ├── main.py
    ├── summarizer.py
    └── test_app.py
```

### Native Deployment on Linux

- Assuming Ubuntu 22.04, install Docker:

```sh
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release 
sudo mkdir -p /etc/apt/keyrings 
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 
    
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
    
sudo apt-get update 
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin 

sudo groupadd docker
sudo usermod -aG docker $USER
sudo gpasswd -a $USER docker

source ~/.bashrc
```

- Make sure you log-off and log back in, download the following image for testing and following dev

```sh
docker pull nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
```

- Assuming Ubuntu or PopOS 22.04, install NV-driver (*version 535.113.01*)
  - PopOS 22.04 should bring NV-driver (*version 535.104.01*) out of the box
  - If not, see [here](https://ubuntu.com/server/docs/nvidia-drivers-installation)

- Assuming Ubuntu or PopOS 22.04, install ICC, GCC, and Intel-MKL

```sh
sudo apt-get install -y libavfilter-dev cargo libpoppler-cpp-dev libmagick++-dev librsvg2-dev tesseract-ocr-eng libtesseract-dev libleptonica-dev libgmp3-dev libcurl4-gnutls-dev libv8-dev  libssl-dev libjpeg62 libxml2-dev libcairo2-dev libudunits2-dev libgeos-dev libgdal-dev clang gcc g++ libmpfr-dev libssh2-1-dev libgit2-dev xdotool xclip libcupti-dev libglu1-mesa-dev freeglut3-dev  mesa-common-dev gfortran libx11-dev libmkl-dev libboost-all-dev libmlpack-dev libboost-test-dev  libboost-serialization-dev libarmadillo-dev binutils-dev
```

- Assuming Ubuntu or Popos 22.04, install CUDA-12.2

```sh
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
cd ~ && wget https://developer.download.nvidia.com/compute/cuda/12.2.2/local_installers/cuda-repo-ubuntu2204-12-2-local_12.2.2-535.104.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-2-local_12.2.2-535.104.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

echo $'\n' >> ~/.bashrc
echo $'#cuda \n' >> ~/.bashrc
echo $'export PATH=\"/usr/local/cuda-12.2/bin:$PATH\" \n' >> ~/.bashrc
echo $'export LD_LIBRARY_PATH=\"/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH\" \n' >> ~/.bashrc

source ~/.bashrc
```

- Assuming Ubuntu or PopOS 22.04, install Python via miniconda or APT

```sh
cd ~

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh

source ~/miniconda3/etc/profile.d/conda.sh

conda activate
```

- Assuming Ubuntu or Popos 22.04, install NV-Docker

```sh
distribution="ubuntu22.04" \
&& curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
&& curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2 nvidia-container-toolkit && source ~/.bashrc && sudo systemctl restart docker
    
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo usermod -aG docker $USER
```

- Testing Docker, NV-Docker, and CUDA (you should see the NV-SMI table in the terminal)

```sh
docker run --rm --gpus all nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 nvidia-smi
```

- Clone the repo to `/root` folder for public accessibility:
 
```sh
sudo -s

mkdir -p /root/source
mkdir -p /root/doc-sum
mkdir -p /root/doc-sum/error
mkdir -p /root/doc-sum/in
mkdir -p /root/doc-sum/log
mkdir -p /root/doc-sum/model
mkdir -p /root/doc-sum/out
mkdir -p /root/doc-sum/process

cd /root/source 

git clone https://github.com/isaac2math/langchain_llamacpp_GGUF.git
```

- Download a pretrained-LLM (make sure you are using the smallest model for testing purpose)

```sh
cd /root/doc-sum/model 
wget https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q2_K.gguf
```

- Docker operations
  - docker build using `/root/source/langchain_llamacpp_GGUF/Dockerfile`
  - install docker-compose `apt install docker-compose`
  - docker-compose using `/root/source/langchain_llamacpp_GGUF/docker-compose.yml`
  - *Doc Flow*
    - the raw txt goes to `/root/doc-sum/in`
    - the processed one will be moved to `/root/doc-sum/process`
    - the one causing error will be moved to `/root/doc-sum/error`
    - the one with successful summarization will be moved to `/root/doc-sum/out`
    - the log will be saved at `/root/doc-sum/log`

#### Usage

- Currently this repo relies on
  - `langchain`
  - `llama-cpp`
  - `chroma`
  - `sbert`


#### Roadmap

- [x] Replace GGML with GGUF
- [x] Use NV-GPU for knowledge graph decomposition for speedup
- [x] Balance the CPU-GPU workload
- [ ] Customize prompts 


#### Contact

Isaac N. Xu - [@email](xuningandy@gmail.com)

