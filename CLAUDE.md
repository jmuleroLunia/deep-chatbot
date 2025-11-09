# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack Deep Agent chatbot application with:
- **Backend**: FastAPI + LangGraph implementation of a deep agent with planning, memory, and file system access
- **Frontend**: (To be created) Web interface for interacting with the agent
- **LLM**: Ollama for local inference

## Project Structure

```
deep-chatbot/
├── backend/              # FastAPI backend with Deep Agent
│   ├── agents/          # Agent implementations
│   │   ├── config.py           # Agent configuration
│   │   ├── deep_agent.py       # Main deep agent
│   │   └── sub_agents.py       # Specialized sub-agents
│   ├── tools/           # Agent tools
│   │   ├── custom_tools.py     # General tools
│   │   ├── file_tools.py       # File system operations
│   │   ├── planning_tools.py   # Planning system
│   │   └── handoff_tools.py    # Agent communication
│   ├── workspace/       # Agent workspace (auto-generated)
│   │   ├── notes/
│   │   ├── context/
│   │   └── current_plan.json
│   ├── main.py          # FastAPI application
│   ├── pyproject.toml   # Poetry dependencies
│   └── README.md        # Backend documentation
├── frontend/            # Frontend application (to be created)
└── funcionalidades/     # Feature tracking system
    ├── pendiente/       # Planned features (not started)
    ├── activas/         # Features in active development
    └── completadas/     # Completed features
```

## Development Commands

### Backend

```bash
cd backend

# Install dependencies
poetry install

# Run backend server
poetry run uvicorn main:app --reload

# Or with specific host/port
poetry run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend runs on `http://127.0.0.1:8000` by default.

### Frontend

```bash
cd frontend
# Commands will be added when frontend is created
```

## Development Workflow

### Feature Development Process

**IMPORTANT**: Before implementing ANY new functionality, follow this workflow:

#### 1. Planning Phase (Pendiente)

Create a markdown file in `funcionalidades/pendiente/` with:
- **Filename**: `[feature-name].md` (descriptive, kebab-case)
- **Content structure**:
  ```markdown
  # [Feature Name]

  ## Description
  Brief description of the feature

  ## Tasks
  Break down into testable blocks (usually front + back together):

  ### Task 1: [Name]
  - [ ] Backend: API endpoint/logic
  - [ ] Frontend: UI component/integration
  - [ ] Testing: How to verify it works

  ### Task 2: [Name]
  - [ ] Backend: ...
  - [ ] Frontend: ...
  - [ ] Testing: ...

  ## Acceptance Criteria
  - Feature works end-to-end
  - All tests pass
  - Code is documented
  ```

#### 2. Active Development (Activas)

When starting work on a feature:
1. Move the markdown file from `funcionalidades/pendiente/` to `funcionalidades/activas/`
2. Update the file as you complete tasks (check off items)
3. Work on tasks in testable blocks (complete backend + frontend + testing together)

#### 3. Completion (Completadas)

When the feature is fully implemented and tested:
1. Move the markdown file from `funcionalidades/activas/` to `funcionalidades/completadas/`
2. Ensure all checkboxes are marked
3. Add completion date at the top of the file

### Key Principles

- **Testable Blocks**: Always break features into tasks that combine frontend and backend work
- **Incremental Progress**: Each task should be independently testable
- **Clear Documentation**: Keep the markdown file updated as you progress
- **One Active Feature**: Focus on completing active features before starting new ones

### Example Workflow

```bash
# 1. Create feature plan
# Created: funcionalidades/pendiente/user-authentication.md

# 2. Start development
mv funcionalidades/pendiente/user-authentication.md funcionalidades/activas/

# 3. Complete the feature
mv funcionalidades/activas/user-authentication.md funcionalidades/completadas/
```

## Architecture

### Deep Agent (Backend)

Following LangChain's deep agent architecture with 4 essential components:

1. **Detailed System Prompt** - Comprehensive instructions with examples
2. **Planning Tool** - TODO list system for complex tasks
3. **Sub-Agents** - Specialized agents (research, analyst, conversation)
4. **File System Access** - Persistent notes and context storage

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Send message to deep agent
- `POST /chat/stream` - Stream responses with tool usage
- `GET /plan` - View current plan
- `GET /notes` - List all saved notes
- `GET /notes/{filename}` - Read specific note
- `DELETE /plan` - Clear current plan

API documentation available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Technology Stack

### Backend
- **AI Framework**: LangGraph 1.0.x
- **LLM**: Ollama (local inference)
- **Web Framework**: FastAPI 0.121.x
- **ASGI Server**: Uvicorn 0.38.x
- **State Management**: LangGraph MemorySaver
- **Dependency Management**: Poetry
- **Python**: 3.12+

### Frontend
- To be determined

## Development Notes

### Ollama Setup

The backend requires Ollama running locally:

```bash
# Install Ollama from https://ollama.ai
# Pull the model
ollama pull llama3.2

# Start Ollama server
ollama serve
```

Default configuration in `backend/agents/config.py`:
- Base URL: `http://localhost:11434`
- Model: `llama3.2`

### CORS Configuration

Backend has CORS enabled for frontend development. In production, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Agent Behavior

The deep agent automatically:
- Creates plans for complex multi-step tasks using `create_plan` tool
- Saves important information to notes via `save_note` tool
- Maintains conversation context via `thread_id`
- Uses specialized tools (calculate, analyze_sentiment, search_knowledge_base)

### Memory System

- **Short-term memory**: Thread-based conversation history (MemorySaver)
- **Long-term memory**: File system (workspace/notes/ and workspace/context/)
- Each conversation thread maintains its own history via `thread_id`

### Workspace

The `backend/workspace/` directory contains:
- `notes/`: Text files with saved information
- `context/`: JSON files with structured context
- `current_plan.json`: Active plan with steps and progress

## Testing

### Backend API

```bash
# Health check
curl http://127.0.0.1:8000/health

# Simple chat
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is it?", "thread_id": "test"}'

# Complex task with planning
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Use create_plan to plan a research task", "thread_id": "test"}'

# View plan
curl http://127.0.0.1:8000/plan
```

## Common Tasks

### Adding a New Tool

1. Create tool function in `backend/tools/custom_tools.py`
2. Add tool to `backend/agents/deep_agent.py` in the `all_tools` list
3. Document in system prompt if needed

### Changing the LLM Model

Edit `backend/agents/config.py`:
```python
OLLAMA_MODEL = "your-model-name"  # e.g., "mixtral", "codellama"
```

Then restart the backend.

### Debugging

Backend logs are visible in the terminal where uvicorn is running. For more detailed logs, check the console output for:
- Tool usage
- Agent reasoning
- Error messages
