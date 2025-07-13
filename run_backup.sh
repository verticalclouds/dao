#!/bin/bash

set -e

DOWNLOADS_DIR="./data"

# Find the next available backup_NNN directory
i=1
while true; do
    BACKUP_DIR="$DOWNLOADS_DIR/backup_$(printf "%03d" $i)"
    if [ ! -d "$BACKUP_DIR" ]; then
        break
    fi
    ((i++))
done

mkdir -p "$BACKUP_DIR"

# Move everything except backup_* into the new backup directory
shopt -s dotglob  # Include hidden files
for item in "$DOWNLOADS_DIR"/*; do
    basename=$(basename "$item")
    if [[ "$basename" != backup_* ]]; then
        mv "$item" "$BACKUP_DIR/"
    fi
done

echo "✅ Moved files to $BACKUP_DIR"
