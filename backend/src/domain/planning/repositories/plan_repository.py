"""PlanRepository Protocol - Abstract interface for plan persistence."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.plan import Plan
from ..entities.step import Step
from ..value_objects.plan_status import PlanStatus


class PlanRepository(ABC):
    """
    Abstract repository interface for Plan persistence.

    Defines the contract that infrastructure must implement.
    Follows Dependency Inversion Principle.
    """

    @abstractmethod
    async def create_plan(self, plan: Plan) -> Plan:
        """
        Create a new plan with its steps.

        Args:
            plan: Plan entity to persist

        Returns:
            Plan with generated ID and step IDs

        Raises:
            RepositoryError: If creation fails
        """
        pass

    @abstractmethod
    async def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """
        Retrieve a plan by its ID with all steps loaded.

        Args:
            plan_id: Plan identifier

        Returns:
            Plan with steps if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_active_plan_by_thread(
        self, thread_id: str
    ) -> Optional[Plan]:
        """
        Get the active plan for a thread.

        Business rule: Only one active plan per thread.

        Args:
            thread_id: Thread identifier

        Returns:
            Active plan if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_plans_by_thread(
        self,
        thread_id: str,
        status: Optional[PlanStatus] = None
    ) -> List[Plan]:
        """
        Get all plans for a thread, optionally filtered by status.

        Args:
            thread_id: Thread identifier
            status: Optional status filter

        Returns:
            List of plans with their steps
        """
        pass

    @abstractmethod
    async def update_plan(self, plan: Plan) -> Plan:
        """
        Update an existing plan and its steps.

        Args:
            plan: Plan entity with updated data

        Returns:
            Updated plan

        Raises:
            RepositoryError: If plan not found or update fails
        """
        pass

    @abstractmethod
    async def update_step(self, step: Step) -> Step:
        """
        Update a single step.

        Args:
            step: Step entity with updated data

        Returns:
            Updated step

        Raises:
            RepositoryError: If step not found or update fails
        """
        pass

    @abstractmethod
    async def delete_plan(self, plan_id: int) -> bool:
        """
        Delete a plan and all its steps.

        Args:
            plan_id: Plan identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def plan_exists(self, plan_id: int) -> bool:
        """
        Check if a plan exists.

        Args:
            plan_id: Plan identifier

        Returns:
            True if plan exists
        """
        pass

    @abstractmethod
    async def has_active_plan(self, thread_id: str) -> bool:
        """
        Check if a thread has an active plan.

        Args:
            thread_id: Thread identifier

        Returns:
            True if thread has an active plan
        """
        pass
