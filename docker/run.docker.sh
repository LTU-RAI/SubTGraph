UNIX=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth

DOCKER_LOCATION="/home/blender"
CONTAINER_NAME="subtgraph"
IMAGE_NAME="fernand0labra/blender:subtgraph"

if [ $(docker container ls -a -q -f name=$CONTAINER_NAME) ]; then
    echo "Removing existing container $CONTAINER_NAME"
	docker container stop $CONTAINER_NAME
    docker container rm $CONTAINER_NAME
else
    echo "Container $CONTAINER_NAME does not exist."
fi

# Windows WSL command
docker run --gpus all --cpus 16 \
			--mount type=volume,src=cuda-vscode-server,dst=${DOCKER_LOCATION}/.vscode-server \
			--mount type=volume,src=cuda-ssh,dst=${DOCKER_LOCATION}/.ssh \
			--mount type=bind,source=/home/fernand0labra/SubTGraph/,target=${DOCKER_LOCATION}/SubTGraph \
			--name ${CONTAINER_NAME} \
			--shm-size 8GB \
			--ipc host \
			--publish 127.0.0.1::22 \
			-itd ${IMAGE_NAME}

# Linux Command
# docker run -itd --gpus all --cpus 16 \
#     --privileged \
#     --env DISPLAY=$DISPLAY \
#     --env QT_X11_NO_MITSHM=1 \
#     --env XAUTHORITY=$XAUTH \
#     --env NVIDIA_DRIVER_CAPABILITIES=all \
#     --volume="$XAUTH:$XAUTH" \
#     --volume="$UNIX:$UNIX:rw" \
#     --mount type=bind,source="/usr/share/vulkan/icd.d",target="/usr/share/vulkan/icd.d" \
#     --mount type=bind,source=/home/fernand0labra/SubTGraph/,target=${DOCKER_LOCATION}/SubTGraph \
#     --name $CONTAINER_NAME \
#     $IMAGE_NAME