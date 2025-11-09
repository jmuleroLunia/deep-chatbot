#!/bin/bash

# Script para arrancar solo el frontend con reload

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR/frontend"
echo "Starting frontend on http://localhost:5173"
npm run dev
