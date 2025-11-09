"""ThreadId Value Object - Represents a unique conversation thread identifier."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ThreadId:
    """
    Value object representing a unique conversation thread identifier.

    Immutable and validates that the ID is a valid UUID or string.
    """

    value: str

    def __post_init__(self):
        """Validate that the thread ID is not empty."""
        if not self.value or not isinstance(self.value, str):
            raise ValueError("ThreadId must be a non-empty string")

        # Ensure it's stripped of whitespace
        object.__setattr__(self, 'value', self.value.strip())

        if not self.value:
            raise ValueError("ThreadId cannot be empty or whitespace")

    @classmethod
    def generate(cls) -> "ThreadId":
        """Generate a new random ThreadId using UUID4."""
        return cls(value=str(uuid4()))

    @classmethod
    def from_string(cls, thread_id: str) -> "ThreadId":
        """Create ThreadId from a string value."""
        return cls(value=thread_id)

    def __str__(self) -> str:
        """Return the string representation of the ThreadId."""
        return self.value

    def __repr__(self) -> str:
        """Return the detailed representation."""
        return f"ThreadId(value='{self.value}')"
