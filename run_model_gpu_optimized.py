# run_model_gpu_optimized.py

import os
import argparse
import glob
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from pathlib import Path
import sys
import json
import time
from datetime import timedelta

# Enable GPU memory growth to avoid allocating all memory at once
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"Enabled memory growth for {len(gpus)} GPU(s)")
    except RuntimeError as e:
        print(e)

def configure_gpu():
    """Configure GPU settings for optimal performance"""
    # Set mixed precision for better performance on RTX cards
    try:
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        print("Mixed precision enabled")
    except:
        print("Mixed precision not available, using default precision")

def process_wav_file_batch(model, wav_file_paths, output_dir):
    """
    Process multiple WAV files in batch for better GPU utilization
    
    Args:
        model: Loaded TensorFlow model
        wav_file_paths: List of paths to input WAV files
        output_dir: Directory where output json files should be saved
    """
    try:
        # Batch load and decode WAV files
        waveforms = []
        valid_files = []
        
        for wav_file_path in wav_file_paths:
            try:
                waveform, sample_rate = tf.audio.decode_wav(
                    tf.io.read_file(wav_file_path),
                    desired_channels=1,
                    desired_samples=-1
                )
                waveforms.append(waveform)
                valid_files.append(wav_file_path)
            except Exception as e:
                print(f"Error loading {wav_file_path}: {str(e)}")
                continue
        
        if not waveforms:
            return 0
        
        # Create batch tensor
        batch = tf.stack(waveforms, axis=0)
        
        # Process batch through model
        spectrograms = model.front_end(batch)
        
        results = []
        for i, spectrogram in enumerate(spectrograms):
            # Process each spectrogram individually
            context_windows = tf.signal.frame(
                spectrogram,
                frame_length=128,
                frame_step=64,
                axis=-2,
            )
            
            logits = model.logits(context_windows)
            probabilities = tf.nn.sigmoid(logits)
            
            # Process all 12 logits
            metadata = model.metadata()
            byte_class_names = metadata['class_names'].numpy()
            
            # Get probabilities for all 12 classes
            all_probabilities = probabilities.numpy()[0]  # First (and only) batch element
            all_logits = logits.numpy()[0]
            
            # Get top classes (all 12 in descending order)
            sorted_indices = tf.argsort(all_probabilities, axis=-1, direction='DESCENDING').numpy()
            top_classes = sorted_indices[:12]  # Get all 12 classes
            
            # Extract probabilities and class names
            top_probabilities = [float(all_probabilities[idx]) for idx in top_classes]
            class_names = [byte_class_names[idx].decode('utf-8') for idx in top_classes]
            top_logits = [float(all_logits[idx]) for idx in top_classes]

            # Create output data
            output_data = {
                "filename": valid_files[i],
                "scores": top_probabilities,
                "class_names": class_names,
                "logits": top_logits
            }
            
            results.append((valid_files[i], output_data))
        
        # Save results
        success_count = 0
        for wav_file_path, output_data in results:
            base_name = os.path.basename(wav_file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            dir_name = os.path.basename(os.path.dirname(wav_file_path))
            output_filename = f"{dir_name}_{name_without_ext}_output.json"
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                with open(output_path, 'w') as f:
                    json.dump(output_data, f, indent=4)
                success_count += 1
            except Exception as e:
                print(f"Error saving results for {wav_file_path}: {str(e)}")
        
        return success_count
        
    except Exception as e:
        print(f"Error processing batch: {str(e)}")
        return 0

def process_directory_optimized(model, input_dir, output_base_dir, batch_size=8):
    """
    Process all WAV files in a directory with batching for better performance
    
    Args:
        model: Loaded TensorFlow model
        input_dir: Directory containing WAV files to process
        output_base_dir: Base directory where output files will be saved
        batch_size: Number of files to process simultaneously
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
    
    # Process files in batches
    processed_count = 0
    total_files = len(wav_files)
    
    start_time = time.time()
    
    for batch_start in range(0, total_files, batch_size):
        batch_end = min(batch_start + batch_size, total_files)
        batch_files = wav_files[batch_start:batch_end]
        
        print(f"Processing batch {batch_start//batch_size + 1}/{(total_files + batch_size - 1)//batch_size}")
        
        success_count = process_wav_file_batch(model, batch_files, output_dir)
        processed_count += success_count
        
        # Estimate remaining time
        elapsed_time = time.time() - start_time
        files_per_second = processed_count / elapsed_time if elapsed_time > 0 else 0
        remaining_files = total_files - processed_count
        remaining_time = remaining_files / files_per_second if files_per_second > 0 else 0
        
        print(f"Processed: {processed_count}/{total_files} | "
              f"Elapsed: {timedelta(seconds=int(elapsed_time))} | "
              f"ETA: {timedelta(seconds=int(remaining_time))} | "
              f"Speed: {files_per_second:.2f} files/sec")
    
    print(f"Successfully processed {processed_count}/{len(wav_files)} files from {input_dir}")

def iterate_directories_optimized(model, root_input_dir, output_base_dir, batch_size=8):
    """
    Iterate through directory structure and process each directory with optimization
    
    Args:
        model: Loaded TensorFlow model
        root_input_dir: Root directory containing subdirectories with WAV files
        output_base_dir: Base directory where output files will be saved
        batch_size: Number of files to process simultaneously
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
    
    total_start_time = time.time()
    
    for i, directory in enumerate(subdirectories):
        print(f"\nProcessing directory {i+1}/{len(subdirectories)}: {directory}")
        dir_start_time = time.time()
        
        process_directory_optimized(model, directory, output_base_dir, batch_size)
        
        dir_time = time.time() - dir_start_time
        print(f"Directory processed in {timedelta(seconds=int(dir_time))}")
    
    total_time = time.time() - total_start_time
    print(f"\nTotal processing time: {timedelta(seconds=int(total_time))}")

def load_model_from_hub(model_url):
    """
    Load TensorFlow model from TensorFlow Hub with optimization
    
    Args:
        model_url: URL or path to the TensorFlow Hub model
        
    Returns:
        Loaded TensorFlow model
    """
    try:
        print(f"Loading model from: {model_url}")
        
        # Use tf.function for better performance
        @tf.function
        def model_call(inputs):
            return model(inputs)
        
        model = hub.load(model_url)
        print("Model loaded successfully")
        
        # Warm up the model
        print("Warming up model...")
        dummy_input = tf.random.normal([1, 16000, 1])
        _ = model.front_end(dummy_input)
        print("Model warm-up complete")
        
        return model
        
    except ImportError:
        print("tensorflow_hub is required. Install with: pip install tensorflow_hub")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Process WAV files using TensorFlow model with GPU optimization')
    parser.add_argument('--input_dir', required=True, 
                       help='Root directory containing subdirectories with WAV files')
    parser.add_argument('--output_dir', required=True,
                       help='Base directory where output json files will be saved')
    parser.add_argument('--model_url', required=True,
                       help='TensorFlow Hub model URL or path')
    parser.add_argument('--batch_size', type=int, default=8,
                       help='Batch size for processing (default: 8)')
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.exists(args.input_dir):
        print(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    # Configure GPU settings
    configure_gpu()
    
    # Load the TensorFlow model
    model = load_model_from_hub(args.model_url)
    
    # Process all directories with optimization
    iterate_directories_optimized(model, args.input_dir, args.output_dir, args.batch_size)
    
    print("\nProcessing completed!")

if __name__ == "__main__":
    main()
