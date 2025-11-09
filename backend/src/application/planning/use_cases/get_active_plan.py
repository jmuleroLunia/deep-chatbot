"""GetActivePlan Use Case - Retrieves the active plan for a thread."""

from typing import Optional

from ....domain.planning import PlanRepository
from ..dtos.plan_response import PlanResponse, StepDTO


class GetActivePlanUseCase:
    """
    Use case for getting the active plan for a thread.

    Returns None if no active plan exists.
    """

    def __init__(self, plan_repository: PlanRepository):
        """
        Initialize use case with dependencies.

        Args:
            plan_repository: Repository for plan persistence
        """
        self.plan_repository = plan_repository

    async def execute(
        self,
        thread_id: str
    ) -> Optional[PlanResponse]:
        """
        Execute the get active plan use case.

        Args:
            thread_id: Thread identifier

        Returns:
            Plan response if active plan exists, None otherwise
        """
        plan = await self.plan_repository.get_active_plan_by_thread(
            thread_id
        )

        if not plan:
            return None

        return self._plan_to_response(plan)

    def _plan_to_response(self, plan) -> PlanResponse:
        """Convert domain Plan to PlanResponse DTO."""
        step_dtos = [
            StepDTO(
                step_number=step.step_number,
                description=step.description,
                completed=step.completed,
                completed_at=(
                    step.completed_at.isoformat()
                    if step.completed_at
                    else None
                )
            )
            for step in plan.steps
        ]

        return PlanResponse(
            plan_id=plan.id or 0,
            thread_id=plan.thread_id,
            title=plan.title,
            status=str(plan.status),
            steps=step_dtos,
            completion_percentage=plan.get_completion_percentage(),
            created_at=plan.created_at.isoformat(),
            updated_at=plan.updated_at.isoformat(),
            completed_at=(
                plan.completed_at.isoformat()
                if plan.completed_at
                else None
            )
        )
