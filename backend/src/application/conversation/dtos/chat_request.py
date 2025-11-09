"""ChatRequest DTO - Input data for chat operations."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChatRequest:
    """
    Data Transfer Object for chat request input.

    Converts API input to application layer format.
    """

    message: str
    thread_id: str
    system_prompt: Optional[str] = None

    def __post_init__(self):
        """Validate chat request."""
        if not self.message or not self.message.strip():
            raise ValueError("Message cannot be empty")

        if not self.thread_id or not self.thread_id.strip():
            raise ValueError("Thread ID cannot be empty")

    @classmethod
    def from_dict(cls, data: dict) -> "ChatRequest":
        """
        Create ChatRequest from dictionary.

        Args:
            data: Dictionary with request data

        Returns:
            ChatRequest instance
        """
        return cls(
            message=data["message"],
            thread_id=data["thread_id"],
            system_prompt=data.get("system_prompt")
        )
