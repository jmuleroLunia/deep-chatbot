"""PlanResponse DTO - Output data for plan operations."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class StepDTO:
    """DTO for a single step."""

    step_number: int
    description: str
    completed: bool
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "step_number": self.step_number,
            "description": self.description,
            "completed": self.completed,
            "completed_at": self.completed_at
        }


@dataclass
class PlanResponse:
    """DTO for plan output."""

    plan_id: int
    thread_id: str
    title: str
    status: str
    steps: List[StepDTO]
    completion_percentage: float
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "plan_id": self.plan_id,
            "thread_id": self.thread_id,
            "title": self.title,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "completion_percentage": self.completion_percentage,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }
