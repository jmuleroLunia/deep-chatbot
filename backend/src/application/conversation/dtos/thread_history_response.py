"""ThreadHistoryResponse DTO - Output data for conversation history."""

from dataclasses import dataclass
from typing import List


@dataclass
class MessageDTO:
    """DTO for a single message in history."""

    role: str
    content: str
    timestamp: str
    message_id: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }


@dataclass
class ThreadHistoryResponse:
    """
    Data Transfer Object for thread history output.

    Contains all messages in a conversation thread.
    """

    thread_id: str
    messages: List[MessageDTO]
    total_messages: int

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "thread_id": self.thread_id,
            "messages": [m.to_dict() for m in self.messages],
            "total_messages": self.total_messages
        }
