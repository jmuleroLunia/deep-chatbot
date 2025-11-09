"""ChatResponse DTO - Output data for chat operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ChatResponse:
    """
    Data Transfer Object for chat response output.

    Converts domain entities to API response format.
    """

    response: str
    thread_id: str
    message_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tool_calls: List[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "response": self.response,
            "thread_id": self.thread_id,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "tool_calls": self.tool_calls,
            "metadata": self.metadata
        }
