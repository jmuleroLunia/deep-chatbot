"""SaveNote Use Case - Saves a new note to memory."""

from ....domain.memory import Note, NoteRepository
from ..dtos.note_request import SaveNoteRequest
from ..dtos.note_response import NoteResponse


class SaveNoteUseCase:
    """
    Use case for saving a new note.

    Notes are part of the agent's long-term memory.
    """

    def __init__(self, note_repository: NoteRepository):
        """
        Initialize use case with dependencies.

        Args:
            note_repository: Repository for note persistence
        """
        self.note_repository = note_repository

    async def execute(
        self,
        request: SaveNoteRequest
    ) -> NoteResponse:
        """
        Execute the save note use case.

        Args:
            request: Save note request with title and content

        Returns:
            Note response with saved note
        """
        # Create note entity
        note = Note(
            thread_id=request.thread_id,
            title=request.title,
            content=request.content,
            tags=request.tags or []
        )

        # Persist
        note = await self.note_repository.create_note(note)

        # Convert to DTO
        return self._note_to_response(note)

    def _note_to_response(self, note: Note) -> NoteResponse:
        """Convert domain Note to NoteResponse DTO."""
        return NoteResponse(
            note_id=note.id or 0,
            thread_id=note.thread_id,
            title=note.title,
            content=note.content,
            tags=note.tags,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat()
        )
