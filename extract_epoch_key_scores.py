import json
import csv
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone

def extract_datetime_from_filename(filename):
    """
    Extract datetime from filename in format: MARS_YYYYMMDD_HHMMSS_*
    Example: MARS_20180413_065913_resampled_24kHz_chunk_004_output.json
    Returns: datetime object
    """
    # Pattern for MARS_YYYYMMDD_HHMMSS format
    pattern = r'MARS_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})'
    match = re.search(pattern, filename)
    
    if not match:
        raise ValueError(f"Could not extract datetime from filename: {filename}")
    
    year, month, day, hour, minute, second = map(int, match.groups())
    
    try:
        dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
        return dt
    except ValueError as e:
        raise ValueError(f"Invalid datetime in filename {filename}: {e}")

def extract_chunk_number(filename):
    """
    Extract the chunk number from filename.
    Example: MARS_20180413_065913_resampled_24kHz_chunk_004_output.json
    """
    chunk_match = re.search(r'chunk_(\d+)', filename)
    if chunk_match:
        return int(chunk_match.group(1))
    
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[-1])
    
    return 0

def calculate_epoch_seconds(base_datetime, chunk_number):
    """
    Calculate epoch seconds (Unix timestamp) from base datetime and chunk number.
    Each chunk represents 5 seconds, so offset = (chunk_number - 1) * 5
    """
    time_offset = (chunk_number - 1) * 5  # 5 seconds per chunk
    epoch_seconds = int(base_datetime.timestamp()) + time_offset
    return epoch_seconds

def extract_key_class_score(json_data, key_name):
    """
    Extract the class score for the specified key from the JSON data by finding the index of key_name
    in the "class_names" list and getting the corresponding score from the "score" list.
    """
    # Look for class_names and score lists
    if not isinstance(json_data, dict):
        return 0.0
    
    # Check if we have both class_names and score lists
    if 'class_names' in json_data and 'scores' in json_data:
        class_names = json_data['class_names']
        scores = json_data['scores']
        
        if (isinstance(class_names, list) and isinstance(scores, list) and 
            len(class_names) == len(scores)):
            
            # Find the index of key_name in class_names
            try:
                key_index = class_names.index(key_name)
                return float(scores[key_index])
            except ValueError:
                # key_name not found in class_names
                pass
            except IndexError:
                # Index out of range for scores list
                pass
    
    # Alternative patterns if the above doesn't work
    # Look for nested structures with class_names and scores
    for key, value in json_data.items():
        if isinstance(value, dict):
            if 'class_names' in value and 'scores' in value:
                class_names = value['class_names']
                scores = value['scores']
                
                if (isinstance(class_names, list) and isinstance(scores, list) and 
                    len(class_names) == len(scores)):
                    
                    try:
                        key_index = class_names.index(key_name)
                        return float(scores[key_index])
                    except (ValueError, IndexError):
                        continue
    
    # Look for classification arrays
    if 'classifications' in json_data and isinstance(json_data['classifications'], list):
        for classification in json_data['classifications']:
            if (isinstance(classification, dict) and 
                'class_names' in classification and 'scores' in classification):
                
                class_names = classification['class_names']
                scores = classification['scores']
                
                if (isinstance(class_names, list) and isinstance(scores, list) and 
                    len(class_names) == len(scores)):
                    
                    try:
                        key_index = class_names.index(key_name)
                        return float(scores[key_index])
                    except (ValueError, IndexError):
                        continue
    
    # If no key score found, return 0.0
    return 0.0

def process_json_directory(input_directory, key_name, output_file=None):
    """
    Process JSON files and create CSV with epoch seconds and key class score.
    """
    dir_path = Path(input_directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory '{input_directory}' does not exist")
    
    json_files = list(dir_path.glob("*.json"))
    
    if not json_files:
        raise ValueError(f"No JSON files found in directory '{input_directory}'")
    
    # Sort files by chunk number
    json_files.sort(key=lambda x: extract_chunk_number(x.name))
    
    # Automatically derive output filename if not provided
    if output_file is None:
        base_name = dir_path.name
        output_file = dir_path.parent / f"{base_name}_epoch_{key_name.lower()}_scores.csv"
    else:
        output_file = Path(output_file)
    
    # Extract base datetime from first valid filename
    base_datetime = None
    for json_file in json_files:
        try:
            base_datetime = extract_datetime_from_filename(json_file.name)
            break
        except ValueError:
            continue
    
    if base_datetime is None:
        raise ValueError("Could not extract valid datetime from any filename")
    
    # Process all files
    results = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                chunk_number = extract_chunk_number(json_file.name)
                epoch_seconds = calculate_epoch_seconds(base_datetime, chunk_number)
                key_score = extract_key_class_score(data, key_name)
                
                results.append({
                    'epoch_seconds': epoch_seconds,
                    f'{key_name}_class_score': key_score,
                    'filename': json_file.name,
                    'chunk_number': chunk_number
                })
                
        except (json.JSONDecodeError, IOError, UnicodeDecodeError, ValueError) as e:
            print(f"Warning: Could not process {json_file.name}: {e}")
            continue
    
    if not results:
        raise ValueError("No valid JSON files could be processed")
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['epoch_seconds', f'{key_name}_class_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'epoch_seconds': result['epoch_seconds'],
                f'{key_name}_class_score': result[f'{key_name}_class_score']
            })
    
    # Print summary
    print(f"Successfully processed {len(results)} JSON files")
    print(f"Input directory: {input_directory}")
    print(f"Output file: {output_file}")
    print(f"Key name: {key_name}")
    print(f"Base datetime: {base_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Time range: {results[0]['epoch_seconds']} to {results[-1]['epoch_seconds']} epoch seconds")
    print(f"{key_name} score range: {min(r[f'{key_name}_class_score'] for r in results):.6f} to {max(r[f'{key_name}_class_score'] for r in results):.6f}")
    
    # Count files with non-zero key scores
    non_zero_count = sum(1 for r in results if r[f'{key_name}_class_score'] > 0)
    print(f"Files with {key_name} scores > 0: {non_zero_count}/{len(results)}")
    
    return str(output_file)

def main():
    """
    Main function with argparse argument handling.
    """
    parser = argparse.ArgumentParser(
        description='Extract epoch seconds and class scores for a specified key from JSON files. The score is extracted from the score list at the position where class_names contains the key name.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s MARS_20180413_065913_resampled_24kHz --key Mn
  %(prog)s /path/to/data --key Oo --output oo_scores.csv
  %(prog)s /path/to/json_files --key Bp -o results/epoch_bp_scores.csv
        """
    )
    
    parser.add_argument(
        'input_directory',
        help='Directory containing JSON files to process'
    )
    
    parser.add_argument(
        '-k', '--key',
        dest='key_name',
        required=True,
        help='Key name to extract scores for (e.g., Mn, Oo, Bp, Bm, Upcall, etc.)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output CSV filename (optional). If not provided, will be automatically derived from input directory name and key name.'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output with additional information'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode to print JSON structure of first file'
    )
    
    args = parser.parse_args()
    
    try:
        if args.debug:
            # Debug: print structure of first JSON file
            dir_path = Path(args.input_directory)
            json_files = list(dir_path.glob("*.json"))
            if json_files:
                json_files.sort(key=lambda x: extract_chunk_number(x.name))
                first_file = json_files[0]
                print(f"Debug: Structure of first file {first_file.name}:")
                with open(first_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=2))
                print("\n" + "="*50 + "\n")
        
        output_file = process_json_directory(args.input_directory, args.key_name, args.output_file)
        
        if args.verbose:
            print("\nDetailed information:")
            print(f"Input directory: {args.input_directory}")
            print(f"Key name: {args.key_name}")
            print(f"Output file: {output_file}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
