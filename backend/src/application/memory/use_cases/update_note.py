"""UpdateNote Use Case - Updates an existing note."""

from ....domain.memory import NoteRepository
from ..dtos.note_request import UpdateNoteRequest
from ..dtos.note_response import NoteResponse


class UpdateNoteUseCase:
    """
    Use case for updating an existing note.

    Can update title, content, or tags independently.
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
        request: UpdateNoteRequest
    ) -> NoteResponse:
        """
        Execute the update note use case.

        Args:
            request: Update note request

        Returns:
            Updated note response

        Raises:
            UseCaseError: If note not found
        """
        # Get existing note
        note = await self.note_repository.get_note_by_id(request.note_id)

        if not note:
            raise ValueError(f"Note {request.note_id} not found")

        # Update fields
        if request.title is not None:
            note.update_title(request.title)

        if request.content is not None:
            note.update_content(request.content)

        if request.tags is not None:
            # Replace all tags
            object.__setattr__(note, 'tags', request.tags)

        # Persist
        note = await self.note_repository.update_note(note)

        # Convert to DTO
        return self._note_to_response(note)

    def _note_to_response(self, note) -> NoteResponse:
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
