"""Message Entity - Represents a single message in a conversation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects.message_role import MessageRole


@dataclass
class Message:
    """
    Domain entity representing a single message in a conversation.

    Contains the core business logic and invariants for messages.
    """

    role: MessageRole
    content: str
    thread_id: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate message invariants."""
        self._validate()

    def _validate(self):
        """
        Validate message business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")

        if not self.thread_id or not self.thread_id.strip():
            raise ValueError("Message must belong to a thread")

        if not isinstance(self.role, MessageRole):
            raise ValueError(
                f"Role must be a MessageRole enum, got {type(self.role)}"
            )

    def is_from_user(self) -> bool:
        """Check if message is from a user (human)."""
        return self.role.is_user_message()

    def is_from_ai(self) -> bool:
        """Check if message is from AI."""
        return self.role.is_ai_message()

    def is_system(self) -> bool:
        """Check if message is a system message."""
        return self.role.is_system_message()

    def is_tool_output(self) -> bool:
        """Check if message is a tool execution output."""
        return self.role.is_tool_message()

    def get_content_preview(self, max_length: int = 100) -> str:
        """
        Get a preview of the message content.

        Args:
            max_length: Maximum length of the preview

        Returns:
            Truncated content with ellipsis if needed
        """
        if len(self.content) <= max_length:
            return self.content

        return self.content[:max_length].strip() + "..."

    def add_metadata(self, key: str, value: any) -> None:
        """
        Add metadata to the message.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

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
        preview = self.get_content_preview(50)
        return (
            f"Message(id={self.id}, role={self.role}, "
            f"thread_id='{self.thread_id}', content='{preview}')"
        )
