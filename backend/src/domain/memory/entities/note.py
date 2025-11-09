"""Note Entity - Represents a persistent note in the agent's memory."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Note:
    """
    Domain entity representing a persistent note.

    Notes are part of the agent's long-term memory system.
    """

    title: str
    content: str
    thread_id: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: list = field(default_factory=list)

    def __post_init__(self):
        """Validate note invariants."""
        self._validate()

    def _validate(self):
        """
        Validate note business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not self.title or not self.title.strip():
            raise ValueError("Note title cannot be empty")

        if not self.content or not self.content.strip():
            raise ValueError("Note content cannot be empty")

        if not self.thread_id or not self.thread_id.strip():
            raise ValueError("Note must belong to a thread")

    def update_content(self, new_content: str) -> None:
        """
        Update note content.

        Args:
            new_content: New content for the note

        Raises:
            ValueError: If content is empty
        """
        if not new_content or not new_content.strip():
            raise ValueError("Note content cannot be empty")

        object.__setattr__(self, 'content', new_content.strip())
        object.__setattr__(self, 'updated_at', datetime.utcnow())

    def update_title(self, new_title: str) -> None:
        """
        Update note title.

        Args:
            new_title: New title for the note

        Raises:
            ValueError: If title is empty
        """
        if not new_title or not new_title.strip():
            raise ValueError("Note title cannot be empty")

        object.__setattr__(self, 'title', new_title.strip())
        object.__setattr__(self, 'updated_at', datetime.utcnow())

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the note.

        Business rule: Tags are case-insensitive and unique.

        Args:
            tag: Tag to add
        """
        normalized_tag = tag.strip().lower()

        if not normalized_tag:
            raise ValueError("Tag cannot be empty")

        if normalized_tag not in [t.lower() for t in self.tags]:
            self.tags.append(tag.strip())
            object.__setattr__(self, 'updated_at', datetime.utcnow())

    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the note.

        Args:
            tag: Tag to remove (case-insensitive)

        Returns:
            True if tag was removed, False if not found
        """
        normalized_tag = tag.strip().lower()

        for existing_tag in self.tags:
            if existing_tag.lower() == normalized_tag:
                self.tags.remove(existing_tag)
                object.__setattr__(self, 'updated_at', datetime.utcnow())
                return True

        return False

    def has_tag(self, tag: str) -> bool:
        """
        Check if note has a specific tag.

        Args:
            tag: Tag to check (case-insensitive)

        Returns:
            True if note has the tag
        """
        normalized_tag = tag.strip().lower()
        return normalized_tag in [t.lower() for t in self.tags]

    def get_content_preview(self, max_length: int = 200) -> str:
        """
        Get a preview of the note content.

        Args:
            max_length: Maximum length of the preview

        Returns:
            Truncated content with ellipsis if needed
        """
        if len(self.content) <= max_length:
            return self.content

        return self.content[:max_length].strip() + "..."

    def __repr__(self) -> str:
        """Return detailed representation."""
        preview = self.get_content_preview(50)
        return (
            f"Note(id={self.id}, title='{self.title}', "
            f"thread_id='{self.thread_id}', content='{preview}')"
        )
