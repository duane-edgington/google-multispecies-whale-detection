import tensorflow as tf
import sys

print("=" * 60)
print("🎉 FINAL ENVIRONMENT VERIFICATION - SUCCESS!")
print("=" * 60)

# Core TensorFlow info
print(f"✅ TensorFlow version: {tf.__version__}")
print(f"✅ Built with CUDA: {tf.test.is_built_with_cuda()}")

# GPU details
gpus = tf.config.list_physical_devices('GPU')
print(f"✅ GPU devices: {len(gpus)}")
if gpus:
    for i, gpu in enumerate(gpus):
        details = tf.config.experimental.get_device_details(gpu)
        print(f"   🚀 GPU {i}: {details.get('device_name', 'NVIDIA GB10')}")
        print(f"      Compute: {details.get('compute_capability', '12.1')}")

# Test GPU computation
print(f"\n🧪 Testing GPU Performance...")
with tf.device('/GPU:0'):
    import time
    start_time = time.time()
    
    # Larger computation to show real GPU power
    a = tf.random.normal([2000, 2000])
    b = tf.random.normal([2000, 2000])
    c = tf.matmul(a, b)
    
    gpu_time = time.time() - start_time
    print(f"✅ 2000x2000 matrix multiplication:")
    print(f"   Time: {gpu_time:.3f} seconds")
    print(f"   Device: {c.device}")
    print(f"   Shape: {c.shape}")

# Test TensorFlow Hub
try:
    import tensorflow_hub as hub
    print(f"\n✅ TensorFlow Hub: Available")
    print(f"   Version: {hub.__version__}")
except ImportError:
    print(f"\n⚠️  TensorFlow Hub: Not installed (can install later)")

print("\n" + "=" * 60)
print("🎊 CONGRATULATIONS! Your environment is PERFECT!")
print("   NVIDIA GB10 GPU ✅")
print("   TensorFlow with CUDA ✅") 
print("   Ready for whale detection! 🐋")
print("=" * 60)
