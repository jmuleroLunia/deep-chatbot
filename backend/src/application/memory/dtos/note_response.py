"""NoteResponse DTO - Output data for note operations."""

from dataclasses import dataclass
from typing import List


@dataclass
class NoteResponse:
    """DTO for note output."""

    note_id: int
    thread_id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "note_id": self.note_id,
            "thread_id": self.thread_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class NotesListResponse:
    """DTO for list of notes."""

    notes: List[NoteResponse]
    total_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "notes": [n.to_dict() for n in self.notes],
            "total_count": self.total_count
        }
