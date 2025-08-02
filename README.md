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

- NVIDIA GPU with drivers installed (✅ tested on GTX 1060 6GB)
- Docker with NVIDIA Container Toolkit
- Python 3.12+ for local development  
- K3s cluster with nvidia runtime class (✅ working setup)

## Quick Start

🚀 **TL;DR**: For immediate deployment on a working K3s cluster with NVIDIA support:
```bash
./build.sh    # Build the container
./deploy.sh   # Deploy to K3s and test GPU
```

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
# Deploy with automated script (recommended)
./deploy.sh

# Or manually:
# 1. Import image to K3s
docker save gpu-uv-test:latest -o gpu-uv-test.tar
sudo k3s ctr images import gpu-uv-test.tar
rm gpu-uv-test.tar

# 2. Deploy using nvidia runtime
kubectl apply -f deployment.yaml

# 3. Check status
kubectl get pods -l app=gpu-uv-test-simple
kubectl logs -l app=gpu-uv-test-simple -f

# 4. Test GPU access
kubectl exec <pod-name> -- nvidia-smi
kubectl exec <pod-name> -- python3 -c "import cupy as cp; print('GPU available:', cp.cuda.is_available())"
```

## Project Structure

```
k3s-docker-gpu/
├── Dockerfile                    # Multi-stage build with UV-managed Python
├── pyproject.toml               # Project dependencies and metadata
├── uv.lock                     # Locked dependency versions (generated)
├── src/
│   ├── __init__.py             # Package marker
│   └── gpu_test.py             # GPU testing and monitoring script
├── build.sh                    # Build Docker image
├── run.sh                      # Run Docker container locally
├── deploy.sh                   # Deploy to K3s (automated)
├── deployment.yaml             # K3s deployment with nvidia runtime
├── LICENSE                     # MIT License
├── README.md                   # This file
├── CLAUDE.md                   # Documentation for Claude AI
└── .claude/                    # Claude AI configuration
    └── settings.json           # Project settings
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

1. **NVIDIA Drivers**: Install NVIDIA drivers on the host
   ```bash
   # Verify drivers
   nvidia-smi
   ```

2. **NVIDIA Container Toolkit**: Install for Docker/containerd GPU support
   ```bash
   # Configure for Docker
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

3. **K3s with GPU Support**: Install K3s (automatically includes nvidia runtime)
   ```bash
   # K3s installation includes nvidia runtime class by default
   kubectl get runtimeclass
   ```

### Deployment Approaches

### Deployment Configuration

The `deployment.yaml` uses the **NVIDIA Runtime Class approach**:
- `runtimeClassName: nvidia` for direct GPU access
- Host volume mounts for GPU devices (`/dev`, `/usr/lib/x86_64-linux-gnu`)
- No NVIDIA device plugin required
- Reliable GPU access through nvidia-container-runtime
- Standard CPU/memory resource requests (no GPU resource requests)

> **Note**: This approach bypasses the complex NVIDIA device plugin setup and provides direct, reliable GPU access.

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

1. **Pod stuck in Pending**:
   ```bash
   kubectl describe pod <pod-name>
   # Check for scheduling issues, image availability
   ```

2. **GPU not accessible in container**:
   ```bash
   # Test GPU access
   kubectl exec <pod-name> -- nvidia-smi
   
   # Check runtime class
   kubectl get runtimeclass nvidia
   
   # Verify NVIDIA Container Toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   ```

3. **Image not found**:
   ```bash
   # Check image availability
   sudo k3s ctr images list | grep gpu-uv-test
   
   # Import if missing
   docker save gpu-uv-test:latest -o gpu-uv-test.tar
   sudo k3s ctr images import gpu-uv-test.tar
   ```

4. **Runtime class issues**:
   ```bash
   # Verify nvidia runtime class exists
   kubectl get runtimeclass nvidia
   
   # If missing, check NVIDIA Container Toolkit setup
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test GPU functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Success Story

✅ **Deployment Successful!** This project successfully demonstrates:
- GPU-accelerated Python containers with UV dependency management
- Seamless K3s deployment using nvidia runtime class
- CuPy GPU computing in a Kubernetes environment
- Production-ready Docker builds with reproducible dependencies

## Acknowledgments

- Built with [UV](https://github.com/astral-sh/uv) for fast Python package management
- Uses [CuPy](https://cupy.dev/) for GPU acceleration
- Deployed on [K3s](https://k3s.io/) lightweight Kubernetes
- NVIDIA Container Toolkit for seamless GPU integration