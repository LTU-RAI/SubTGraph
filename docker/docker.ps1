# Ensure Docker is running
$dockerStatus = docker info

if (-not $dockerStatus) {
    Write-Host "Docker is not running. Starting Docker..."
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 10
}

$imageName = "fernand0labra/subtgraph:latest"
$containerName = "subtgraph"
$workspace = "C:\Users\usuario\rai-subtgraph"

$existingContainer = docker ps -a | Select-String -Pattern $containerName

if ($existingContainer) {
    Write-Host "Container $containerName already exists. Removing it..."
    docker rm -f $containerName
}

# Run the container
Write-Host "Initializing Docker container: $containerName from image $imageName"
docker run -itd \
    --mount type=bind,source=$WORKSPACE,target="/workspace/rai-subtgraph" \
    --env NVIDIA_DRIVER_CAPABILITIES=all \
    --name $containerName \
    $imageName

$containerStatus = docker ps -f "name=$containerName"

if ($containerStatus) {
    Write-Host "Container $containerName is up and running."
} else {
    Write-Host "Failed to start container $containerName."
}
