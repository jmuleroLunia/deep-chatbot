"""NoteRepository Protocol - Abstract interface for note persistence."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.note import Note


class NoteRepository(ABC):
    """
    Abstract repository interface for Note persistence.

    Defines the contract that infrastructure must implement.
    Follows Dependency Inversion Principle.
    """

    @abstractmethod
    async def create_note(self, note: Note) -> Note:
        """
        Create a new note.

        Args:
            note: Note entity to persist

        Returns:
            Note with generated ID

        Raises:
            RepositoryError: If creation fails
        """
        pass

    @abstractmethod
    async def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """
        Retrieve a note by its ID.

        Args:
            note_id: Note identifier

        Returns:
            Note if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_notes_by_thread(
        self,
        thread_id: str,
        limit: Optional[int] = None
    ) -> List[Note]:
        """
        Get all notes for a thread.

        Args:
            thread_id: Thread identifier
            limit: Maximum number of notes to return (None = all)

        Returns:
            List of notes sorted by creation time (newest first)
        """
        pass

    @abstractmethod
    async def get_notes_by_tag(
        self,
        tag: str,
        thread_id: Optional[str] = None
    ) -> List[Note]:
        """
        Get notes by tag, optionally filtered by thread.

        Args:
            tag: Tag to search for (case-insensitive)
            thread_id: Optional thread filter

        Returns:
            List of notes with the specified tag
        """
        pass

    @abstractmethod
    async def search_notes(
        self,
        query: str,
        thread_id: Optional[str] = None
    ) -> List[Note]:
        """
        Search notes by content or title.

        Args:
            query: Search query string
            thread_id: Optional thread filter

        Returns:
            List of matching notes
        """
        pass

    @abstractmethod
    async def update_note(self, note: Note) -> Note:
        """
        Update an existing note.

        Args:
            note: Note entity with updated data

        Returns:
            Updated note

        Raises:
            RepositoryError: If note not found or update fails
        """
        pass

    @abstractmethod
    async def delete_note(self, note_id: int) -> bool:
        """
        Delete a note.

        Args:
            note_id: Note identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def note_exists(self, note_id: int) -> bool:
        """
        Check if a note exists.

        Args:
            note_id: Note identifier

        Returns:
            True if note exists
        """
        pass

    @abstractmethod
    async def get_all_tags(self, thread_id: Optional[str] = None) -> List[str]:
        """
        Get all unique tags, optionally filtered by thread.

        Args:
            thread_id: Optional thread filter

        Returns:
            List of unique tags
        """
        pass
