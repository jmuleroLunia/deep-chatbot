"""UpdateStep Use Case - Updates a step's completion status."""

from ....domain.planning import PlanRepository
from ..dtos.plan_request import UpdateStepRequest
from ..dtos.plan_response import PlanResponse, StepDTO


class UpdateStepUseCase:
    """
    Use case for updating a step's completion status.

    Business rules enforced:
    - Can only modify active plans
    - Auto-completes plan when all steps are done
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
        request: UpdateStepRequest
    ) -> PlanResponse:
        """
        Execute the update step use case.

        Args:
            request: Update step request

        Returns:
            Updated plan response

        Raises:
            UseCaseError: If plan not found or cannot be modified
        """
        # Get plan
        plan = await self.plan_repository.get_plan_by_id(request.plan_id)

        if not plan:
            raise ValueError(f"Plan {request.plan_id} not found")

        # Get step
        step = plan.get_step(request.step_number)

        if not step:
            raise ValueError(
                f"Step {request.step_number} not found in plan {request.plan_id}"
            )

        # Update step status
        if request.completed:
            plan.complete_step(request.step_number)
        else:
            step.mark_incomplete()

        # Persist changes
        plan = await self.plan_repository.update_plan(plan)

        # Convert to DTO
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
