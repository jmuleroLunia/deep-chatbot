"""Step Entity - Represents a single step in a plan."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Step:
    """
    Domain entity representing a single step in a plan.

    Encapsulates step business logic and validation rules.
    """

    description: str
    step_number: int
    plan_id: Optional[int] = None
    id: Optional[int] = None
    completed: bool = False
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate step invariants."""
        self._validate()

    def _validate(self):
        """
        Validate step business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not self.description or not self.description.strip():
            raise ValueError("Step description cannot be empty")

        if self.step_number < 1:
            raise ValueError(f"Step number must be >= 1, got {self.step_number}")

        if self.completed and self.completed_at is None:
            # Auto-set completion time if not provided
            object.__setattr__(self, 'completed_at', datetime.utcnow())

        if not self.completed and self.completed_at is not None:
            raise ValueError(
                "Step marked as not completed but has completion timestamp"
            )

    def mark_completed(self) -> None:
        """
        Mark step as completed.

        Business rule: Sets completion timestamp to current UTC time.
        """
        if self.completed:
            # Already completed, no-op
            return

        object.__setattr__(self, 'completed', True)
        object.__setattr__(self, 'completed_at', datetime.utcnow())

    def mark_incomplete(self) -> None:
        """
        Mark step as incomplete.

        Business rule: Clears completion timestamp.
        """
        if not self.completed:
            # Already incomplete, no-op
            return

        object.__setattr__(self, 'completed', False)
        object.__setattr__(self, 'completed_at', None)

    def is_completed(self) -> bool:
        """Check if step is completed."""
        return self.completed

    def get_description_preview(self, max_length: int = 100) -> str:
        """
        Get a preview of the step description.

        Args:
            max_length: Maximum length of the preview

        Returns:
            Truncated description with ellipsis if needed
        """
        if len(self.description) <= max_length:
            return self.description

        return self.description[:max_length].strip() + "..."

    def __repr__(self) -> str:
        """Return detailed representation."""
        status = "✓" if self.completed else "○"
        preview = self.get_description_preview(50)
        return (
            f"Step(#{self.step_number} {status} '{preview}', "
            f"plan_id={self.plan_id})"
        )
