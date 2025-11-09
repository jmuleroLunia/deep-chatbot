"""CompletePlan Use Case - Marks a plan as completed."""

from ....domain.planning import PlanRepository
from ..dtos.plan_response import PlanResponse, StepDTO


class CompletePlanUseCase:
    """
    Use case for manually completing a plan.

    Business rule: All steps must be completed before plan can be marked complete.
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
        plan_id: int
    ) -> PlanResponse:
        """
        Execute the complete plan use case.

        Args:
            plan_id: Plan identifier

        Returns:
            Completed plan response

        Raises:
            UseCaseError: If plan not found or cannot be completed
        """
        # Get plan
        plan = await self.plan_repository.get_plan_by_id(plan_id)

        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        # Mark as completed (enforces business rules)
        plan.mark_completed()

        # Persist
        plan = await self.plan_repository.update_plan(plan)

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
