# K3s Docker GPU Project

A production-ready setup for running GPU-accelerated Python workloads in Docker containers on K3s clusters.

## Overview

This project demonstrates how to:
- Build Docker containers with NVIDIA GPU support
- Use UV for Python dependency management
- Deploy GPU workloads to K3s clusters
- Test and monitor GPU performance

## Features

- 🐍 **Python 3.12** with UV package manager
- 🎮 **NVIDIA CUDA 12.2** support
- 📦 **CuPy** for GPU-accelerated computing
- 🚀 **K3s** deployment ready
- 🔧 **Multiple Dockerfile options** for different use cases
- 📊 **Comprehensive GPU testing and monitoring**

## Prerequisites

- NVIDIA GPU with drivers installed (tested on GTX 1060 6GB)
- Docker with NVIDIA Container Toolkit
- Python 3.12+ for local development
- K3s cluster with NVIDIA device plugin (for deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd k3s-docker-gpu
```

### 2. Build the Docker Image

```bash
# Build with UV package management
docker build -f Dockerfile -t gpu-uv-test:latest .
```

### 3. Run Locally

```bash
# Test GPU functionality
docker run --rm --gpus all gpu-uv-test:latest
```

### 4. Deploy to K3s

```bash
# Load image to K3s
sudo k3s ctr images import gpu-uv-test.tar

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=gpu-uv-test
kubectl logs -l app=gpu-uv-test -f
```

## Project Structure

```
k3s-docker-gpu/
├── Dockerfile              # Main Dockerfile with UV and CUDA support
├── requirements.txt        # Python dependencies
├── pyproject.toml         # UV/Python project configuration
├── src/
│   └── gpu_test.py        # GPU testing and monitoring script
├── deployment.yaml        # K3s deployment manifest
├── CLAUDE.md             # Documentation for Claude AI assistance
└── .claude/              # Claude AI project configuration
    └── settings.json     # Project settings
```

## Docker Images

Multiple Dockerfile options are available:

- `Dockerfile` - Production image with UV package management and CUDA development tools
- `Dockerfile.runtime` - Lighter runtime-only image (if you don't need compilation)
- `Dockerfile.multistage` - Multi-stage build for smallest final image

## GPU Testing

The included `gpu_test.py` script performs:

1. **Environment verification** - Python version, virtual environment, system resources
2. **NVIDIA driver check** - GPU detection and driver information
3. **CUDA/CuPy tests** - GPU compute capability and memory information
4. **Performance benchmarks** - Matrix multiplication performance tests
5. **Continuous monitoring** - Real-time GPU utilization tracking

## Dependencies

Managed via UV in `requirements.txt`:
- `cupy-cuda12x` - GPU acceleration library
- `numpy<2.0` - Numerical computing (compatible version)
- `psutil` - System monitoring

## Development

### Local Setup with UV

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv --python 3.12

# Install dependencies
uv pip install -r requirements.txt

# Run tests
python src/gpu_test.py
```

### Building for Different CUDA Versions

Edit `requirements.txt` to use different CuPy versions:
- `cupy-cuda11x` for CUDA 11.x
- `cupy-cuda12x` for CUDA 12.x

## Deployment

### K3s Prerequisites

1. Install NVIDIA drivers on the host
2. Install NVIDIA Container Toolkit
3. Install K3s with GPU support
4. Deploy NVIDIA device plugin to K3s

### Deployment Configuration

The `deployment.yaml` includes:
- GPU resource requests (`nvidia.com/gpu: 1`)
- Node selector for specific hosts
- Environment variables for CUDA
- Tolerations for GPU nodes

## Monitoring

View GPU utilization:
```bash
# On host
nvidia-smi

# In container
docker exec <container-id> nvidia-smi

# In K3s pod
kubectl exec <pod-name> -- nvidia-smi
```

## Troubleshooting

### GPU Not Detected

1. Verify NVIDIA drivers: `nvidia-smi`
2. Check Docker GPU support: `docker run --rm --gpus all nvidia/cuda:12.2.0-base nvidia-smi`
3. Ensure NVIDIA Container Toolkit is installed

### Build Issues

- Use `Dockerfile` with devel image for CUDA compilation support
- Check internet connectivity for package downloads
- Increase Docker build timeout for slow connections

### K3s Deployment Issues

1. Check pod status: `kubectl describe pod <pod-name>`
2. Verify GPU resources: `kubectl describe node <node-name> | grep nvidia`
3. Check device plugin: `kubectl get pods -n kube-system | grep nvidia`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test GPU functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [UV](https://github.com/astral-sh/uv) for fast Python package management
- Uses [CuPy](https://cupy.dev/) for GPU acceleration
- Deployed on [K3s](https://k3s.io/) lightweight Kubernetes