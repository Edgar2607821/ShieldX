#!/bin/bash

# ==============================================================================
# A simple script to run a Uvicorn server with configurable parameters.
#
# Usage:
#   ./run_server.sh
#
# You can also override the default variables from the command line:
#   APP_MODULE="my_app:app" PORT=8080 ./run_server.sh
# ==============================================================================

# --- Configuration ---
# The import string for your FastAPI application.
# Format: <python_file_name>:<fastapi_instance_name>
APP_MODULE=${APP_MODULE:-"shieldx.server:app"}

# The host IP address to bind to.
# Use 0.0.0.0 to make the server accessible from other devices on the network.
HOST=${HOST:-"0.0.0.0"}

# The port to run the server on.
PORT=${PORT:-20000}

# The number of worker processes.
# For development, 1 is usually sufficient.
WORKERS=${WORKERS:-1}

# Enable or disable auto-reloading for development.
# Set to "--reload" to enable, or an empty string "" to disable.
RELOAD_FLAG=${RELOAD_FLAG:-"--reload"}

# --- Script Logic ---

# Announce the settings being used.
echo "Starting Uvicorn server for: $APP_MODULE"
echo "  > Host: $HOST"
echo "  > Port: $PORT"
echo "  > Workers: $WORKERS"
echo "  > Reloading: ${RELOAD_FLAG:+enabled}" # Prints 'enabled' if RELOAD_FLAG is not empty
echo "----------------------------------------------------"

# Execute the Uvicorn command with the specified parameters.
# The ${RELOAD_FLAG} will expand to either "--reload" or nothing.
uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --workers "$WORKERS" ${RELOAD_FLAG}