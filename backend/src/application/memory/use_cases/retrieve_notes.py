"""RetrieveNotes Use Case - Retrieves notes with optional filters."""

from ....domain.memory import NoteRepository
from ..dtos.note_request import RetrieveNotesRequest
from ..dtos.note_response import NoteResponse, NotesListResponse


class RetrieveNotesUseCase:
    """
    Use case for retrieving notes with filtering options.

    Supports filtering by:
    - Thread ID
    - Tag
    - Search query (content/title)
    - Limit
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
        request: RetrieveNotesRequest
    ) -> NotesListResponse:
        """
        Execute the retrieve notes use case.

        Args:
            request: Retrieve notes request with filters

        Returns:
            Notes list response with matching notes
        """
        # Determine which retrieval method to use based on filters
        if request.query:
            # Search by query
            notes = await self.note_repository.search_notes(
                query=request.query,
                thread_id=request.thread_id
            )
        elif request.tag:
            # Filter by tag
            notes = await self.note_repository.get_notes_by_tag(
                tag=request.tag,
                thread_id=request.thread_id
            )
        elif request.thread_id:
            # Get notes for thread
            notes = await self.note_repository.get_notes_by_thread(
                thread_id=request.thread_id,
                limit=request.limit
            )
        else:
            # Get notes for all threads (if supported)
            # For now, raise error as we require at least thread_id
            raise ValueError(
                "At least one filter must be provided "
                "(thread_id, tag, or query)"
            )

        # Apply limit if specified and not already applied
        if request.limit and not request.thread_id:
            notes = notes[:request.limit]

        # Convert to DTOs
        note_responses = [self._note_to_response(note) for note in notes]

        return NotesListResponse(
            notes=note_responses,
            total_count=len(note_responses)
        )

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
