import json
import csv
import os
import sys
import re
import argparse
from pathlib import Path
from natsort import natsorted

def natural_sort_key(s):
    """
    Key function for natural sorting of strings containing numbers.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def flatten_json(data, parent_key='', sep='_'):
    """
    Flatten a nested dictionary and expand lists into separate columns.
    Uses natural sorting for list items to ensure proper ordering.
    """
    items = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(flatten_json(value, new_key, sep=sep))
            elif isinstance(value, list):
                # Expand list into separate columns with natural sorting
                sorted_items = natsorted(enumerate(value), key=lambda x: str(x[1]))
                for orig_idx, item in sorted_items:
                    list_key = f"{new_key}_{orig_idx + 1}"  # Keep original 1-based indexing
                    if isinstance(item, (dict, list)):
                        items.update(flatten_json(item, list_key, sep=sep))
                    else:
                        items[list_key] = item
            else:
                items[new_key] = value
    elif isinstance(data, list):
        # Handle top-level lists with natural sorting
        sorted_items = natsorted(enumerate(data), key=lambda x: str(x[1]))
        for orig_idx, item in sorted_items:
            list_key = f"{parent_key}_{orig_idx + 1}" if parent_key else f"item_{orig_idx + 1}"
            if isinstance(item, (dict, list)):
                items.update(flatten_json(item, list_key, sep=sep))
            else:
                items[list_key] = item
    else:
        items[parent_key] = data
    
    return items

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

def calculate_time_offset(chunk_number):
    """
    Calculate 5-second time offset by reducing chunk number by 1.
    """
    return max(0, chunk_number - 1)

def json_directory_to_csv(input_directory, output_file=None):
    """
    Convert all JSON files in a directory to a single CSV file.
    Uses natural sorting for list items and automatic output filename.
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
        # Use the directory name as base for output filename
        base_name = dir_path.name
        output_file = dir_path.parent / f"{base_name}_expanded.csv"
    else:
        output_file = Path(output_file)
    
    # First pass: collect all possible fieldnames with natural sorting
    all_fieldnames = set()
    flattened_data_list = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                flattened_data = flatten_json(data)
                
                chunk_number = extract_chunk_number(json_file.name)
                time_offset = calculate_time_offset(chunk_number)
                flattened_data['5_sec_time_offset'] = time_offset
                
                flattened_data_list.append(flattened_data)
                all_fieldnames.update(flattened_data.keys())
                
        except (json.JSONDecodeError, IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not process {json_file.name}: {e}")
            continue
    
    if not flattened_data_list:
        raise ValueError("No valid JSON files could be processed")
    
    # Remove special columns from fieldnames set
    all_fieldnames.discard('5_sec_time_offset')
    
    # Convert to list and sort naturally
    fieldnames_list = list(all_fieldnames)
    fieldnames_list.sort(key=natural_sort_key)
    
    # Put 5_sec_time_offset first
    fieldnames = ['5_sec_time_offset'] + fieldnames_list
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for flattened_data in flattened_data_list:
            row = {field: flattened_data.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"Successfully converted {len(flattened_data_list)} JSON files")
    print(f"Input directory: {input_directory}")
    print(f"Output file: {output_file}")
    print(f"Total columns: {len(fieldnames)}")
    print(f"Time offset range: {min([d['5_sec_time_offset'] for d in flattened_data_list])} to {max([d['5_sec_time_offset'] for d in flattened_data_list])} seconds")
    
    return str(output_file)

def main():
    """
    Main function with argparse argument handling.
    """
    parser = argparse.ArgumentParser(
        description='Convert JSON files from a directory to a single CSV file with expanded lists and natural sorting.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s MARS_20180413_065913_resampled_24kHz
  %(prog)s /path/to/data --output custom_output.csv
  %(prog)s /path/to/json_files -o results/processed_data.csv
        """
    )
    
    parser.add_argument(
        'input_directory',
        help='Directory containing JSON files to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output CSV filename (optional). If not provided, will be automatically derived from input directory name.'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Processing directory: {args.input_directory}")
            if args.output_file:
                print(f"Output file specified: {args.output_file}")
            else:
                print("Output file will be automatically generated")
        
        output_file = json_directory_to_csv(args.input_directory, args.output_file)
        
        if args.verbose:
            print("Conversion completed successfully!")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
