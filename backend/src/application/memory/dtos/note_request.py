"""NoteRequest DTO - Input data for note operations."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SaveNoteRequest:
    """DTO for saving a new note."""

    thread_id: str
    title: str
    content: str
    tags: List[str] = None

    def __post_init__(self):
        """Validate save note request."""
        if not self.thread_id or not self.thread_id.strip():
            raise ValueError("Thread ID cannot be empty")

        if not self.title or not self.title.strip():
            raise ValueError("Note title cannot be empty")

        if not self.content or not self.content.strip():
            raise ValueError("Note content cannot be empty")

        # Initialize empty tags list if None
        if self.tags is None:
            object.__setattr__(self, 'tags', [])


@dataclass(frozen=True)
class UpdateNoteRequest:
    """DTO for updating an existing note."""

    note_id: int
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        """Validate update note request."""
        if self.note_id < 1:
            raise ValueError(f"Invalid note ID: {self.note_id}")

        # At least one field must be provided for update
        if not any([self.title, self.content, self.tags is not None]):
            raise ValueError(
                "At least one of title, content, or tags must be provided"
            )


@dataclass(frozen=True)
class RetrieveNotesRequest:
    """DTO for retrieving notes with filters."""

    thread_id: Optional[str] = None
    tag: Optional[str] = None
    query: Optional[str] = None
    limit: Optional[int] = None

    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any([
            self.thread_id,
            self.tag,
            self.query,
            self.limit is not None
        ])
