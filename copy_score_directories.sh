#!/bin/bash

# Source directory
SOURCE_DIR="/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores"

# Target directory
TARGET_DIR="/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2018/04/"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR does not exist!"
    exit 1
fi

# Copy all directories (and their contents) from source to target
for dir in "$SOURCE_DIR"/*/; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        echo "Copying directory: $dir_name"
        cp -r "$dir" "$TARGET_DIR"
    fi
done

echo "Directory copy operation completed!"
