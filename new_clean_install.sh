#!/bin/bash
echo "=== COMPLETE CLEAN INSTALL ==="

# Remove old environment
cd ~/google-multispecies-whale-detection/new3-12_whale_detection/google-multispecies-whale-detection
rm -rf venv

# Create fresh environment
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Step 1: Install ONLY NVIDIA TensorFlow via direct wheel
echo "Step 1: Installing NVIDIA TensorFlow..."
pip install --extra-index-url https://pypi.ngc.nvidia.com nvidia-tensorflow  \
    tensorflow-hub \
    protobuf -c constraints.txt


# Step 2: Test TensorFlow installation
echo "Step 2: Testing TensorFlow..."
python -c "\
try:
    import tensorflow as tf
    print('✅ TensorFlow imported successfully')
    print('✅ Version:', tf.__version__)
    gpus = tf.config.list_physical_devices('GPU')
    print('✅ GPU devices:', len(gpus))
    if gpus:
        print('🎉 SUCCESS: GPU is working!')
    else:
        print('❌ No GPU detected')
except Exception as e:
    print('❌ Error:', e)
    exit(1)
"

# Step 3: Install compatible packages WITHOUT breaking GPU
echo "Step 3: Installing compatible packages..."

# OPTION 1: Let NVIDIA TensorFlow handle Keras internally (RECOMMENDED)
echo "Using built-in Keras from NVIDIA TensorFlow..."
python -c "
import tensorflow as tf
print('Keras available via tf.keras')
"

# OPTION 2: If you specifically need tf-keras, install from NVIDIA's index
echo "INSTALL NVIDIA-KERAS"
#pip install --extra-index-url https://pypi.ngc.nvidia.com nvidia-keras

# Install other packages carefully
#pip install protobuf==4.25.3
#pip install tensorflow-hub==0.16.1

# Test after each installation to catch what breaks GPU
echo "Testing after protobuf and tf-hub..."
python -c "
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print(f'GPU devices after protobuf/tf-hub: {len(gpus)}')
"

# Step 4: Install additional packages if needed
echo "Step 4: Installing additional packages..."
pip install natsort matplotlib pandas

# Final verification
echo "=== FINAL VERIFICATION ==="
python -c "\
import tensorflow as tf
import tensorflow_hub as hub
print('✅ TensorFlow version:', tf.__version__)
print('✅ TensorFlow Hub version:', hub.__version__)
gpus = tf.config.list_physical_devices('GPU')
print('✅ GPU devices:', len(gpus))
if gpus:
    print('🎉 GPU STILL WORKING! Environment ready!')
else:
    print('❌ GPU BROKEN - check what package broke it')
"

echo "=== INSTALLATION COMPLETE ==="
