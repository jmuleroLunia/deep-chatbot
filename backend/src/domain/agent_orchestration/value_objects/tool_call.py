"""ToolCall Value Object - Represents a tool invocation request."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ToolCall:
    """
    Value object representing a tool invocation request from an agent.

    Immutable representation of tool execution parameters.
    """

    tool_name: str
    arguments: Dict[str, Any]
    call_id: str

    def __post_init__(self):
        """Validate tool call invariants."""
        if not self.tool_name or not self.tool_name.strip():
            raise ValueError("Tool name cannot be empty")

        if not isinstance(self.arguments, dict):
            raise ValueError(f"Arguments must be a dict, got {type(self.arguments)}")

        if not self.call_id or not self.call_id.strip():
            raise ValueError("Call ID cannot be empty")

    def get_argument(self, key: str, default: Any = None) -> Any:
        """
        Get an argument value by key.

        Args:
            key: Argument key
            default: Default value if key not found

        Returns:
            Argument value or default
        """
        return self.arguments.get(key, default)

    def has_argument(self, key: str) -> bool:
        """
        Check if tool call has a specific argument.

        Args:
            key: Argument key

        Returns:
            True if argument exists
        """
        return key in self.arguments

    def __repr__(self) -> str:
        """Return detailed representation."""
        args_preview = str(self.arguments)[:100]
        return (
            f"ToolCall(tool_name='{self.tool_name}', "
            f"call_id='{self.call_id}', arguments={args_preview})"
        )
