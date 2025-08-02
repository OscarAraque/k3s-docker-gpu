#!/bin/bash

set -e

IMAGE_NAME="${IMAGE_NAME:-gpu-uv-test}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "=== Building GPU Docker Image with UV-managed Dependencies ==="
echo ""
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Check if uv.lock exists
if [ ! -f "uv.lock" ]; then
    echo "⚠️  No uv.lock file found!"
    echo ""
    echo "To generate it:"
    echo "  1. Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  2. Generate lock: uv lock"
    echo ""
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
echo "  - Using pyproject.toml for dependency definitions"
echo "  - Using uv.lock for reproducible builds"
echo "  - Multi-stage build for optimization"
echo ""

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    # Show image info
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | head -1
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep ${IMAGE_NAME}:${IMAGE_TAG}
    
    echo ""
    echo "To run the container locally:"
    echo "  ./run.sh"
    echo "  # or manually:"
    echo "  docker run --rm --gpus all ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    echo "To deploy to K3s:"
    echo "  kubectl apply -f deployment.yaml"
    echo ""
    echo "To import into K3s (if needed):"
    echo "  docker save ${IMAGE_NAME}:${IMAGE_TAG} -o ${IMAGE_NAME}.tar"
    echo "  sudo k3s ctr images import ${IMAGE_NAME}.tar"
else
    echo "❌ Build failed!"
    exit 1
fi