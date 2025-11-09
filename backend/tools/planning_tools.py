"""Planning tools for deep agent - enables complex task management."""
from langchain_core.tools import tool
from typing import List
import json
from pathlib import Path


# Planning state - stored in workspace
WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)
PLAN_FILE = WORKSPACE_DIR / "current_plan.json"


@tool
def create_plan(task: str, steps: List[str]) -> str:
    """
    Create a detailed plan for completing a complex task.

    Args:
        task: The main task to accomplish
        steps: List of steps needed to complete the task

    Returns:
        Confirmation that the plan was created
    """
    plan = {
        "task": task,
        "steps": [{"step": s, "completed": False} for s in steps],
        "status": "in_progress"
    }

    PLAN_FILE.write_text(json.dumps(plan, indent=2))
    return f"Plan created with {len(steps)} steps for task: {task}"


@tool
def update_plan_step(step_number: int, completed: bool = True) -> str:
    """
    Mark a step in the current plan as completed or update its status.

    Args:
        step_number: The step number (1-indexed)
        completed: Whether the step is completed

    Returns:
        Confirmation of the update
    """
    if not PLAN_FILE.exists():
        return "No active plan found. Create a plan first."

    plan = json.loads(PLAN_FILE.read_text())

    if step_number < 1 or step_number > len(plan["steps"]):
        return f"Invalid step number. Plan has {len(plan['steps'])} steps."

    plan["steps"][step_number - 1]["completed"] = completed

    # Check if all steps are completed
    if all(s["completed"] for s in plan["steps"]):
        plan["status"] = "completed"

    PLAN_FILE.write_text(json.dumps(plan, indent=2))

    return f"Step {step_number} marked as {'completed' if completed else 'incomplete'}"


@tool
def view_plan() -> str:
    """
    View the current plan and its progress.

    Returns:
        The current plan with completion status
    """
    if not PLAN_FILE.exists():
        return "No active plan found."

    plan = json.loads(PLAN_FILE.read_text())

    output = [f"Task: {plan['task']}", f"Status: {plan['status']}", "", "Steps:"]

    for i, step in enumerate(plan["steps"], 1):
        status = "✓" if step["completed"] else "○"
        output.append(f"{status} {i}. {step['step']}")

    return "\n".join(output)


@tool
def add_plan_step(step: str, position: int = None) -> str:
    """
    Add a new step to the current plan.

    Args:
        step: The step description
        position: Optional position to insert (1-indexed), defaults to end

    Returns:
        Confirmation of the addition
    """
    if not PLAN_FILE.exists():
        return "No active plan found. Create a plan first."

    plan = json.loads(PLAN_FILE.read_text())

    new_step = {"step": step, "completed": False}

    if position is None:
        plan["steps"].append(new_step)
        pos_msg = "at the end"
    else:
        plan["steps"].insert(position - 1, new_step)
        pos_msg = f"at position {position}"

    PLAN_FILE.write_text(json.dumps(plan, indent=2))

    return f"Added step {pos_msg}: {step}"