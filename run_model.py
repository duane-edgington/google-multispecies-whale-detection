import os
import argparse
import glob
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from pathlib import Path
import sys

import time
from datetime import timedelta

def process_wav_file(model, wav_file_path, output_text_path):
    """
    Process a single WAV file using the loaded TensorFlow model
    
    Args:
        model: Loaded TensorFlow model
        wav_file_path: Path to the input WAV file
        output_text_path: Path where the output text file should be saved
    """
    try:
        # Your existing TensorFlow procedure here
        # This should include loading the WAV file and running inference
        
        # Example structure (replace with your actual implementation):
        # 1. Load and preprocess the WAV file
        # 2. Run the model inference
        # 3. Process the model output
        # 4. Save results to output_text_path
        
        print(f"Processing: {wav_file_path}")
        print(f"Output will be saved to: {output_text_path}")
        
        # Placeholder for your actual processing code
        # result = your_tensorflow_procedure(wav_file_path, output_text_path)
        
        waveform, sample_rate = tf.audio.decode_wav(tf.io.read_file(wav_file_path),desired_channels=1,desired_samples=-1)
        # tf.audio.decode_wav decodes a 16bit PCM WAV file to a float tensor
        # The -32768 to 32767 signed 16-bit values will be scaled to -1.0 to 1.0 in float.
        # desired_channels=1 means decode one channel
        # desired_samples=-1 means decode all samples
        
        batch = tf.expand_dims(waveform, 0)
        #here, tf.expand_dims inserts a dimension of length 1 index 0 of waveform's shape.
        #This is useful to add an outer "batch" dimension to a single element

        spectrogram = model.front_end(batch)
        # This line calls a function or method named front_end on your model object.
        # This function is designed to extract features from the audio data in batch.
        # The output of this function is expected to be a spectrogram.

        print(spectrogram.shape)

        context_windows = tf.signal.frame(
            tf.squeeze(spectrogram, 0),
            frame_length=128,
            frame_step=64,
            axis=-2,
        )

        logits = model.logits(context_windows)
        features = model.features(context_windows)
        probabilities = tf.nn.sigmoid(logits)

        raw_predictions = logits.numpy()
        print(raw_predictions)
        print(raw_predictions.shape)

        save_probabilities = probabilities.numpy()
        print(save_probabilities)

        metadata = model.metadata()
        byte_class_names = metadata['class_names'].numpy()

        # first print out the logits in order
        # Find the top 10 classes in the probabilities
        top_logits_classes = tf.argsort(save_probabilities, axis=-1, direction='DESCENDING')[0, :10]
        p1 = tf.nn.sigmoid(logits)[0, top_logits_classes[0]].numpy()
        p2 = tf.nn.sigmoid(logits)[0, top_logits_classes[1]].numpy()
        p3 = tf.nn.sigmoid(logits)[0, top_logits_classes[2]].numpy()
        p4 = tf.nn.sigmoid(logits)[0, top_logits_classes[3]].numpy()
        p5 = tf.nn.sigmoid(logits)[0, top_logits_classes[4]].numpy()
        p6 = tf.nn.sigmoid(logits)[0, top_logits_classes[5]].numpy()
        p7 = tf.nn.sigmoid(logits)[0, top_logits_classes[6]].numpy()
        p8 = tf.nn.sigmoid(logits)[0, top_logits_classes[7]].numpy()
        p9 = tf.nn.sigmoid(logits)[0, top_logits_classes[8]].numpy()
        p10 = tf.nn.sigmoid(logits)[0, top_logits_classes[9]].numpy()

        save_probabilities = [float(p1), float(p2), float(p3), float(p4), float(p5), float(p6), float(p7),float(p8),float(p9),float(p10)]

        class_names = [name.decode('utf-8') for name in byte_class_names[top_logits_classes]]
 
        with open(output_text_path, 'w') as f:
    
            f.write(f'{wav_file_path}, {class_names},"{save_probabilities}\n')
            print(f"Top 10 classes: {class_names}, sigmoid probabilities: {save_probabilities}\n")

        return True
        
    except Exception as e:
        print(f"Error processing {wav_file_path}: {str(e)}")
        return False

def process_directory(model, input_dir, output_base_dir):
    """
    Process all WAV files in a directory and save results to output directory
    
    Args:
        model: Loaded TensorFlow model
        input_dir: Directory containing WAV files to process
        output_base_dir: Base directory where output files will be saved
    """
    # Get the directory name to encode in output filename
    dir_name = os.path.basename(os.path.normpath(input_dir))
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(output_base_dir, dir_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all WAV files in the input directory
    wav_files = glob.glob(os.path.join(input_dir, "*.wav"))
    
    if not wav_files:
        print(f"No WAV files found in {input_dir}")
        return
    
    print(f"Found {len(wav_files)} WAV files in {input_dir}")
    
    processed_count = 0
    for wav_file in wav_files:
        # Create output filename that encodes the directory name
        base_name = os.path.basename(wav_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_filename = f"{dir_name}_{name_without_ext}_output.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        # Process the WAV file
        success = process_wav_file(model, wav_file, output_path)
        if success:
            processed_count += 1
    
    print(f"Successfully processed {processed_count}/{len(wav_files)} files from {input_dir}")

def iterate_directories(model, root_input_dir, output_base_dir):
    """
    Iterate through directory structure and process each directory
    
    Args:
        model: Loaded TensorFlow model
        root_input_dir: Root directory containing subdirectories with WAV files
        output_base_dir: Base directory where output files will be saved
    """
    # Create output base directory if it doesn't exist
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Get all subdirectories in the root directory
    subdirectories = []
    for root, dirs, files in os.walk(root_input_dir):
        # Only process directories that contain WAV files
        wav_files = [f for f in files if f.lower().endswith('.wav')]
        if wav_files:
            subdirectories.append(root)
    
    if not subdirectories:
        print(f"No directories with WAV files found in {root_input_dir}")
        return
    
    print(f"Found {len(subdirectories)} directories with WAV files")
    
    for directory in subdirectories:
        print(f"\nProcessing directory: {directory}")
        process_directory(model, directory, output_base_dir)

def load_model_from_hub(model_url):
    """
    Load TensorFlow model from TensorFlow Hub
    
    Args:
        model_url: URL or path to the TensorFlow Hub model
        
    Returns:
        Loaded TensorFlow model
    """
    try:
        import tensorflow_hub as hub
        print(f"Loading model from: {model_url}")
        model = hub.load(model_url)
        print("Model loaded successfully")
        return model
    except ImportError:
        print("tensorflow_hub is required. Install with: pip install tensorflow_hub")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Process WAV files using TensorFlow model')
    parser.add_argument('--input_dir', required=True, 
                       help='Root directory containing subdirectories with WAV files')
    parser.add_argument('--output_dir', required=True,
                       help='Base directory where output text files will be saved')
    parser.add_argument('--model_url', required=True,
                       help='TensorFlow Hub model URL or path')
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.exists(args.input_dir):
        print(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    # Load the TensorFlow model
    model = load_model_from_hub(args.model_url)
    
    # Process all directories
    iterate_directories(model, args.input_dir, args.output_dir)
    
    print("\nProcessing completed!")

if __name__ == "__main__":
    main()
