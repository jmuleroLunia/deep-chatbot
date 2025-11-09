#!/bin/bash

# Script para arrancar solo el backend con reload

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR/backend"
echo "Starting backend on http://127.0.0.1:8000"
echo "API Docs: http://127.0.0.1:8000/docs"
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload
