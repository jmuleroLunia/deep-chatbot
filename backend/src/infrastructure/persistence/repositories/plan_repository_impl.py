"""PlanRepository implementation using SQLAlchemy."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....domain.planning import Plan, PlanRepository, PlanStatus, Step
from ..sqlalchemy import mappers
from ..sqlalchemy.models import PlanModel, StepModel


class PlanRepositoryImpl(PlanRepository):
    """
    SQLAlchemy implementation of PlanRepository.

    Implements the repository contract defined in the domain layer.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_plan(self, plan: Plan) -> Plan:
        """Create a new plan with its steps."""
        plan_model = mappers.plan_entity_to_model(plan)
        self.session.add(plan_model)
        await self.session.flush()

        # Update plan entity with generated IDs
        return mappers.plan_model_to_entity(plan_model)

    async def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """Retrieve a plan by its ID with all steps loaded."""
        result = await self.session.execute(
            select(PlanModel)
            .options(selectinload(PlanModel.steps))
            .where(PlanModel.id == plan_id)
        )
        plan_model = result.scalar_one_or_none()

        if not plan_model:
            return None

        return mappers.plan_model_to_entity(plan_model)

    async def get_active_plan_by_thread(
        self, thread_id: str
    ) -> Optional[Plan]:
        """Get the active plan for a thread."""
        result = await self.session.execute(
            select(PlanModel)
            .options(selectinload(PlanModel.steps))
            .where(
                PlanModel.thread_id == thread_id,
                PlanModel.status == str(PlanStatus.ACTIVE),
            )
            .order_by(PlanModel.created_at.desc())
        )
        plan_model = result.scalar_one_or_none()

        if not plan_model:
            return None

        return mappers.plan_model_to_entity(plan_model)

    async def get_plans_by_thread(
        self, thread_id: str, status: Optional[PlanStatus] = None
    ) -> List[Plan]:
        """Get all plans for a thread, optionally filtered by status."""
        query = (
            select(PlanModel)
            .options(selectinload(PlanModel.steps))
            .where(PlanModel.thread_id == thread_id)
        )

        if status is not None:
            query = query.where(PlanModel.status == str(status))

        query = query.order_by(PlanModel.created_at.desc())

        result = await self.session.execute(query)
        plan_models = result.scalars().all()

        return [mappers.plan_model_to_entity(model) for model in plan_models]

    async def update_plan(self, plan: Plan) -> Plan:
        """Update an existing plan and its steps."""
        # Get existing plan
        result = await self.session.execute(
            select(PlanModel)
            .options(selectinload(PlanModel.steps))
            .where(PlanModel.id == plan.id)
        )
        plan_model = result.scalar_one_or_none()

        if not plan_model:
            raise ValueError(f"Plan {plan.id} not found")

        # Update plan fields
        plan_model.title = plan.title
        plan_model.status = str(plan.status)
        plan_model.updated_at = plan.updated_at
        plan_model.completed_at = plan.completed_at

        # Update steps
        # Remove old steps
        for old_step in plan_model.steps:
            await self.session.delete(old_step)

        # Add updated steps
        plan_model.steps = [
            mappers.step_entity_to_model(step) for step in plan.steps
        ]

        await self.session.flush()

        return mappers.plan_model_to_entity(plan_model)

    async def update_step(self, step: Step) -> Step:
        """Update a single step."""
        result = await self.session.execute(
            select(StepModel).where(StepModel.id == step.id)
        )
        step_model = result.scalar_one_or_none()

        if not step_model:
            raise ValueError(f"Step {step.id} not found")

        # Update fields
        step_model.description = step.description
        step_model.completed = step.completed
        step_model.completed_at = step.completed_at

        await self.session.flush()

        return mappers.step_model_to_entity(step_model)

    async def delete_plan(self, plan_id: int) -> bool:
        """Delete a plan and all its steps."""
        result = await self.session.execute(
            select(PlanModel).where(PlanModel.id == plan_id)
        )
        plan_model = result.scalar_one_or_none()

        if not plan_model:
            return False

        await self.session.delete(plan_model)
        await self.session.flush()
        return True

    async def plan_exists(self, plan_id: int) -> bool:
        """Check if a plan exists."""
        result = await self.session.execute(
            select(PlanModel.id).where(PlanModel.id == plan_id)
        )
        return result.scalar_one_or_none() is not None

    async def has_active_plan(self, thread_id: str) -> bool:
        """Check if a thread has an active plan."""
        result = await self.session.execute(
            select(PlanModel.id).where(
                PlanModel.thread_id == thread_id,
                PlanModel.status == str(PlanStatus.ACTIVE),
            )
        )
        return result.scalar_one_or_none() is not None
