# MetaWorm

Welcome to MetaWorm, an **integrative data-driven model of *C. elegans***, linking brain, body and environment to faithfully replicate *C. elegans* locomotion behavior.    
For a comprehensive introduction to MetaWorm, please refer to our paper available at [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.02.22.581686v2).

### Components:
**eworm:** The neural network model  
**MetaWorm:** The body & environment model  
**neuroXcore:** 3D visualization for the neural network model  

## Table of Contents
* [Background](#background)  
* [System Requirements](#system-requirements)  
* [Installation Guide](#installation-guide)  
* [Demo](#demo)  
* [Instructions for Use](#instructions-for-use)  
* [License](#license)  

## Background
The behavior of an organism is profoundly influenced by the complex interplay between its brain, body, and environment. Existing data-driven models focusing on either the brain or the body-environment separately. A model that integrates these two components is yet to be developed. Here, we present MetaWorm, an integrative data-driven model of a widely studied organism, *C. elegans*. This model consists of two sub-models: the brain model and the body & environment model. The brain model was built by multi-compartment models with realistic morphology, connectome, and neural population dynamics based on experimental data. Simultaneously, the body & environment model employed a lifelike body and a 3D physical environment, facilitating easy behavior quantification. Through the closed-loop interaction between two sub-models, MetaWorm faithfully reproduced the realistic zigzag movement towards attractors observed in *C. elegans*. Notably, MetaWorm is the first model to achieve seamless integration of detailed brain, body, and environment simulations, enabling unprecedented insights into the intricate relationships between neural structures, neural activities, and behaviors. Leveraging this model, we investigated the impact of neural system structure on both neural activities and behaviors. Consequently, MetaWorm can enhance our understanding of how the brain controls the body to interact with its surrounding environment. 

## System Requirements
To ensure optimal performance and compatibility, we recommend installing and running MetaWorm on Ubuntu. Below are the tested specifications:   
- OS: Ubuntu 20.04    
- GPU: Nvidia 3090     
- CUDA: 11.4  
- Python 3.8.x  
- Nvidia Optix: 7.0.0

## Installation Guide
### Get code
```
sudo apt install git
git clone https://github.com/Jessie940611/MetaWorm.git
```
### C++ 
#### Basic C++ library
```
sudo apt update
sudo apt install cmake libpython3-dev python3-pip libeigen3-dev libgl-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev freeglut3-dev libglew-dev 
```
#### Build Boost from source (Boost 1.79 tested)
get Boost
```
wget https://boostorg.jfrog.io/artifactory/main/release/1.79.0/source/boost_1_79_0.tar.gz
```
build and install boost to path you want
```
tar -xzf boost_1_79_0.tar.gz
cd boost_1_79_0
./bootstrap.sh --with-python=python3
./b2 --with-python --with-filesystem --with-system --prefix="YOUR_BOOST_PATH" install
```
### Build
```
cd PROJECT_ROOT_DIR
mkdir build
cd build 
cmake ../neuronXcore -G"Unix Makefiles" -DCUDA_TOOLKIT_ROOT_DIR="path to cuda root" -DOptiX_INCLUDE="path to optix library/include" -DBoost_DIR="path to BoostConfig.cmake"
make -j8
```
### Python
#### change build path in `worm_in_env.py`
```
cd MetaWorm/eworm/ghost_in_mesh_sim/
# change line 3 in worm_in_env.py to add the `build` dir in your PC
sys.path.append('[directory of build]')
```
#### install Python packages
```
pip install -r requirements.txt
```
#### create an NMODL mechanism library
```
cd MetaWorm/eworm/components/mechanism
nrnivmodl modfile
```
If you get "Command 'nrnivmodl' not found", find it in `/home/[username]/.local/bin`
## Demo
Experience the simulation of *C. elegans* movement with our demo.   
Execute the open-loop simulation of *C. elegans* movement.
```
cd MetaWorm/build
./neuronXcore -data ../eworm/ghost_in_mesh_sim/data/tuned/video_offline/video_offline_neuronX
```
It you get "No module named xxx", try
```
export PYTHONPATH=~/MetaWorm/
```

## Instructions for Use
### Modify the Neural Network Model of MetaWorm
#### Modify any parameters of the model
Adjust the parameters of the neural network model by modifying the respective files.
```
├── components
│   ├── mechanism      # ion channel models
│   ├── model          # cell models, including morphology and locations of cells
│   ├── param
│   │   ├── cell       # biophysical parameters of cells
│   │   ├── connection # adjacency matrix
├── network
│   ├── config.json    # network config
```
Run the script to generate a neural network model
```
python test.py
```
#### Fitting the neural network data
The `eworm_learn` file contains code to training the neural network model to fit the target data. The target data can be Preason Correlation Matrix of neurons' membrane potentials, or the Calcium signals of neurons. This training algorithm requires GPUs to run and supports multiple GPUs.   
   
(If you add or change an ion channel model X, you need to make the correspoding X_lr.mod file in `/MetaWorm/eworm_learn/components/mechanism/modfile/` for training)  

Create an NMODL mechanism library
```
cd /MetaWorm/eworm_learn
nrnivmodl components/mechanism/modfile
```
Train the model
```
./x86_64/special run_eworm_v4.py
```
Before training, configure the parameters in `run_eworm_v4.py`
```
TARGET_MODE: 'corr' - fit the correlation matrix of neurons' membrane potentials; 'traces' - fit neurons' membrane potentials
PERCISE: True - more precise, but costs more memory and time; False - less precise, but save memory and time
ADAM: True - used Adam as optimizer，False - use SGD
ngpu: number of GPUs
K_nblock: Transfer impedance matrix division block number; larger values save more memory, with a maximum equal to the number of neurons.
```
### Modify the interaction between the Neural Network Model and the Body & Environment Model
#### Train the neural network to control the body
```
cd MetaWorm/eworm/ghost_in_mesh_sim
# set parameters in 02_train_cnn.py
python 02_train_cnn.py
```
#### Run the simulation of *C. elegans* movement
To run the simulation in GUI and render the neural network model, you need to export the morphological data of your neural network model.
```
cd MetaWorm/eworm/ghost_in_mesh_sim
# Set parameters in 03_make_morph.py
python 03_make_morph.py
```
Set parameters in `worm_in_env.py`, like `group_name` and parameters in `config`.
If you want to do perturbation experiment, replace the corresponding function in line 58 of `worm_neural_network.py`.
Run the simulation of *C. elegans* movement.
```
./neuronXcore -data [directory of your morphological data]
```
### 3D User Interface Interaction
#### Mouse
Rotatation with mouse right key   
Zoom with mouse middle key
#### Keyboard
space : Play & Pause.   
'r': reset worm.   
't': tetrahedron mesh of worm body(FEM).   
'w': worm body.   
'm': worm muscles(96 muscles).   
'p': path of swimming trajectory.   
'a': arrow of worm swimming direction (yellow arrow)   
'x': coordinate of world. x-red arrow. y-green arrow. z-blue arrow.   
'c': coordinate of worm body & head. x-red arrow. y-green arrow. z-blue arrow.   
'q': exit   

## License
This project is covered under the Apache 2.0 License.   
[BAAI](https://www.baai.ac.cn/)
