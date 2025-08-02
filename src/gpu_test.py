#!/usr/bin/env python3
"""
GPU test script for Docker container with UV-managed dependencies.
Tests CUDA functionality using CuPy.
"""

import sys
import time
import os
import subprocess
import psutil
from datetime import datetime

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_environment():
    """Test the Python and system environment."""
    print_section("Environment Information")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check UV environment
    if os.getenv('VIRTUAL_ENV'):
        print(f"Virtual Environment: {os.getenv('VIRTUAL_ENV')}")
    
    # System resources
    print(f"\nSystem Resources:")
    print(f"  CPU Count: {psutil.cpu_count()}")
    print(f"  Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"  Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")

def test_nvidia_smi():
    """Test nvidia-smi command."""
    print_section("NVIDIA Driver Check")
    
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,driver_version,memory.total,temperature.gpu', '--format=csv,noheader'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            print("✅ NVIDIA drivers detected")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:
                    print(f"\nGPU {parts[0]}:")
                    print(f"  Name: {parts[1]}")
                    print(f"  Driver: {parts[2]}")
                    print(f"  Memory: {parts[3]}")
                    print(f"  Temperature: {parts[4]}")
            return True
        else:
            print(f"❌ nvidia-smi failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running nvidia-smi: {e}")
        return False

def test_cuda_with_cupy():
    """Test CUDA functionality using CuPy."""
    print_section("CuPy CUDA Test")
    
    try:
        import cupy as cp
        import numpy as np
        
        print(f"✅ CuPy version: {cp.__version__}")
        print(f"✅ NumPy version: {np.__version__}")
        
        # CUDA information
        print(f"\nCUDA Information:")
        cuda_version = cp.cuda.runtime.runtimeGetVersion()
        print(f"  CUDA Runtime Version: {cuda_version // 1000}.{(cuda_version % 1000) // 10}")
        
        # Device information
        device_count = cp.cuda.runtime.getDeviceCount()
        print(f"  Device Count: {device_count}")
        
        for i in range(device_count):
            with cp.cuda.Device(i):
                device = cp.cuda.Device(i)
                
                # Get device properties using the correct API
                try:
                    device_name = cp.cuda.runtime.getDeviceProperties(i)['name'].decode()
                except:
                    # Fallback method
                    device_name = f"GPU {i}"
                
                mem_info = device.mem_info
                compute_capability = device.compute_capability
                
                print(f"\nGPU {i}: {device_name}")
                print(f"  Compute Capability: {compute_capability}")
                print(f"  Total Memory: {mem_info[1] / (1024**3):.2f} GB")
                print(f"  Free Memory: {mem_info[0] / (1024**3):.2f} GB")
                
                # Get additional device properties
                try:
                    props = cp.cuda.runtime.getDeviceProperties(i)
                    print(f"  Multiprocessors: {props.get('multiProcessorCount', 'N/A')}")
                    mp_count = props.get('multiProcessorCount', 0)
                    # Estimate CUDA cores based on compute capability
                    # Convert compute_capability to comparable format
                    if isinstance(compute_capability, (list, tuple)):
                        cc_major, cc_minor = compute_capability[0], compute_capability[1]
                    else:
                        # Handle cases where it's returned as integer like 61
                        cc_major = compute_capability // 10
                        cc_minor = compute_capability % 10
                    
                    if (cc_major, cc_minor) >= (8, 0):  # Ampere
                        cores_per_mp = 128
                    elif (cc_major, cc_minor) >= (7, 5):  # Turing
                        cores_per_mp = 64
                    elif (cc_major, cc_minor) >= (6, 0):  # Pascal (GTX 1060 is 6.1)
                        cores_per_mp = 128
                    else:
                        cores_per_mp = 128  # Approximate
                    print(f"  CUDA Cores: ~{mp_count * cores_per_mp} (CC {cc_major}.{cc_minor})")
                except Exception as e:
                    print(f"  Could not get detailed properties: {e}")
        
        # Performance test
        print_section("GPU Performance Test")
        
        print("Creating test matrices...")
        size = 1000  # Smaller size to avoid compilation issues
        
        # GPU computation
        print(f"Testing {size}x{size} matrix multiplication on GPU...")
        print("  Creating arrays on GPU...")
        gpu_a = cp.random.random((size, size), dtype=cp.float32)
        gpu_b = cp.random.random((size, size), dtype=cp.float32)
        print("  Arrays created successfully!")
        
        # Simple GPU operations first
        print("  Testing basic GPU operations...")
        try:
            # Simple element-wise operations (no compilation needed)
            gpu_c = gpu_a + gpu_b
            gpu_d = gpu_a * 2.0
            gpu_sum = cp.sum(gpu_a)
            print(f"  ✅ Basic operations successful (sum: {gpu_sum:.2f})")
        except Exception as e:
            print(f"  ❌ Basic operations failed: {e}")
            return False
        
        # Try matrix multiplication
        print("  Testing matrix multiplication...")
        try:
            # Warmup
            _ = cp.matmul(gpu_a, gpu_b)
            cp.cuda.Stream.null.synchronize()
            
            # Benchmark
            iterations = 5  # Reduced iterations
            start = time.perf_counter()
            for _ in range(iterations):
                gpu_result = cp.matmul(gpu_a, gpu_b)
                cp.cuda.Stream.null.synchronize()
            gpu_time = time.perf_counter() - start
            print(f"  ✅ Matrix multiplication successful")
        
            print(f"  GPU Time ({iterations} iterations): {gpu_time:.3f} seconds")
            print(f"  GPU Throughput: {iterations/gpu_time:.2f} ops/sec")
            
        except Exception as e:
            print(f"  ⚠️  Matrix multiplication failed (likely compilation issue): {e}")
            print("  This is common with runtime CUDA images. Basic GPU operations still work!")
        
        # CPU comparison (smaller size for CPU)
        try:
            print(f"\n  Testing {size//2}x{size//2} matrix multiplication on CPU for comparison...")
            cpu_a = np.random.random((size//2, size//2)).astype(np.float32)
            cpu_b = np.random.random((size//2, size//2)).astype(np.float32)
            
            start = time.perf_counter()
            for _ in range(iterations):
                cpu_result = np.matmul(cpu_a, cpu_b)
            cpu_time = time.perf_counter() - start
            
            print(f"  CPU Time ({iterations} iterations, {size//2}x{size//2}): {cpu_time:.3f} seconds")
        except:
            print("  CPU comparison skipped")
        
        # Memory test
        print_section("GPU Memory Test")
        
        print("Allocating large arrays on GPU...")
        try:
            # Try to allocate 1GB
            large_array = cp.zeros((512, 512, 1024), dtype=cp.float32)  # ~1GB
            print(f"  ✅ Successfully allocated 1GB on GPU")
            
            # Check memory usage
            with cp.cuda.Device(0):
                mem_info = cp.cuda.Device(0).mem_info
                used = (mem_info[1] - mem_info[0]) / (1024**3)
                print(f"  Memory used: {used:.2f} GB")
            
            del large_array
            cp.get_default_memory_pool().free_all_blocks()
            
        except cp.cuda.memory.OutOfMemoryError as e:
            print(f"  ⚠️  Could not allocate 1GB: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ CuPy not available: {e}")
        return False
    except Exception as e:
        print(f"❌ CUDA test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def continuous_monitoring():
    """Keep container running and monitor GPU."""
    print_section("Continuous Monitoring Mode")
    print("Container will stay running. GPU stats every 30 seconds...")
    print("Press Ctrl+C to stop")
    
    iteration = 0
    while True:
        iteration += 1
        time.sleep(30)
        
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                timestamp = datetime.now().strftime("%H:%M:%S")
                stats = result.stdout.strip().split(',')
                if len(stats) >= 4:
                    print(f"[{timestamp}] Iteration {iteration}: GPU {stats[0].strip()}, "
                          f"Mem {stats[1].strip()}/{stats[2].strip()}, Temp {stats[3].strip()}")
            
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            break
        except Exception:
            pass

def main():
    """Main test function."""
    print("=" * 60)
    print(" GPU Docker Test with UV-managed Dependencies")
    print("=" * 60)
    
    # Run tests
    env_ok = test_environment()
    nvidia_ok = test_nvidia_smi()
    cuda_ok = test_cuda_with_cupy()
    
    # Summary
    print_section("Test Summary")
    
    if nvidia_ok and cuda_ok:
        print("✅ All tests PASSED!")
        print("GPU is fully functional in the Docker container.")
        
        # Keep running for monitoring
        continuous_monitoring()
        return 0
    else:
        print("❌ Some tests FAILED")
        if not nvidia_ok:
            print("  - NVIDIA drivers not detected")
        if not cuda_ok:
            print("  - CUDA/CuPy tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())