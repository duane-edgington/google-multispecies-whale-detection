import json
import csv
import os
import sys
from pathlib import Path

def json_directory_to_csv(input_directory):
    """
    Convert all JSON files in a directory to a single CSV file.
    
    Args:
        input_directory (str): Path to the directory containing JSON files
    
    Returns:
        str: Path to the created CSV file
    """
    # Convert to Path object for easier handling
    dir_path = Path(input_directory)
    
    # Check if directory exists
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory '{input_directory}' does not exist or is not a directory")
    
    # Find all JSON files in the directory
    json_files = list(dir_path.glob("*.json"))
    
    if not json_files:
        raise ValueError(f"No JSON files found in directory '{input_directory}'")
    
    # Sort files by chunk number to maintain order
    json_files.sort(key=lambda x: extract_chunk_number(x.name))
    
    # Output CSV file path (same name as input directory)
    output_csv = dir_path.parent / f"{dir_path.name}.csv"
    
    # Extract all unique keys from all JSON files for CSV headers
    all_keys = set()
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                all_keys.update(data.keys())
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read {json_file}: {e}")
    
    # Convert set to sorted list for consistent column order
    fieldnames = ['chunk_number'] + sorted(all_keys)
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                    # Extract chunk number from filename
                    chunk_number = extract_chunk_number(json_file.name)
                    
                    # Create row with chunk number as first column
                    row_data = {'chunk_number': chunk_number}
                    row_data.update(data)
                    
                    writer.writerow(row_data)
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not process {json_file}: {e}")
                continue
    
    print(f"Successfully converted {len(json_files)} JSON files to {output_csv}")
    return str(output_csv)

def extract_chunk_number(filename):
    """
    Extract the chunk number from filename like:
    MARS_20180413_065913_resampled_24kHz_chunk_004_output.json
    
    Returns the chunk number as integer
    """
    # Split by underscores and find the part after 'chunk'
    parts = filename.split('_')
    
    for i, part in enumerate(parts):
        if part == 'chunk' and i + 1 < len(parts):
            # Get the next part and remove any non-digit characters
            chunk_str = parts[i + 1]
            # Extract only digits
            digits = ''.join(filter(str.isdigit, chunk_str))
            if digits:
                return int(digits)
    
    # If chunk pattern not found, try to extract any number from filename
    # This is a fallback for different naming patterns
    import re
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[-1])  # Use the last number found
    
    # If no number found, return 0 (shouldn't happen with proper filenames)
    return 0

def main():
    """
    Main function to handle command line arguments
    """
    if len(sys.argv) != 2:
        print("Usage: python json_to_csv.py <directory_path>")
        print("Example: python json_to_csv.py MARS_20180413_065913_resampled_24kHz")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    
    try:
        output_file = json_directory_to_csv(input_directory)
        print(f"Conversion completed successfully. Output file: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
