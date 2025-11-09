#!/bin/bash

# Simple dev script - starts both services

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting Deep Chatbot..."
echo ""

# Start backend
echo "📡 Starting backend..."
osascript -e "tell app \"Terminal\" to do script \"cd '$PROJECT_ROOT/backend' && .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload\""

sleep 1

# Start frontend
echo "🎨 Starting frontend..."
osascript -e "tell app \"Terminal\" to do script \"cd '$PROJECT_ROOT/frontend' && npm run dev\""

echo ""
echo "✅ Services starting in new terminal windows!"
echo ""
echo "URLs:"
echo "  Backend:  http://127.0.0.1:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://127.0.0.1:8000/docs"
