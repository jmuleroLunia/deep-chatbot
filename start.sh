#!/bin/bash

# Script para arrancar el frontend y backend en paralelo con reload

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Deep Chatbot...${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${BLUE}Warning: Ollama doesn't seem to be running${NC}"
    echo -e "${BLUE}Please start Ollama with: ollama serve${NC}"
fi

# Start backend in background
echo -e "${GREEN}Starting backend on http://127.0.0.1:8000${NC}"
(cd "$SCRIPT_DIR/backend" && .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
(cd "$SCRIPT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo -e "\n${GREEN}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

echo -e "${GREEN}Services started!${NC}"
echo -e "${BLUE}Backend: http://127.0.0.1:8000${NC}"
echo -e "${BLUE}Frontend: http://localhost:5173${NC}"
echo -e "${BLUE}API Docs: http://127.0.0.1:8000/docs${NC}"
echo -e "\nPress Ctrl+C to stop all services"

# Wait for processes
wait
