"""Thread Entity - Represents a conversation thread."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .message import Message
from ..value_objects.thread_id import ThreadId


@dataclass
class Thread:
    """
    Domain entity representing a conversation thread.

    A thread is a collection of messages that form a coherent conversation.
    Contains business logic for managing conversation flow.
    """

    thread_id: ThreadId
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[Message] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate thread invariants."""
        self._validate()

    def _validate(self):
        """
        Validate thread business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not isinstance(self.thread_id, ThreadId):
            raise ValueError(
                f"thread_id must be a ThreadId instance, got {type(self.thread_id)}"
            )

    def add_message(self, message: Message) -> None:
        """
        Add a message to the thread.

        Business rule: Message must belong to this thread.

        Args:
            message: Message to add

        Raises:
            ValueError: If message doesn't belong to this thread
        """
        if message.thread_id != str(self.thread_id):
            raise ValueError(
                f"Message thread_id '{message.thread_id}' "
                f"doesn't match thread '{self.thread_id}'"
            )

        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def get_messages(self) -> List[Message]:
        """
        Get all messages in chronological order.

        Returns:
            List of messages sorted by creation time
        """
        return sorted(self.messages, key=lambda m: m.created_at)

    def get_last_message(self) -> Optional[Message]:
        """
        Get the most recent message in the thread.

        Returns:
            Last message or None if thread is empty
        """
        if not self.messages:
            return None

        return max(self.messages, key=lambda m: m.created_at)

    def get_message_count(self) -> int:
        """
        Get the total number of messages in the thread.

        Returns:
            Number of messages
        """
        return len(self.messages)

    def get_user_messages(self) -> List[Message]:
        """
        Get only user (human) messages.

        Returns:
            List of user messages
        """
        return [m for m in self.messages if m.is_from_user()]

    def get_ai_messages(self) -> List[Message]:
        """
        Get only AI messages.

        Returns:
            List of AI messages
        """
        return [m for m in self.messages if m.is_from_ai()]

    def is_empty(self) -> bool:
        """
        Check if thread has no messages.

        Returns:
            True if thread is empty
        """
        return len(self.messages) == 0

    def add_metadata(self, key: str, value: any) -> None:
        """
        Add metadata to the thread.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def get_metadata(self, key: str, default: any = None) -> any:
        """
        Get metadata value by key.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"Thread(id={self.id}, thread_id={self.thread_id}, "
            f"messages={len(self.messages)}, "
            f"created_at={self.created_at.isoformat()})"
        )
