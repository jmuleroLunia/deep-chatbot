"""CreatePlan Use Case - Creates a new plan with steps."""

from ....domain.planning import Plan, PlanRepository, Step
from ..dtos.plan_request import CreatePlanRequest
from ..dtos.plan_response import PlanResponse, StepDTO


class CreatePlanUseCase:
    """
    Use case for creating a new plan.

    Business rules:
    - Thread can only have one active plan at a time
    - Steps are automatically numbered sequentially
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
        request: CreatePlanRequest
    ) -> PlanResponse:
        """
        Execute the create plan use case.

        Args:
            request: Create plan request with title and steps

        Returns:
            Plan response with created plan

        Raises:
            UseCaseError: If thread already has an active plan
        """
        # Check if thread already has an active plan
        has_active = await self.plan_repository.has_active_plan(
            request.thread_id
        )

        if has_active:
            raise ValueError(
                f"Thread '{request.thread_id}' already has an active plan. "
                "Complete or cancel it before creating a new one."
            )

        # Create plan with steps
        steps = [
            Step(description=desc, step_number=idx + 1)
            for idx, desc in enumerate(request.steps)
        ]

        plan = Plan(
            thread_id=request.thread_id,
            title=request.title,
            steps=steps
        )

        # Persist
        plan = await self.plan_repository.create_plan(plan)

        # Convert to DTO
        return self._plan_to_response(plan)

    def _plan_to_response(self, plan: Plan) -> PlanResponse:
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
