"""Plan Entity - Represents a plan with multiple steps."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .step import Step
from ..value_objects.plan_status import PlanStatus


@dataclass
class Plan:
    """
    Domain entity representing a plan with multiple steps.

    Encapsulates planning business logic and step management.
    """

    thread_id: str
    title: str
    steps: List[Step] = field(default_factory=list)
    id: Optional[int] = None
    status: PlanStatus = PlanStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate plan invariants."""
        self._validate()

    def _validate(self):
        """
        Validate plan business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not self.thread_id or not self.thread_id.strip():
            raise ValueError("Plan must belong to a thread")

        if not self.title or not self.title.strip():
            raise ValueError("Plan title cannot be empty")

        if not isinstance(self.status, PlanStatus):
            raise ValueError(
                f"Status must be a PlanStatus enum, got {type(self.status)}"
            )

        # Validate steps numbering
        for idx, step in enumerate(self.steps, start=1):
            if step.step_number != idx:
                raise ValueError(
                    f"Step numbering is invalid: expected {idx}, got {step.step_number}"
                )

    def add_step(self, description: str) -> Step:
        """
        Add a new step to the plan.

        Business rule: Steps are auto-numbered sequentially.

        Args:
            description: Step description

        Returns:
            Created step

        Raises:
            ValueError: If plan cannot be modified
        """
        if not self.status.can_be_modified():
            raise ValueError(
                f"Cannot add steps to a {self.status} plan. "
                f"Only {PlanStatus.ACTIVE} plans can be modified."
            )

        step_number = len(self.steps) + 1
        step = Step(
            description=description,
            step_number=step_number,
            plan_id=self.id
        )

        self.steps.append(step)
        self.updated_at = datetime.utcnow()

        return step

    def get_step(self, step_number: int) -> Optional[Step]:
        """
        Get a step by its number.

        Args:
            step_number: Step number (1-indexed)

        Returns:
            Step if found, None otherwise
        """
        if step_number < 1 or step_number > len(self.steps):
            return None

        return self.steps[step_number - 1]

    def complete_step(self, step_number: int) -> bool:
        """
        Mark a step as completed.

        Args:
            step_number: Step number to complete

        Returns:
            True if step was marked completed, False if not found

        Raises:
            ValueError: If plan is not active
        """
        if not self.status.can_be_modified():
            raise ValueError(
                f"Cannot modify steps in a {self.status} plan"
            )

        step = self.get_step(step_number)
        if not step:
            return False

        step.mark_completed()
        self.updated_at = datetime.utcnow()

        # Auto-complete plan if all steps are done
        if self.are_all_steps_completed():
            self.mark_completed()

        return True

    def are_all_steps_completed(self) -> bool:
        """
        Check if all steps are completed.

        Returns:
            True if all steps are completed or plan has no steps
        """
        if not self.steps:
            return True

        return all(step.is_completed() for step in self.steps)

    def get_completion_percentage(self) -> float:
        """
        Get plan completion percentage.

        Returns:
            Percentage (0.0 to 100.0)
        """
        if not self.steps:
            return 100.0

        completed_count = sum(1 for step in self.steps if step.is_completed())
        return (completed_count / len(self.steps)) * 100.0

    def mark_completed(self) -> None:
        """
        Mark plan as completed.

        Business rule: Can only complete from ACTIVE status.

        Raises:
            ValueError: If plan is not active or has incomplete steps
        """
        if not self.status.is_active():
            raise ValueError(f"Cannot complete a {self.status} plan")

        if not self.are_all_steps_completed():
            raise ValueError(
                "Cannot complete plan: not all steps are completed"
            )

        object.__setattr__(self, 'status', PlanStatus.COMPLETED)
        object.__setattr__(self, 'completed_at', datetime.utcnow())
        object.__setattr__(self, 'updated_at', datetime.utcnow())

    def cancel(self) -> None:
        """
        Cancel the plan.

        Business rule: Can only cancel from ACTIVE status.

        Raises:
            ValueError: If plan is not active
        """
        if not self.status.is_active():
            raise ValueError(f"Cannot cancel a {self.status} plan")

        object.__setattr__(self, 'status', PlanStatus.CANCELLED)
        object.__setattr__(self, 'updated_at', datetime.utcnow())

    def get_pending_steps(self) -> List[Step]:
        """
        Get all pending (incomplete) steps.

        Returns:
            List of incomplete steps
        """
        return [step for step in self.steps if not step.is_completed()]

    def get_completed_steps(self) -> List[Step]:
        """
        Get all completed steps.

        Returns:
            List of completed steps
        """
        return [step for step in self.steps if step.is_completed()]

    def __repr__(self) -> str:
        """Return detailed representation."""
        completion = self.get_completion_percentage()
        return (
            f"Plan(id={self.id}, thread_id='{self.thread_id}', "
            f"title='{self.title}', status={self.status}, "
            f"steps={len(self.steps)}, completion={completion:.1f}%)"
        )
