#!/bin/bash
set -e

# --- Configuration ---
RSHELL_EXEC="/Users/devbook/Documents/pet-project/drone/esptoolenv/bin/rshell"
PORT="/dev/tty.usbmodem2101"
RSHELL_OPTS="-p $PORT --buffer-size 32"
LOCAL_SRC_DIR="src"
REMOTE_PYBOARD_DIR="/pyboard"

# --- rshell wrapper function ---
run_rshell() {
    echo "Executing: rshell $@"
    $RSHELL_EXEC $RSHELL_OPTS "$@"
}

# --- Main script ---
echo "Starting robust upload process..."

# 1. Remove old files to ensure a clean slate.
# The '|| true' prevents failure if the file doesn't exist.
echo "Step 1: Removing old files from $REMOTE_PYBOARD_DIR..."
run_rshell "rm $REMOTE_PYBOARD_DIR/main.py" || true
run_rshell "rm $REMOTE_PYBOARD_DIR/server.py" || true
run_rshell "rm $REMOTE_PYBOARD_DIR/fc.py" || true
run_rshell "rm $REMOTE_PYBOARD_DIR/index.html" || true
echo "Old files removed."

# 2. Copy all files from the local source directory
echo "Step 2: Copying new files from $LOCAL_SRC_DIR to $REMOTE_PYBOARD_DIR..."
for file in "$LOCAL_SRC_DIR"/*; do
    if [ -f "$file" ]; then
        run_rshell "cp '$file' '$REMOTE_PYBOARD_DIR/'"
    fi
done
echo "New files copied."

# 3. Verify that the main file exists on the board
echo "Step 3: Verifying main.py on pyboard..."
run_rshell "ls $REMOTE_PYBOARD_DIR"

echo "Upload finished successfully. Please reset the device."