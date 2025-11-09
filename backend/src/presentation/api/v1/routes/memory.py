"""Memory API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from .....application.memory import (
    RetrieveNotesRequest,
    RetrieveNotesUseCase,
    SaveNoteRequest,
    SaveNoteUseCase,
    UpdateNoteRequest,
    UpdateNoteUseCase,
)
from ..dependencies import (
    get_retrieve_notes_use_case,
    get_save_note_use_case,
    get_update_note_use_case,
)

router = APIRouter(prefix="/memory", tags=["memory"])


# ===== Request Models =====


class SaveNoteRequestModel(BaseModel):
    """Request model for saving a note."""

    thread_id: str
    title: str
    content: str
    tags: list[str] | None = None


class UpdateNoteRequestModel(BaseModel):
    """Request model for updating a note."""

    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


# ===== Endpoints =====


@router.post("/notes", status_code=status.HTTP_201_CREATED)
async def save_note(
    request: SaveNoteRequestModel,
    use_case: SaveNoteUseCase = Depends(get_save_note_use_case),
):
    """
    Save a new note.

    Args:
        request: Note creation request
        use_case: Injected SaveNoteUseCase

    Returns:
        Created note
    """
    try:
        note_request = SaveNoteRequest(
            thread_id=request.thread_id,
            title=request.title,
            content=request.content,
            tags=request.tags or [],
        )

        response = await use_case.execute(note_request)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save note: {str(e)}",
        )


@router.get("/notes", status_code=status.HTTP_200_OK)
async def get_notes(
    thread_id: str | None = None,
    tag: str | None = None,
    query: str | None = None,
    limit: int | None = None,
    use_case: RetrieveNotesUseCase = Depends(get_retrieve_notes_use_case),
):
    """
    Retrieve notes with optional filters.

    Args:
        thread_id: Optional thread filter
        tag: Optional tag filter
        query: Optional search query
        limit: Optional limit
        use_case: Injected RetrieveNotesUseCase

    Returns:
        List of matching notes
    """
    try:
        retrieve_request = RetrieveNotesRequest(
            thread_id=thread_id,
            tag=tag,
            query=query,
            limit=limit,
        )

        response = await use_case.execute(retrieve_request)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve notes: {str(e)}",
        )


@router.put("/notes/{note_id}", status_code=status.HTTP_200_OK)
async def update_note(
    note_id: int,
    request: UpdateNoteRequestModel,
    use_case: UpdateNoteUseCase = Depends(get_update_note_use_case),
):
    """
    Update an existing note.

    Args:
        note_id: Note identifier
        request: Note update request
        use_case: Injected UpdateNoteUseCase

    Returns:
        Updated note
    """
    try:
        update_request = UpdateNoteRequest(
            note_id=note_id,
            title=request.title,
            content=request.content,
            tags=request.tags,
        )

        response = await use_case.execute(update_request)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update note: {str(e)}",
        )
