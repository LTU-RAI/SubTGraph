#!/bin/bash

IMAGE_NAME="fernand0labra/subtgraph:latest"
CONTAINER_NAME="subtgraph"

WORKSPACE="~/rai-subtgraph"

# docker build -t $IMAGE_NAME .
if [ $(docker ps -q -f name=$CONTAINER_NAME) ]; then
    echo "Stopping the existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

echo "Running the Docker container..."
docker run -itd --gpus all \
    --env NVIDIA_DRIVER_CAPABILITIES=all \
    --mount type=bind,source=$WORKSPACE,target="/workspace/rai-subtgraph" \
    --name $CONTAINER_NAME \
    $IMAGE_NAME
