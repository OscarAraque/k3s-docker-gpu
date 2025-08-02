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

### 2. Generate Lock File (First Time Setup)

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Generate uv.lock from pyproject.toml
uv lock
```

### 3. Build the Docker Image

```bash
# Build with UV-managed Python and locked dependencies
./build.sh

# Or manually:
docker build -t gpu-uv-test:latest .

# The build process:
# - Requires uv.lock file (generated in step 2)
# - Uses multi-stage build for optimization
# - Installs Python 3.12 via UV (no system Python)
# - Syncs exact dependencies from lock file
```

### 4. Run Locally

```bash
# Test GPU functionality (interactive)
./run.sh

# Or manually:
docker run --rm --gpus all gpu-uv-test:latest

# Run in detached mode for continuous monitoring
docker run -d --name gpu-test --gpus all gpu-uv-test:latest

# View logs
docker logs -f gpu-test

# Stop and remove
docker stop gpu-test && docker rm gpu-test
```

### 5. Deploy to K3s

```bash
# Save image for transfer to K3s node
docker save gpu-uv-test:latest -o gpu-uv-test.tar

# Transfer to K3s node (e.g., p7)
scp gpu-uv-test.tar user@p7:/tmp/

# Load image on K3s node
ssh user@p7 'sudo k3s ctr images import /tmp/gpu-uv-test.tar'

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=gpu-uv-test
kubectl logs -l app=gpu-uv-test -f
```

## Project Structure

```
k3s-docker-gpu/
├── Dockerfile              # Multi-stage build with UV-managed Python
├── pyproject.toml         # Project dependencies and metadata
├── uv.lock               # Locked dependency versions (generated)
├── src/
│   ├── __init__.py       # Package marker
│   └── gpu_test.py       # GPU testing and monitoring script
├── build.sh             # Build Docker image
├── run.sh               # Run Docker container
├── deployment.yaml      # K3s deployment manifest
├── LICENSE              # MIT License
├── README.md            # This file
├── CLAUDE.md           # Documentation for Claude AI
└── .claude/            # Claude AI configuration
    └── settings.json   # Project settings
```

## Docker Build Details

The main `Dockerfile` uses a multi-stage build approach:

### Stage 1: Builder
- Base: `nvidia/cuda:12.2.0-devel-ubuntu22.04`
- Installs UV package manager from official image
- Uses UV to install Python 3.12 (no system Python needed!)
- Creates virtual environment: `uv venv .venv --python 3.12`
- Syncs exact dependencies: `uv sync --frozen --no-install-project`

### Stage 2: Runtime
- Base: `nvidia/cuda:12.2.0-devel-ubuntu22.04` (includes CUDA headers for CuPy JIT)
- Copies only the virtual environment from builder
- Copies UV-managed Python installation
- Minimal system dependencies (ca-certificates, libssl3)
- Results in optimized image with full GPU support

### Key Features:
- **Single source of truth**: Dependencies only in `pyproject.toml`
- **Reproducible builds**: `uv.lock` pins exact versions with hashes
- **UV-managed Python**: No system Python packages required
- **CUDA JIT support**: Development headers included for CuPy compilation
- **Multi-stage optimization**: Build artifacts not in final image

## GPU Testing

The included `gpu_test.py` script performs:

1. **Environment verification** - Python version, virtual environment, system resources
2. **NVIDIA driver check** - GPU detection and driver information
3. **CUDA/CuPy tests** - GPU compute capability and memory information
4. **Performance benchmarks** - Matrix multiplication performance tests
5. **Continuous monitoring** - Real-time GPU utilization tracking

## Dependencies

All dependencies are defined in `pyproject.toml` and locked in `uv.lock`:
- `cupy-cuda12x>=13.0.0` - GPU acceleration library for CUDA 12.x
- `numpy<2.0` - Numerical computing (compatible version)
- `psutil>=5.9.0` - System and process monitoring

The lock file ensures reproducible builds with exact versions and cryptographic hashes.

## Development

### Local Setup with UV

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.12 using UV (no system Python needed!)
uv python install 3.12

# Create virtual environment
uv venv --python 3.12

# Sync dependencies from lock file
uv sync

# Activate environment and run tests
source .venv/bin/activate
python src/gpu_test.py
```

### Managing Dependencies

```bash
# Add a new dependency to pyproject.toml
uv add <package-name>

# Remove a dependency
uv remove <package-name>

# Update lock file with latest compatible versions
uv lock --upgrade

# Update specific package only
uv lock --upgrade-package <package-name>

# Verify lock file is up to date
uv lock --check

# After any changes, rebuild Docker image
./build.sh
```

### Building for Different CUDA Versions

Edit `pyproject.toml` to use different CuPy versions:
- `cupy-cuda11x` for CUDA 11.x
- `cupy-cuda12x` for CUDA 12.x (current)

Then regenerate the lock file:
```bash
uv lock
```

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
3. Ensure NVIDIA Container Toolkit is installed:
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

### Build Issues

- **Missing uv.lock**: Run `uv lock` to generate it
- **Slow dependency downloads**: UV caches packages, subsequent builds are faster
- **CUDA compilation errors**: Ensure using `cuda:12.2.0-devel` base image (not runtime)
- **Out of space**: Clean Docker cache with `docker system prune`

### Runtime Issues

- **CuPy compilation errors**: The runtime needs CUDA headers, use devel image
- **Memory errors**: Reduce matrix size in gpu_test.py or add memory limits
- **Python version mismatch**: UV manages Python 3.12, ensure consistency

### K3s Deployment Issues

1. Check pod status: `kubectl describe pod <pod-name>`
2. Verify GPU resources: `kubectl describe node <node-name> | grep nvidia`
3. Check device plugin: `kubectl get pods -n kube-system | grep nvidia`
4. Image not found: Ensure image is imported with `k3s ctr images import`

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