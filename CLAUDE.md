# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This project demonstrates GPU-enabled Docker containers for k3s clusters, using UV for Python dependency management and NVIDIA CUDA for GPU acceleration. Target deployment is host 'p7' with NVIDIA GeForce GTX 1060 6GB.

## Key Commands

### Dependency Management (UV)
- Generate lock file: `uv lock`
- Add dependency: `uv add <package>`
- Update dependencies: `uv lock --upgrade`
- Verify lock file: `uv lock --check`

### Build and Run
- Build Docker image: `./build.sh`
- Run container: `./run.sh`
- Run detached: `docker run -d --name gpu-test --gpus all gpu-uv-test:latest`

### K3s Deployment
- Save image: `docker save gpu-uv-test:latest -o gpu-uv-test.tar`
- Transfer to p7: `scp gpu-uv-test.tar user@p7:/tmp/`
- Import to k3s: `ssh user@p7 'sudo k3s ctr images import /tmp/gpu-uv-test.tar'`
- Deploy: `kubectl apply -f deployment.yaml`
- Check pods: `kubectl get pods -l app=gpu-uv-test`
- View logs: `kubectl logs -l app=gpu-uv-test -f`

## Architecture

### Components
- **Dockerfile**: Multi-stage build with NVIDIA CUDA 12.2 and UV-managed Python 3.12
- **pyproject.toml**: Single source of truth for dependencies (CuPy, NumPy, psutil)
- **uv.lock**: Locked dependency versions for reproducible builds
- **src/gpu_test.py**: GPU testing script with benchmarks and continuous monitoring
- **deployment.yaml**: K3s manifest with GPU resources and p7 node selector
- **build.sh**: Build script that checks for uv.lock and builds image
- **run.sh**: Run script with GPU support detection

### Deployment Strategy
- Uses `imagePullPolicy: Never` to use local images
- Targets p7 node specifically via `nodeSelector`
- Requests 1 GPU via `nvidia.com/gpu: 1` resource limit
- Includes NVIDIA environment variables for GPU visibility

## Important Considerations

### Dependency Management
- All Python dependencies MUST be defined in `pyproject.toml` only (DRY principle)
- Never use requirements.txt - it duplicates information
- Always commit `uv.lock` for reproducible builds
- Run `uv lock` after any dependency changes

### Technical Requirements
- p7 host must have NVIDIA drivers and k3s NVIDIA device plugin
- Docker needs NVIDIA Container Toolkit for GPU support
- Runtime image uses cuda:12.2.0-devel (not runtime) for CuPy JIT compilation
- Container runs continuously for monitoring purposes

### UV and Python Management
- UV manages Python installation (no system Python needed)
- Virtual environment created with: `uv venv .venv --python 3.12`
- Dependencies synced with: `uv sync --frozen --no-install-project`
- This ensures exact reproducibility across all environments