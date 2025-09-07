#!/bin/bash
set -e

# --- Configuration ---
# Path to rshell executable
RSHELL_EXEC="/Users/devbook/Documents/pet-project/drone/esptoolenv/bin/rshell"
# Serial port of your device
PORT="/dev/tty.usbmodem2101"
# rshell options, using --buffer-size as it's the standard long option
RSHELL_OPTS="-p $PORT --buffer-size 32"
# Local and remote directories
LOCAL_SRC_DIR="src"
REMOTE_PYBOARD_DIR="/pyboard"

# --- rshell wrapper function ---
run_rshell() {
    echo "Executing: rshell $@"
    # Quoting arguments to handle spaces or special characters
    $RSHELL_EXEC $RSHELL_OPTS "$@"
}

# --- Main script ---
echo "Starting upload process..."

# Create remote directories. The '|| true' part ensures that the script doesn't fail if the directory already exists.
run_rshell "mkdir $REMOTE_PYBOARD_DIR/utils" || true

# Copy all files from the root of the local source directory
echo "Copying files from $LOCAL_SRC_DIR to $REMOTE_PYBOARD_DIR..."
for file in "$LOCAL_SRC_DIR"/*; do
    # Check if it is a file before trying to copy
    if [ -f "$file" ]; then
        run_rshell "cp '$file' '$REMOTE_PYBOARD_DIR/'"
    fi
done

# Copy all files from the local utils directory if it exists
if [ -d "$LOCAL_SRC_DIR/utils" ]; then
    echo "Copying files from $LOCAL_SRC_DIR/utils to $REMOTE_PYBOARD_DIR/utils..."
    for file in "$LOCAL_SRC_DIR"/utils/*; do
        if [ -f "$file" ]; then
            run_rshell "cp '$file' '$REMOTE_PYBOARD_DIR/utils/'"
        fi
    done
else
    echo "Local directory $LOCAL_SRC_DIR/utils not found, skipping."
fi

echo "Upload finished successfully."