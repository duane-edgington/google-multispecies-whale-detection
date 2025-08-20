import os
import argparse
from pathlib import Path
import logging
import numpy as np
import soundfile as sf
from typing import List, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def chunk_audio_file(input_file: Path, output_dir: Path, chunk_duration: float = 5.0) -> int:
    """
    Chunk a single audio file into smaller segments.
    
    Args:
        input_file: Path to input audio file
        output_dir: Directory to save output chunks
        chunk_duration: Duration of each chunk in seconds
    
    Returns:
        Number of chunks created
    """
    try:
        # Load audio file
        audio_data, sample_rate = sf.read(input_file)
        
        # Calculate chunk size in samples
        chunk_size = int(chunk_duration * sample_rate)
        total_samples = len(audio_data)
        
        # Calculate expected number of chunks for 600-second file
        expected_chunks = 120
        actual_chunks = total_samples // chunk_size
        
        if actual_chunks != expected_chunks:
            logger.warning(f"File {input_file.name}: Expected {expected_chunks} chunks, got {actual_chunks} chunks")
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate chunks
        chunks_created = 0
        for i in range(actual_chunks):
            start_sample = i * chunk_size
            end_sample = start_sample + chunk_size
            
            # Extract chunk
            chunk = audio_data[start_sample:end_sample]
            
            # Create output filename
            output_filename = output_dir / f"{input_file.stem}_chunk_{i+1:03d}.wav"
            
            # Save chunk
            sf.write(output_filename, chunk, sample_rate)
            chunks_created += 1
        
        logger.info(f"Created {chunks_created} chunks from {input_file.name}")
        return chunks_created
        
    except Exception as e:
        logger.error(f"Error processing {input_file}: {str(e)}")
        return 0

def process_directory_tree(
    input_root: str,
    output_root: str,
    chunk_duration: float = 5.0,
    file_pattern: str = "*.wav"
) -> dict:
    """
    Process all audio files in directory tree, chunking them into smaller segments.
    
    Args:
        input_root: Root directory of input audio files
        output_root: Root directory for output chunks
        chunk_duration: Duration of each chunk in seconds
        file_pattern: Pattern to match audio files
    
    Returns:
        Dictionary with processing statistics
    """
    input_path = Path(input_root)
    output_path = Path(output_root)
    
    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_path}")
    
    # Statistics
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'total_chunks': 0,
        'failed_files': 0
    }
    
    # Find all audio files
    audio_files = list(input_path.rglob(file_pattern))
    stats['total_files'] = len(audio_files)
    
    if not audio_files:
        logger.warning(f"No audio files found matching pattern '{file_pattern}' in {input_path}")
        return stats
    
    logger.info(f"Found {stats['total_files']} audio files to process")
    
    for input_file in audio_files:
        if not input_file.is_file():
            continue
            
        # Create corresponding output directory structure
        relative_path = input_file.relative_to(input_path).parent
        output_dir = output_path / relative_path / input_file.stem
        
        logger.info(f"Processing: {input_file}")
        
        # Process the file
        chunks_created = chunk_audio_file(input_file, output_dir, chunk_duration)
        
        if chunks_created > 0:
            stats['processed_files'] += 1
            stats['total_chunks'] += chunks_created
            logger.info(f"Successfully created {chunks_created} chunks for {input_file.name}")
        else:
            stats['failed_files'] += 1
            logger.error(f"Failed to process {input_file.name}")
    
    return stats

def specific_orca_chunking_processor(
    input_directory: str,
    chunk_duration: float = 5.0
) -> dict:
    """
    Specific processor for Orca audio files that chunks 600s files into 5s segments.
    
    Args:
        input_directory: Input directory path
        chunk_duration: Duration of each chunk in seconds
    
    Returns:
        Processing statistics
    """
    # Create output path by replacing directory name
    output_directory = input_directory.replace('resampled_24kHz', 'resampled_24kHz_chunks')
    
    logger.info(f"Input directory: {input_directory}")
    logger.info(f"Output directory: {output_directory}")
    logger.info(f"Chunk duration: {chunk_duration} seconds")
    logger.info("Starting audio chunking process...")
    
    # Process the directory tree
    stats = process_directory_tree(
        input_root=input_directory,
        output_root=output_directory,
        chunk_duration=chunk_duration,
        file_pattern="*.wav"
    )
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("PROCESSING SUMMARY:")
    logger.info(f"Total files found: {stats['total_files']}")
    logger.info(f"Successfully processed: {stats['processed_files']}")
    logger.info(f"Failed files: {stats['failed_files']}")
    logger.info(f"Total chunks created: {stats['total_chunks']}")
    
    if stats['processed_files'] > 0:
        avg_chunks = stats['total_chunks'] / stats['processed_files']
        logger.info(f"Average chunks per file: {avg_chunks:.1f}")
    
    logger.info("="*50)
    
    return stats

def verify_audio_duration(input_file: Path, expected_duration: float = 600.0) -> bool:
    """
    Verify that an audio file has the expected duration.
    
    Args:
        input_file: Path to audio file
        expected_duration: Expected duration in seconds
    
    Returns:
        True if duration matches expected, False otherwise
    """
    try:
        import soundfile as sf
        audio_data, sample_rate = sf.read(input_file)
        actual_duration = len(audio_data) / sample_rate
        
        if abs(actual_duration - expected_duration) > 1.0:  # 1 second tolerance
            logger.warning(f"File {input_file.name}: Expected {expected_duration}s, got {actual_duration:.1f}s")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying {input_file}: {str(e)}")
        return False

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Chunk 600-second audio files into 5-second segments')
    parser.add_argument('input_directory', help='Input directory containing audio files')
    parser.add_argument('--chunk-duration', type=float, default=5.0, 
                       help='Duration of each chunk in seconds (default: 5.0)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify input files are 600 seconds before processing')
    
    args = parser.parse_args()
    
    # Process the files
    specific_orca_chunking_processor(
        input_directory=args.input_directory,
        chunk_duration=args.chunk_duration
    )

# Example usage
if __name__ == "__main__":
    # Direct usage example
    input_dir = '/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz/2018/04/'
    
    # Process the directory
    stats = specific_orca_chunking_processor(input_dir, chunk_duration=5.0)
    
    # Alternatively, use command line:
    # python script.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz/2018/04/ --chunk-duration 5.0
