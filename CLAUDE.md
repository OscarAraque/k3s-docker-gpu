# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a minimal test project for deploying GPU-enabled Docker containers to a k3s cluster running on host 'p7' with an NVIDIA GeForce GTX 1060 6GB GPU.

## Key Commands

### Build and Deploy
- Build Docker image: `./build.sh`
- Deploy to k3s on p7: `./deploy.sh`
- Check deployment: `ssh user@p7 'sudo kubectl get pods -l app=gpu-test'`
- View logs: `ssh user@p7 'sudo kubectl logs -l app=gpu-test -f'`
- Delete deployment: `ssh user@p7 'sudo kubectl delete deployment gpu-test'`

### Image Transfer (if building locally)
```bash
scp gpu-test.tar user@p7:/tmp/
ssh user@p7 'docker load -i /tmp/gpu-test.tar'
ssh user@p7 'sudo k3s ctr images import /tmp/gpu-test.tar'
```

## Architecture

### Components
- **Dockerfile**: NVIDIA CUDA 11.8 base image with Python and PyTorch for GPU testing
- **gpu_test.py**: Tests GPU availability, reports specs, runs benchmarks, stays running for monitoring
- **deployment.yaml**: k8s manifest with GPU resource requests, node selector for p7, and GPU tolerations
- **build.sh**: Builds Docker image and creates tar for transfer
- **deploy.sh**: Deploys to k3s via SSH to p7

### Deployment Strategy
- Uses `imagePullPolicy: Never` to use local images
- Targets p7 node specifically via `nodeSelector`
- Requests 1 GPU via `nvidia.com/gpu: 1` resource limit
- Includes NVIDIA environment variables for GPU visibility

## Important Considerations
- The p7 host must have NVIDIA drivers and k3s NVIDIA device plugin installed
- SSH access to p7 is required for deployment
- The container stays running indefinitely for monitoring purposes
- GPU test performs matrix multiplication benchmarks to verify CUDA functionality