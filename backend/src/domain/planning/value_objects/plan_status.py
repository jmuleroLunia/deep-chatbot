"""PlanStatus Value Object - Represents the status of a plan."""

from enum import Enum


class PlanStatus(str, Enum):
    """
    Enum representing the execution status of a plan.

    Business rules encoded in the status lifecycle.
    """

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        """Return the string value of the status."""
        return self.value

    @classmethod
    def from_string(cls, status: str) -> "PlanStatus":
        """
        Create PlanStatus from a string value.

        Args:
            status: String representation of the status

        Returns:
            PlanStatus enum value

        Raises:
            ValueError: If status is not valid
        """
        try:
            return cls(status.lower())
        except ValueError:
            valid_statuses = ", ".join([s.value for s in cls])
            raise ValueError(
                f"Invalid plan status: '{status}'. "
                f"Valid statuses are: {valid_statuses}"
            )

    def is_active(self) -> bool:
        """Check if plan is currently active."""
        return self == PlanStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if plan has been completed."""
        return self == PlanStatus.COMPLETED

    def is_cancelled(self) -> bool:
        """Check if plan has been cancelled."""
        return self == PlanStatus.CANCELLED

    def can_be_modified(self) -> bool:
        """
        Check if plan can be modified.

        Business rule: Only active plans can be modified.
        """
        return self.is_active()

    def can_transition_to(self, new_status: "PlanStatus") -> bool:
        """
        Check if transition to a new status is valid.

        Business rules:
        - ACTIVE can transition to COMPLETED or CANCELLED
        - COMPLETED cannot transition
        - CANCELLED cannot transition

        Args:
            new_status: Desired new status

        Returns:
            True if transition is allowed
        """
        if self == PlanStatus.ACTIVE:
            return new_status in [PlanStatus.COMPLETED, PlanStatus.CANCELLED]

        # Completed and cancelled are final states
        return False
