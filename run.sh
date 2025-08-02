#!/bin/bash

set -e

IMAGE_NAME="${IMAGE_NAME:-gpu-uv-test}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CONTAINER_NAME="${CONTAINER_NAME:-gpu-test}"

echo "=== Running GPU Docker Container ==="
echo ""

# Check if image exists
if ! docker images -q ${IMAGE_NAME}:${IMAGE_TAG} 2>/dev/null | grep -q .; then
    echo "❌ Image ${IMAGE_NAME}:${IMAGE_TAG} not found!"
    echo ""
    echo "Please build it first:"
    echo "  ./build.sh"
    exit 1
fi

# Check for GPU support
if ! docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "⚠️  GPU support not available!"
    echo "Please ensure:"
    echo "  1. NVIDIA drivers are installed"
    echo "  2. NVIDIA Container Toolkit is installed"
    echo "  3. Docker daemon is configured for GPU"
    echo ""
fi

# Stop existing container if running
if docker ps -q -f name=${CONTAINER_NAME} 2>/dev/null | grep -q .; then
    echo "Stopping existing container..."
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
fi

# Run the container
echo "Starting container with GPU support..."
docker run \
    --name ${CONTAINER_NAME} \
    --gpus all \
    --rm \
    -it \
    ${IMAGE_NAME}:${IMAGE_TAG}

echo ""
echo "Container exited."