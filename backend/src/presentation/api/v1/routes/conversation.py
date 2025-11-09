"""Conversation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .....application.conversation import (
    ChatRequest,
    GetThreadHistoryUseCase,
    SendMessageUseCase,
    StreamChatUseCase,
)
from ..dependencies import (
    get_get_thread_history_use_case,
    get_send_message_use_case,
    get_stream_chat_use_case,
    get_thread_repository,
)

router = APIRouter(prefix="/conversations", tags=["conversation"])


# ===== Request/Response Models =====


class CreateThreadRequest(BaseModel):
    """Request model for creating a thread."""

    thread_id: str | None = None


class UpdateThreadRequest(BaseModel):
    """Request model for updating a thread."""

    title: str


class ThreadListResponse(BaseModel):
    """Response model for thread list."""

    threads: list[dict]


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""

    message: str
    thread_id: str
    system_prompt: str | None = None


class MessageResponse(BaseModel):
    """Response model for a single message."""

    role: str
    content: str
    timestamp: str
    message_id: int


class ThreadHistoryResponse(BaseModel):
    """Response model for thread history."""

    thread_id: str
    messages: list[MessageResponse]
    total_messages: int


# ===== Endpoints =====


@router.post("/send", status_code=status.HTTP_200_OK)
async def send_message(
    request: SendMessageRequest,
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
):
    """
    Send a message and get AI response.

    Args:
        request: Message request with content and thread_id
        use_case: Injected SendMessageUseCase

    Returns:
        AI response with message content
    """
    try:
        chat_request = ChatRequest(
            message=request.message,
            thread_id=request.thread_id,
            system_prompt=request.system_prompt,
        )

        response = await use_case.execute(chat_request)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )


@router.post("/stream", status_code=status.HTTP_200_OK)
async def stream_message(
    request: SendMessageRequest,
    use_case: StreamChatUseCase = Depends(get_stream_chat_use_case),
):
    """
    Stream AI response token by token.

    Args:
        request: Message request with content and thread_id
        use_case: Injected StreamChatUseCase

    Returns:
        Streaming response with AI tokens
    """
    try:
        chat_request = ChatRequest(
            message=request.message,
            thread_id=request.thread_id,
            system_prompt=request.system_prompt,
        )

        async def generate():
            async for token in use_case.execute(chat_request):
                yield token

        return StreamingResponse(generate(), media_type="text/plain")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream message: {str(e)}",
        )


@router.get("/{thread_id}/messages", status_code=status.HTTP_200_OK)
async def get_thread_history(
    thread_id: str,
    limit: int | None = None,
    use_case: GetThreadHistoryUseCase = Depends(get_get_thread_history_use_case),
):
    """
    Get conversation history for a thread.

    Args:
        thread_id: Thread identifier
        limit: Optional limit on number of messages
        use_case: Injected GetThreadHistoryUseCase

    Returns:
        Thread history with messages
    """
    try:
        response = await use_case.execute(thread_id, limit)

        return response.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_thread(
    request: CreateThreadRequest,
    thread_repository=Depends(get_thread_repository),
):
    """
    Create a new conversation thread.

    Args:
        request: Thread creation request with optional thread_id

    Returns:
        Created thread information
    """
    try:
        from .....domain.conversation import Thread, ThreadId

        thread_id = (
            ThreadId.from_string(request.thread_id)
            if request.thread_id
            else ThreadId.generate()
        )

        thread = Thread(thread_id=thread_id)
        created_thread = await thread_repository.create_thread(thread)

        return {
            "id": str(created_thread.thread_id),
            "thread_id": str(created_thread.thread_id),
            "title": created_thread.metadata.get("title", "New Conversation"),
            "created_at": created_thread.created_at.isoformat(),
            "updated_at": created_thread.updated_at.isoformat() if created_thread.updated_at else created_thread.created_at.isoformat(),
            "metadata": created_thread.metadata,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create thread: {str(e)}",
        )


@router.get("", status_code=status.HTTP_200_OK)
async def list_threads(thread_repository=Depends(get_thread_repository)):
    """
    List all conversation threads.

    Returns:
        List of threads with their metadata
    """
    try:
        threads = await thread_repository.list_all_threads()

        # Convert Thread entities to dict format
        threads_data = [
            {
                "id": str(thread.thread_id),
                "title": thread.metadata.get("title", "New Conversation"),
                "created_at": thread.created_at.isoformat(),
                "updated_at": thread.updated_at.isoformat() if thread.updated_at else thread.created_at.isoformat(),
                "metadata": thread.metadata,
            }
            for thread in threads
        ]

        return {"threads": threads_data}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list threads: {str(e)}",
        )


@router.put("/{thread_id}", status_code=status.HTTP_200_OK)
async def update_thread(
    thread_id: str,
    request: UpdateThreadRequest,
    thread_repository=Depends(get_thread_repository),
):
    """
    Update thread metadata (e.g. title).

    Args:
        thread_id: Thread identifier
        request: Update request with new title

    Returns:
        Updated thread information
    """
    try:
        from .....domain.conversation import ThreadId

        tid = ThreadId.from_string(thread_id)

        # Update metadata with title
        metadata = {"title": request.title}
        success = await thread_repository.update_thread_metadata(tid, metadata)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

        # Retrieve updated thread to return complete structure
        updated_thread = await thread_repository.get_thread_by_id(tid)

        return {
            "id": str(updated_thread.thread_id),
            "thread_id": str(updated_thread.thread_id),
            "title": updated_thread.metadata.get("title", "New Conversation"),
            "created_at": updated_thread.created_at.isoformat(),
            "updated_at": updated_thread.updated_at.isoformat() if updated_thread.updated_at else updated_thread.created_at.isoformat(),
            "metadata": updated_thread.metadata,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update thread: {str(e)}",
        )


@router.delete("/{thread_id}", status_code=status.HTTP_200_OK)
async def delete_thread(
    thread_id: str, thread_repository=Depends(get_thread_repository)
):
    """
    Delete a conversation thread and all its messages.

    Args:
        thread_id: Thread identifier

    Returns:
        Deletion confirmation
    """
    try:
        from .....domain.conversation import ThreadId

        tid = ThreadId.from_string(thread_id)

        success = await thread_repository.delete_thread(tid)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

        return {"message": "Thread deleted successfully", "thread_id": thread_id}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete thread: {str(e)}",
        )
