"""AgentResponse Value Object - Represents an agent's response."""

from dataclasses import dataclass, field
from typing import List, Optional

from .tool_call import ToolCall


@dataclass(frozen=True)
class AgentResponse:
    """
    Value object representing an agent's response.

    Contains the agent's message and any tool calls it wants to make.
    """

    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate agent response invariants."""
        # Agent response can have empty content if it's making tool calls
        if not self.content and not self.tool_calls:
            raise ValueError(
                "AgentResponse must have either content or tool_calls"
            )

        if not isinstance(self.tool_calls, list):
            raise ValueError(
                f"tool_calls must be a list, got {type(self.tool_calls)}"
            )

        for tool_call in self.tool_calls:
            if not isinstance(tool_call, ToolCall):
                raise ValueError(
                    f"All tool_calls must be ToolCall instances, "
                    f"got {type(tool_call)}"
                )

    def has_content(self) -> bool:
        """
        Check if response has text content.

        Returns:
            True if content is non-empty
        """
        return bool(self.content and self.content.strip())

    def has_tool_calls(self) -> bool:
        """
        Check if response includes tool calls.

        Returns:
            True if there are tool calls
        """
        return len(self.tool_calls) > 0

    def get_tool_call_count(self) -> int:
        """
        Get the number of tool calls.

        Returns:
            Number of tool calls
        """
        return len(self.tool_calls)

    def get_tool_calls_by_name(self, tool_name: str) -> List[ToolCall]:
        """
        Get tool calls for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of matching tool calls
        """
        return [tc for tc in self.tool_calls if tc.tool_name == tool_name]

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
        content_preview = self.content[:100] if self.content else ""
        return (
            f"AgentResponse(content='{content_preview}', "
            f"tool_calls={len(self.tool_calls)})"
        )
