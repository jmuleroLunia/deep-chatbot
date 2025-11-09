# Deep Agent Chatbot

Full-stack chatbot application with a Deep Agent implementation using LangGraph, FastAPI, and React.

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry
- Ollama (for local LLM inference)

### Starting the Application

**Option 1: Using Makefile (Recommended)**

```bash
# Start both frontend and backend
make start

# Or start them separately
make backend   # Only backend
make frontend  # Only frontend
```

**Option 2: Using Shell Scripts**

```bash
# Start both
./start.sh

# Or separately
./start-backend.sh
./start-frontend.sh
```

**Option 3: Manual**

```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## Installation

```bash
# Install all dependencies
make install

# Or manually
cd backend && poetry install
cd frontend && npm install
```

## Available Commands

```bash
make start      # Start both services
make backend    # Start only backend
make frontend   # Start only frontend
make install    # Install dependencies
make stop       # Stop all services
make help       # Show help
```

## Project Structure

```
deep-chatbot/
├── backend/              # FastAPI + LangGraph backend
│   ├── agents/          # Agent implementations
│   ├── tools/           # Agent tools
│   ├── workspace/       # Agent workspace (auto-generated)
│   └── main.py          # FastAPI app
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # React components
│       └── App.jsx      # Main app
└── funcionalidades/     # Feature tracking
    ├── pendiente/       # Planned features
    ├── activas/         # Active features
    └── completadas/     # Completed features
```

## Development

See [CLAUDE.md](./CLAUDE.md) for detailed development instructions and architecture documentation.

## Technology Stack

**Backend:**
- FastAPI
- LangGraph 1.0.x
- Ollama (llama3.2)
- Python 3.12+

**Frontend:**
- React 19
- Vite
- Tailwind CSS
- Axios

## Stopping Services

```bash
# Using Makefile
make stop

# Or manually kill processes
pkill -f "uvicorn main:app"
pkill -f "vite"
```
