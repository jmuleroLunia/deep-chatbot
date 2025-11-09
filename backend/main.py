from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import json
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc, func
from sqlalchemy.orm import selectinload

from agents.deep_agent import create_deep_agent, get_checkpointer
from database import init_db, close_db, get_db, async_session_factory
from models import Thread, Message

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

# Deep agent will be initialized on startup
deep_agent = None

# Workspace paths
WORKSPACE_DIR = Path("workspace")
PLAN_FILE = WORKSPACE_DIR / "current_plan.json"
NOTES_DIR = WORKSPACE_DIR / "notes"


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database and deep agent on startup."""
    global deep_agent
    await init_db()
    # Initialize checkpointer and create agent with it
    checkpointer = await get_checkpointer()
    deep_agent = create_deep_agent(checkpointer=checkpointer)


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_db()


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


# Thread management models
class ThreadCreate(BaseModel):
    title: Optional[str] = None


class ThreadUpdate(BaseModel):
    title: str


class ThreadResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
    tool_calls: Optional[dict] = None

    class Config:
        from_attributes = True


class ThreadWithMessages(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


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
            "POST /threads": "Create a new conversation thread",
            "GET /threads": "List all threads",
            "GET /threads/{thread_id}": "Get a specific thread with messages",
            "PUT /threads/{thread_id}": "Update thread title",
            "DELETE /threads/{thread_id}": "Delete a thread",
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

    Messages are persisted both in LangGraph's checkpointer and our database.
    """

    async def event_generator():
        assistant_content = ""
        try:
            # Save user message to database
            async with async_session_factory() as db:
                user_message = Message(
                    thread_id=request.thread_id,
                    role="user",
                    content=request.message,
                    timestamp=datetime.now(timezone.utc)
                )
                db.add(user_message)

                # Update thread's updated_at
                result = await db.execute(
                    select(Thread).where(Thread.id == request.thread_id)
                )
                thread = result.scalar_one_or_none()
                if thread:
                    thread.updated_at = datetime.now(timezone.utc)

                await db.commit()

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
                        assistant_content += chunk.content
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

                elif event["event"] == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event.get("data", {}).get("input", {})
                    yield f"data: {json.dumps({'type': 'tool_call', 'name': tool_name, 'args': tool_input})}\n\n"

                elif event["event"] == "on_tool_end":
                    tool_name = event["name"]
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': tool_name})}\n\n"

            # Save assistant message to database
            if assistant_content:
                async with async_session_factory() as db:
                    assistant_message = Message(
                        thread_id=request.thread_id,
                        role="assistant",
                        content=assistant_content,
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.add(assistant_message)
                    await db.commit()

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


# ============================================================================
# THREAD MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/threads", response_model=ThreadResponse)
async def create_thread(
    thread_data: ThreadCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conversation thread.

    If no title is provided, it will be set to "New Conversation" initially.
    The title can be auto-generated from the first message or updated manually.
    """
    try:
        # Generate a new thread ID
        thread_id = str(uuid.uuid4())

        # Create new thread
        new_thread = Thread(
            id=thread_id,
            title=thread_data.title or "New Conversation",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(new_thread)
        await db.commit()
        await db.refresh(new_thread)

        return ThreadResponse(
            id=new_thread.id,
            title=new_thread.title,
            created_at=new_thread.created_at,
            updated_at=new_thread.updated_at,
            message_count=0
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")


@app.get("/threads", response_model=List[ThreadResponse])
async def list_threads(db: AsyncSession = Depends(get_db)):
    """
    List all conversation threads, ordered by most recently updated.

    Returns a list of threads with their basic information and message count.
    """
    try:
        # Query threads with message count, ordered by updated_at descending
        stmt = (
            select(
                Thread.id,
                Thread.title,
                Thread.created_at,
                Thread.updated_at,
                func.count(Message.id).label("message_count")
            )
            .outerjoin(Message, Thread.id == Message.thread_id)
            .group_by(Thread.id, Thread.title, Thread.created_at, Thread.updated_at)
            .order_by(desc(Thread.updated_at))
        )

        result = await db.execute(stmt)
        threads = result.all()

        # Build response
        thread_responses = [
            ThreadResponse(
                id=row.id,
                title=row.title,
                created_at=row.created_at,
                updated_at=row.updated_at,
                message_count=row.message_count
            )
            for row in threads
        ]

        return thread_responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing threads: {str(e)}")


@app.get("/threads/{thread_id}", response_model=ThreadWithMessages)
async def get_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific thread with all its messages.

    Args:
        thread_id: The UUID of the thread to retrieve

    Returns:
        Thread with all associated messages ordered by timestamp
    """
    try:
        # Use selectinload to eagerly load messages
        result = await db.execute(
            select(Thread)
            .options(selectinload(Thread.messages))
            .where(Thread.id == thread_id)
        )
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread not found: {thread_id}")

        # Convert messages to response format
        message_responses = [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                tool_calls=msg.tool_calls
            )
            for msg in thread.messages
        ]

        return ThreadWithMessages(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            messages=message_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving thread: {str(e)}")


@app.put("/threads/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: str,
    thread_update: ThreadUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a thread's title.

    Args:
        thread_id: The UUID of the thread to update
        thread_update: New thread data (title)

    Returns:
        Updated thread information
    """
    try:
        result = await db.execute(
            select(Thread).where(Thread.id == thread_id)
        )
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread not found: {thread_id}")

        # Update thread
        thread.title = thread_update.title
        thread.updated_at = datetime.now(timezone.utc)

        await db.commit()

        # Get message count
        count_result = await db.execute(
            select(func.count(Message.id)).where(Message.thread_id == thread_id)
        )
        message_count = count_result.scalar()

        return ThreadResponse(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            message_count=message_count
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating thread: {str(e)}")


@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a thread and all its associated messages.

    Args:
        thread_id: The UUID of the thread to delete

    Returns:
        Success message
    """
    try:
        result = await db.execute(
            select(Thread).where(Thread.id == thread_id)
        )
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread not found: {thread_id}")

        # Delete thread (messages will be cascade deleted)
        await db.delete(thread)
        await db.commit()

        return {"message": f"Thread {thread_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting thread: {str(e)}")
