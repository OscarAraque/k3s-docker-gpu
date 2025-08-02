# K3s Docker GPU Test

A minimal Docker image to test GPU functionality on a k3s cluster with NVIDIA GPU support.

## Prerequisites

- Docker installed on build machine
- k3s cluster with NVIDIA GPU support installed on p7 host
- NVIDIA Container Toolkit configured on p7
- SSH access to p7 host

## Project Structure

- `Dockerfile` - CUDA-enabled container with Python and PyTorch
- `gpu_test.py` - Python script to test GPU availability and performance
- `deployment.yaml` - Kubernetes deployment manifest for k3s
- `build.sh` - Script to build the Docker image
- `deploy.sh` - Script to deploy to k3s cluster on p7

## Quick Start

### 1. Build the Docker Image

```bash
./build.sh
```

This creates a Docker image tagged as `gpu-test:latest` and saves it to `gpu-test.tar`.

### 2. Transfer Image to p7 (if building locally)

```bash
# Copy the image tar file to p7
scp gpu-test.tar user@p7:/tmp/

# Load the image on p7
ssh user@p7 'docker load -i /tmp/gpu-test.tar'

# Import to k3s container runtime
ssh user@p7 'sudo k3s ctr images import /tmp/gpu-test.tar'
```

### 3. Deploy to k3s

```bash
./deploy.sh
```

### 4. Check Deployment Status

```bash
# Check pod status
ssh user@p7 'sudo kubectl get pods -l app=gpu-test'

# View logs
ssh user@p7 'sudo kubectl logs -l app=gpu-test -f'
```

## What the Test Does

The GPU test script:
1. Checks CUDA availability
2. Lists available GPUs (should show GTX 1060 6GB)
3. Reports GPU memory
4. Performs matrix multiplication benchmarks
5. Monitors memory usage
6. Keeps running for monitoring purposes

## Cleanup

To remove the deployment:

```bash
ssh user@p7 'sudo kubectl delete deployment gpu-test'
```

## Troubleshooting

### GPU Not Detected

If the container doesn't detect the GPU:

1. Verify NVIDIA drivers on p7:
   ```bash
   ssh user@p7 'nvidia-smi'
   ```

2. Check k3s NVIDIA device plugin:
   ```bash
   ssh user@p7 'sudo kubectl get pods -n kube-system | grep nvidia'
   ```

3. Verify node GPU resources:
   ```bash
   ssh user@p7 'sudo kubectl describe node p7 | grep nvidia'
   ```

### Container Fails to Start

Check pod events:
```bash
ssh user@p7 'sudo kubectl describe pod -l app=gpu-test'
```

## Configuration

The deployment is configured to:
- Run on node `p7` specifically (via nodeSelector)
- Request 1 NVIDIA GPU
- Use local image (imagePullPolicy: Never)
- Include GPU tolerations for scheduling