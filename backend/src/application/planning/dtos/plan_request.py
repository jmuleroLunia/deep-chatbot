"""PlanRequest DTO - Input data for plan operations."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CreatePlanRequest:
    """DTO for creating a new plan."""

    thread_id: str
    title: str
    steps: List[str]

    def __post_init__(self):
        """Validate create plan request."""
        if not self.thread_id or not self.thread_id.strip():
            raise ValueError("Thread ID cannot be empty")

        if not self.title or not self.title.strip():
            raise ValueError("Plan title cannot be empty")

        if not self.steps:
            raise ValueError("Plan must have at least one step")

        for idx, step in enumerate(self.steps):
            if not step or not step.strip():
                raise ValueError(f"Step {idx + 1} cannot be empty")


@dataclass(frozen=True)
class UpdateStepRequest:
    """DTO for updating a step status."""

    plan_id: int
    step_number: int
    completed: bool

    def __post_init__(self):
        """Validate update step request."""
        if self.plan_id < 1:
            raise ValueError(f"Invalid plan ID: {self.plan_id}")

        if self.step_number < 1:
            raise ValueError(f"Invalid step number: {self.step_number}")
