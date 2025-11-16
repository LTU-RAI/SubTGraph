# Variables
$DOCKER_LOCATION = "/home/blender"
$CONTAINER_NAME = "subtgraph"
$IMAGE_NAME = "fernand0labra/blender:subtgraph"

# Check if container exists
$existingContainer = docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.ID}}"

if ($existingContainer) {
    Write-Host "Removing existing container $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
} else {
    Write-Host "Container $CONTAINER_NAME does not exist."
}

# Run Docker container
docker run --gpus all --cpus 16 `
    --mount type=volume,src=cuda-vscode-server,dst="$DOCKER_LOCATION/.vscode-server" `
    --mount type=volume,src=cuda-ssh,dst="$DOCKER_LOCATION/.ssh" `
    --mount type=bind,source="C:/Users/YourUsername/SubTGraph",target="$DOCKER_LOCATION/SubTGraph" `
    --name $CONTAINER_NAME `
    --shm-size 8GB `
    --ipc host `
    --publish 127.0.0.1::22 `
    -itd $IMAGE_NAME
