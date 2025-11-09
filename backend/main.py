from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json
from pathlib import Path

from agents.deep_agent import create_deep_agent

# Initialize FastAPI app
app = FastAPI(
    title="Deep Agent Chatbot",
    description="AI chatbot with planning, memory, and file system capabilities using LangGraph",
    version="1.0.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the deep agent
deep_agent = create_deep_agent()

# Workspace paths
WORKSPACE_DIR = Path("workspace")
PLAN_FILE = WORKSPACE_DIR / "current_plan.json"
NOTES_DIR = WORKSPACE_DIR / "notes"


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    thread_id: str


class PlanResponse(BaseModel):
    task: Optional[str] = None
    status: Optional[str] = None
    steps: Optional[List[dict]] = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Deep Agent Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a message to the deep agent",
            "POST /chat/stream": "Stream responses from the deep agent",
            "GET /plan": "View the current plan",
            "GET /notes": "List all saved notes",
            "GET /notes/{filename}": "Read a specific note",
            "GET /health": "Check API health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "ready"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the deep agent and get a response.

    The agent will use planning tools for complex tasks and save important
    information to the file system.
    """
    try:
        # Prepare config with thread_id for conversation memory
        config = {"configurable": {"thread_id": request.thread_id}}

        # Invoke the agent
        result = deep_agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config,
        )

        # Extract the last message (agent's response)
        last_message = result["messages"][-1]
        response_text = last_message.content

        return ChatResponse(response=response_text, thread_id=request.thread_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.options("/chat/stream")
async def chat_stream_options():
    """Handle CORS preflight for streaming endpoint."""
    return {"message": "OK"}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream responses from the deep agent.

    This endpoint streams the agent's thought process and tool usage in real-time.
    """

    async def event_generator():
        try:
            config = {"configurable": {"thread_id": request.thread_id}}

            # Stream the agent's responses
            async for event in deep_agent.astream_events(
                {"messages": [{"role": "user", "content": request.message}]},
                config=config,
                version="v2",
            ):
                # Send different types of events
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

                elif event["event"] == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event.get("data", {}).get("input", {})
                    yield f"data: {json.dumps({'type': 'tool_call', 'name': tool_name, 'args': tool_input})}\n\n"

                elif event["event"] == "on_tool_end":
                    tool_name = event["name"]
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': tool_name})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/plan", response_model=PlanResponse)
async def get_plan():
    """
    Get the current plan from the workspace.

    Returns the active plan with all steps and their completion status.
    """
    if not PLAN_FILE.exists():
        return PlanResponse()

    try:
        plan_data = json.loads(PLAN_FILE.read_text())
        return PlanResponse(**plan_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading plan: {str(e)}")


@app.get("/notes")
async def list_notes():
    """
    List all notes saved in the workspace.

    Returns a list of note filenames.
    """
    if not NOTES_DIR.exists():
        return {"notes": []}

    notes = sorted(NOTES_DIR.glob("*.txt"))
    return {"notes": [n.name for n in notes]}


@app.get("/notes/{filename}")
async def read_note(filename: str):
    """
    Read the content of a specific note.

    Args:
        filename: The name of the note file to read
    """
    filepath = NOTES_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Note not found: {filename}")

    try:
        content = filepath.read_text()
        return {"filename": filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading note: {str(e)}")


@app.delete("/plan")
async def clear_plan():
    """
    Clear the current plan.

    Useful for starting fresh with a new task.
    """
    if PLAN_FILE.exists():
        PLAN_FILE.unlink()
        return {"message": "Plan cleared successfully"}
    return {"message": "No plan to clear"}
