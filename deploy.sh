#!/bin/bash

set -e

IMAGE_NAME="${IMAGE_NAME:-gpu-uv-test}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "=== Deploying GPU Container to K3s ===="
echo ""
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not available"
    echo "Please ensure K3s is installed and kubectl is configured"
    exit 1
fi

# Check if K3s cluster is running
if ! kubectl get nodes &>/dev/null; then
    echo "❌ Cannot connect to K3s cluster"
    echo "Please ensure K3s is running and configured"
    exit 1
fi

echo "✅ K3s cluster is accessible"

# Check if nvidia runtime class exists
if ! kubectl get runtimeclass nvidia &>/dev/null; then
    echo "❌ NVIDIA runtime class not found"
    echo "Please ensure NVIDIA Container Toolkit is configured for K3s"
    exit 1
fi

echo "✅ NVIDIA runtime class is available"

# Check if image exists locally
if ! docker images -q ${IMAGE_NAME}:${IMAGE_TAG} 2>/dev/null | grep -q .; then
    echo "❌ Image ${IMAGE_NAME}:${IMAGE_TAG} not found locally!"
    echo ""
    echo "Please build it first:"
    echo "  ./build.sh"
    exit 1
fi

echo "✅ Docker image found locally"

# Check if image exists in K3s
if ! sudo k3s ctr images list -q | grep -q "${IMAGE_NAME}:${IMAGE_TAG}"; then
    echo "📦 Importing image to K3s..."
    
    # Export and import image
    docker save ${IMAGE_NAME}:${IMAGE_TAG} -o /tmp/${IMAGE_NAME}.tar
    sudo k3s ctr images import /tmp/${IMAGE_NAME}.tar
    rm /tmp/${IMAGE_NAME}.tar
    
    echo "✅ Image imported to K3s"
else
    echo "✅ Image already available in K3s"
fi

# Deploy the application
echo ""
echo "🚀 Deploying to K3s..."
kubectl apply -f deployment.yaml

echo ""
echo "⏳ Waiting for pod to be ready..."
kubectl wait --for=condition=ready pod -l app=gpu-uv-test-simple --timeout=60s

# Show deployment status
echo ""
echo "📊 Deployment Status:"
kubectl get pods -l app=gpu-uv-test-simple
echo ""

# Get pod name
POD_NAME=$(kubectl get pods -l app=gpu-uv-test-simple -o jsonpath='{.items[0].metadata.name}')

echo "🔍 Testing GPU access in pod..."
if kubectl exec $POD_NAME -- nvidia-smi &>/dev/null; then
    echo "✅ GPU is accessible in the pod!"
    echo ""
    echo "🧪 Testing CuPy GPU functionality..."
    kubectl exec $POD_NAME -- python3 -c "import cupy as cp; print('✅ CuPy version:', cp.__version__); print('✅ GPU detected:', cp.cuda.is_available())"
else
    echo "❌ GPU not accessible in pod"
fi

echo ""
echo "📋 Useful commands:"
echo "  # View logs:"
echo "  kubectl logs $POD_NAME -f"
echo ""
echo "  # Execute commands in pod:"
echo "  kubectl exec $POD_NAME -- nvidia-smi"
echo "  kubectl exec $POD_NAME -it -- bash"
echo ""
echo "  # Delete deployment:"
echo "  kubectl delete -f deployment.yaml"
echo ""
echo "✅ Deployment complete!"