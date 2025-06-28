#!/bin/bash

# Script to recursively copy files (not folders) from source to destination
# Usage: ./copy_files.sh

SOURCE_DIR="dafnck-machine-3.3/01_Machine"
DEST_DIR="/home/daihungpham/agentic-project/rules"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Function to copy files recursively to flat destination
copy_files() {
    local src="$1"
    local dst="$2"
    
    # Create destination directory
    mkdir -p "$dst"
    
    # Find all files (not directories) and copy them to flat destination
    find "$src" -type f -print0 | while IFS= read -r -d '' file; do
        # Get just the filename
        filename="$(basename "$file")"
        
        # Copy the file to destination root (no subdirectories)
        cp "$file" "$dst/$filename"
        echo "Copied: $filename"
    done
}

echo "Starting file copy from '$SOURCE_DIR' to '$DEST_DIR'..."
copy_files "$SOURCE_DIR" "$DEST_DIR"
echo "File copy completed!"