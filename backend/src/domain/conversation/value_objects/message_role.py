"""MessageRole Value Object - Represents the role of a message in a conversation."""

from enum import Enum


class MessageRole(str, Enum):
    """
    Enum representing the role of a message sender in a conversation.

    Follows LangChain/LangGraph message conventions.
    """

    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL = "tool"

    def __str__(self) -> str:
        """Return the string value of the role."""
        return self.value

    @classmethod
    def from_string(cls, role: str) -> "MessageRole":
        """
        Create MessageRole from a string value.

        Args:
            role: String representation of the role

        Returns:
            MessageRole enum value

        Raises:
            ValueError: If role is not valid
        """
        # Map legacy role names to new ones
        role_mapping = {
            "user": "human",
            "assistant": "ai",
        }

        normalized_role = role.lower()
        # Apply legacy mapping if needed
        normalized_role = role_mapping.get(normalized_role, normalized_role)

        try:
            return cls(normalized_role)
        except ValueError:
            valid_roles = ", ".join([r.value for r in cls])
            raise ValueError(
                f"Invalid message role: '{role}'. "
                f"Valid roles are: {valid_roles}"
            )

    def is_user_message(self) -> bool:
        """Check if this is a user (human) message."""
        return self == MessageRole.HUMAN

    def is_ai_message(self) -> bool:
        """Check if this is an AI message."""
        return self == MessageRole.AI

    def is_system_message(self) -> bool:
        """Check if this is a system message."""
        return self == MessageRole.SYSTEM

    def is_tool_message(self) -> bool:
        """Check if this is a tool execution message."""
        return self == MessageRole.TOOL
