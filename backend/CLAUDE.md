# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Deep Agent chatbot built with LangGraph and FastAPI. It implements a sophisticated AI agent capable of complex multi-step reasoning, planning, and task execution with persistent memory and file system access.

**Key Features:**
- Deep agent architecture with planning capabilities
- Persistent memory across conversations
- File system for storing notes and context
- Specialized sub-agents for different tasks
- RESTful API with streaming support
- Ollama integration for local LLM inference

## Development Commands

### Environment Setup
```bash
# Install dependencies using Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Running the Application
```bash
# Run the FastAPI development server
poetry run uvicorn main:app --reload

# Run on specific host/port
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application runs on `http://127.0.0.1:8000` by default.

### Dependency Management
```bash
# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>

# Update dependencies
poetry update
```

## Architecture

### Deep Agent Components

Following LangChain's deep agent architecture, this system has four essential components:

1. **Detailed System Prompt** (`agents/deep_agent.py`)
   - Comprehensive instructions for the agent
   - Examples of proper behavior
   - Task-specific guidance

2. **Planning Tool** (`tools/planning_tools.py`)
   - Create and manage multi-step plans
   - Track progress on complex tasks
   - Functions as a "context engineering strategy"

3. **Sub-Agents** (`agents/sub_agents.py`)
   - Research agent: Information retrieval
   - Analyst agent: Data analysis and calculations
   - Conversation agent: Natural dialogue

4. **File System Access** (`tools/file_tools.py`)
   - Save and retrieve notes
   - Store context across sessions
   - Persist intermediate results

### Project Structure

```
deep-chatbot/
├── agents/
│   ├── config.py           # Agent configuration
│   ├── deep_agent.py       # Main deep agent implementation
│   └── sub_agents.py       # Specialized sub-agents
├── tools/
│   ├── custom_tools.py     # General-purpose tools
│   ├── file_tools.py       # File system operations
│   ├── planning_tools.py   # Planning and task management
│   └── handoff_tools.py    # Agent-to-agent communication
├── workspace/              # Agent workspace (created at runtime)
│   ├── notes/             # Saved notes
│   ├── context/           # Saved context
│   └── current_plan.json  # Active plan
└── main.py                # FastAPI application
```

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Send message to deep agent
- `POST /chat/stream` - Stream responses with tool usage
- `GET /plan` - View current plan
- `GET /notes` - List all notes
- `GET /notes/{filename}` - Read specific note
- `DELETE /plan` - Clear current plan

### Technology Stack

- **AI Framework**: LangGraph (1.0.x)
- **LLM**: Ollama (local inference)
- **Web Framework**: FastAPI (0.121.x)
- **ASGI Server**: Uvicorn (0.38.x)
- **State Management**: LangGraph MemorySaver
- **Dependency Management**: Poetry
- **Python Version**: 3.12+

## Development Notes

### Ollama Configuration

The agent uses Ollama for local LLM inference. Default configuration in `agents/config.py`:
- Base URL: `http://localhost:11434`
- Model: `llama3.2` (configurable)

Make sure Ollama is running before starting the application:
```bash
ollama serve
```

### Agent Behavior

The deep agent automatically:
- Creates plans for complex multi-step tasks
- Saves important information to notes
- Maintains conversation context via thread_id
- Uses specialized tools when needed

### Workspace

The `workspace/` directory is created automatically and contains:
- `notes/`: Text files with saved information
- `context/`: JSON files with structured context
- `current_plan.json`: Active plan with steps and progress

### Memory

- **Short-term memory**: Thread-based conversation history (MemorySaver)
- **Long-term memory**: File system (notes and context)
- Each conversation thread maintains its own history via `thread_id`