<p align="center">
  <img src="imgs/subtgraph.png" style="width:80%; height:auto;"/>
</p>
<p align="center">
  <img src="imgs/Figure5.jpg" style="width:80%; height:auto;"/>
</p>

This is the code repository of SubTGraph, an underground world generator for statistical evaluation of robotic techniques. This tool is governed by the user-specified configuration that allows the creation of object meshes with different levels, topologies, textures, widths and lengths.

## Installation
The repository can be installed as a standalone Python package or deployed as a Docker container.

### Python package
This method of installation allows the user to work in a Python environment by simply installing the package. The definition of the package includes all required dependencies that the code utilizes.
```
# Clone repository
cd ~ & git clone https://github.com/fernand0labra/rai-subtgraph.git

# Install package
cd ~/rai-subtgraph & python3 -m pip install -e .  --config-settings editable_mode=compat
```

### Container deployment
Docker allows for any machine and operative system to execute this tool by simply pulling an image. All dependencies are included and the repository is mounted during runtime to allow configuration changes from the user.
```
# Pull image from Docker Hub
docker pull fernand0labra/rai-subtgraph:latest

# Clone repository
cd ~ & git clone https://github.com/fernand0labra/rai-subtgraph.git

# Start container "subtgraph"
bash ~/rai-subtgraph/docker/docker.sh

# Connect to container terminal
docker exec -it subtgraph bash
```


## Subterranean World Generation
TODO
<img src="imgs/Figure13.jpg"/>


### User Configuration
TODO
```
# This is my code
```

#### Level Visualization & Selection
TODO
```
# This is my code
```
<img src="imgs/Figure7.jpg"/>
Image

#### Mesh Storage & Reconstruction
TODO
```
# This is my code
```

#### Constraint Definition
TODO
```
# This is my code
```
<img src="imgs/Figure4.png"/>

#### Dimension Controllability
TODO
```
# This is my code
```
<img src="imgs/Figure8.jpg"/>

#### Texture Definition
TODO
```
# This is my code
```
<img src="imgs/Figure6.jpg"/>

## Tutorial Video


## Citation
