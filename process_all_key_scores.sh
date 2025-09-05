#!/bin/bash

# Script to recursively process all google multispecies-whale model directories
# each directory contains json files with key values
# Usage: ./process_all_key_scores.sh [input_directory] [key]

# Set default input directory
DEFAULT_IN_DIR="/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores"
IN_DIR="${1:-$DEFAULT_IN_DIR}"

# Check if key parameter is provided
if [ -z "$2" ]; then
    echo "Error: Key parameter is required"
    echo "Usage: $0 [input_directory] [key]"
    echo "Example: $0 /path/to/scores Oo"
    exit 1
fi

KEY="$2"

# Check if the input directory exists
if [ ! -d "$IN_DIR" ]; then
    echo "Error: Directory not found: $IN_DIR"
    exit 1
fi

echo "Recursively processing directories in: $IN_DIR"
echo "Using key: $KEY"

# Counter for processed directories
COUNT=0

# Find all directories that match the MARS_YYYYMMDD pattern and process them
find "$IN_DIR" -type d -name "MARS_*" | while read -r DIR; do
    # Check if the directory contains JSON files
    JSON_COUNT=$(find "$DIR" -name "*_output.json" -type f | wc -l)
    
    if [ "$JSON_COUNT" -gt 0 ]; then
        echo "Processing directory: $DIR (contains $JSON_COUNT JSON files)"
        
        # Run the Python script with the directory and key as input
        python3 extract_epoch_key_scores.py "$DIR" --key="$KEY" &
        
        COUNT=$((COUNT + 1))
        
        # Optional: Limit number of concurrent processes
        # if [ $(jobs -r | wc -l) -ge 4 ]; then
        #     wait -n
        # fi
    fi
done

echo "Started processing $COUNT directories in the background."
echo "Use 'wait' to wait for all background processes to complete."
