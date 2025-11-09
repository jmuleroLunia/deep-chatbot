"""Planning tools for deep agent - enables per-thread complex task management."""
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select
from database import SessionLocal
from models import Plan, Thread


def _get_thread_id_from_config(config: Optional[RunnableConfig] = None) -> str:
    """
    Extract thread_id from the RunnableConfig.

    Args:
        config: The RunnableConfig object passed by LangGraph

    Returns:
        The thread_id string, defaults to "default" if not found
    """
    if config and isinstance(config, dict):
        configurable = config.get("configurable", {})
        return configurable.get("thread_id", "default")
    return "default"


@tool
def create_plan(task: str, steps: List[str], config: Optional[RunnableConfig] = None) -> str:
    """
    Create a detailed plan for completing a complex task. Each thread has its own independent plans.

    Args:
        task: The main task to accomplish
        steps: List of steps needed to complete the task
        config: Configuration object containing thread_id (injected by LangGraph)

    Returns:
        Confirmation that the plan was created
    """
    thread_id = _get_thread_id_from_config(config)

    with SessionLocal() as db:
        # Check if thread exists
        thread = db.execute(select(Thread).where(Thread.id == thread_id)).scalar_one_or_none()
        if not thread:
            return f"Error: Thread '{thread_id}' does not exist. Cannot create plan."

        # Check if an active plan already exists for this thread
        existing_plan = db.execute(
            select(Plan).where(
                Plan.thread_id == thread_id,
                Plan.status == "active"
            )
        ).scalar_one_or_none()

        if existing_plan:
            return f"An active plan already exists for this thread. Complete or cancel it first, or use add_plan_step to extend it."

        # Create new plan
        plan = Plan(
            thread_id=thread_id,
            task=task,
            steps=[{"step": s, "completed": False} for s in steps],
            status="active"
        )

        db.add(plan)
        db.commit()

    return f"Plan created with {len(steps)} steps for task: {task}"


@tool
def update_plan_step(step_number: int, completed: bool = True, config: Optional[RunnableConfig] = None) -> str:
    """
    Mark a step in the current plan as completed or update its status.

    Args:
        step_number: The step number (1-indexed)
        completed: Whether the step is completed
        config: Configuration object containing thread_id (injected by LangGraph)

    Returns:
        Confirmation of the update
    """
    thread_id = _get_thread_id_from_config(config)

    with SessionLocal() as db:
        # Get active plan for this thread
        plan = db.execute(
            select(Plan).where(
                Plan.thread_id == thread_id,
                Plan.status == "active"
            )
        ).scalar_one_or_none()

        if not plan:
            return "No active plan found for this thread. Create a plan first."

        if step_number < 1 or step_number > len(plan.steps):
            return f"Invalid step number. Plan has {len(plan.steps)} steps."

        # Update the step
        steps = plan.steps.copy()
        steps[step_number - 1]["completed"] = completed
        plan.steps = steps

        # Check if all steps are completed
        if all(s["completed"] for s in steps):
            plan.status = "completed"

        plan.updated_at = datetime.now(timezone.utc)
        db.commit()

    return f"Step {step_number} marked as {'completed' if completed else 'incomplete'}"


@tool
def view_plan(config: Optional[RunnableConfig] = None) -> str:
    """
    View the current plan and its progress for the current thread.

    Args:
        config: Configuration object containing thread_id (injected by LangGraph)

    Returns:
        The current plan with completion status
    """
    thread_id = _get_thread_id_from_config(config)

    with SessionLocal() as db:
        # Get active plan for this thread
        plan = db.execute(
            select(Plan).where(
                Plan.thread_id == thread_id,
                Plan.status == "active"
            )
        ).scalar_one_or_none()

        if not plan:
            return "No active plan found for this thread."

        output = [f"Task: {plan.task}", f"Status: {plan.status}", "", "Steps:"]

        for i, step in enumerate(plan.steps, 1):
            status = "✓" if step["completed"] else "○"
            output.append(f"{status} {i}. {step['step']}")

        return "\n".join(output)


@tool
def add_plan_step(step: str, position: Optional[int] = None, config: Optional[RunnableConfig] = None) -> str:
    """
    Add a new step to the current plan.

    Args:
        step: The step description
        position: Optional position to insert (1-indexed), defaults to end
        config: Configuration object containing thread_id (injected by LangGraph)

    Returns:
        Confirmation of the addition
    """
    thread_id = _get_thread_id_from_config(config)

    with SessionLocal() as db:
        # Get active plan for this thread
        plan = db.execute(
            select(Plan).where(
                Plan.thread_id == thread_id,
                Plan.status == "active"
            )
        ).scalar_one_or_none()

        if not plan:
            return "No active plan found for this thread. Create a plan first."

        new_step = {"step": step, "completed": False}
        steps = plan.steps.copy()

        if position is None:
            steps.append(new_step)
            pos_msg = "at the end"
        else:
            steps.insert(position - 1, new_step)
            pos_msg = f"at position {position}"

        plan.steps = steps
        plan.updated_at = datetime.now(timezone.utc)
        db.commit()

    return f"Added step {pos_msg}: {step}"
