# Using UV with requirements.txt file
# Based on https://docs.astral.sh/uv/guides/integration/docker/
# Use devel image instead of runtime for CUDA compilation

FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Set non-interactive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    ca-certificates \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Install uv - using COPY method for better reliability
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy requirements file
COPY requirements.txt .

# Create virtual environment
RUN uv venv .venv --python python3.12

# Install dependencies from requirements.txt
RUN uv pip install --python .venv -r requirements.txt

# Copy application code
COPY src/ ./src/

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV=/app/.venv

# Run the GPU test
CMD ["python", "src/gpu_test.py"]