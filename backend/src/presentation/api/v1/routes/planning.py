"""Planning API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from .....application.planning import (
    CompletePlanUseCase,
    CreatePlanRequest,
    CreatePlanUseCase,
    GetActivePlanUseCase,
    UpdateStepRequest,
    UpdateStepUseCase,
)
from ..dependencies import (
    get_complete_plan_use_case,
    get_create_plan_use_case,
    get_get_active_plan_use_case,
    get_update_step_use_case,
    get_plan_repository,
)

router = APIRouter(prefix="/plans", tags=["planning"])


# ===== Request Models =====


class CreatePlanRequestModel(BaseModel):
    """Request model for creating a plan."""

    thread_id: str
    title: str
    steps: list[str]


class UpdateStepRequestModel(BaseModel):
    """Request model for updating a step."""

    step_number: int
    completed: bool


# ===== Endpoints =====


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_plan(
    request: CreatePlanRequestModel,
    use_case: CreatePlanUseCase = Depends(get_create_plan_use_case),
):
    """
    Create a new plan with steps.

    Args:
        request: Plan creation request
        use_case: Injected CreatePlanUseCase

    Returns:
        Created plan with all details
    """
    try:
        plan_request = CreatePlanRequest(
            thread_id=request.thread_id,
            title=request.title,
            steps=request.steps,
        )

        response = await use_case.execute(plan_request)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create plan: {str(e)}",
        )


@router.put("/{plan_id}/steps", status_code=status.HTTP_200_OK)
async def update_step(
    plan_id: int,
    request: UpdateStepRequestModel,
    use_case: UpdateStepUseCase = Depends(get_update_step_use_case),
):
    """
    Update a step's completion status.

    Args:
        plan_id: Plan identifier
        request: Step update request
        use_case: Injected UpdateStepUseCase

    Returns:
        Updated plan with new step status
    """
    try:
        update_request = UpdateStepRequest(
            plan_id=plan_id,
            step_number=request.step_number,
            completed=request.completed,
        )

        response = await use_case.execute(update_request)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update step: {str(e)}",
        )


@router.get("/active/{thread_id}", status_code=status.HTTP_200_OK)
async def get_active_plan(
    thread_id: str,
    use_case: GetActivePlanUseCase = Depends(get_get_active_plan_use_case),
):
    """
    Get the active plan for a thread.

    Args:
        thread_id: Thread identifier
        use_case: Injected GetActivePlanUseCase

    Returns:
        Active plan if exists, null otherwise
    """
    try:
        response = await use_case.execute(thread_id)

        if response is None:
            return {"message": "No active plan found", "plan": None}

        return response.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active plan: {str(e)}",
        )


@router.post("/{plan_id}/complete", status_code=status.HTTP_200_OK)
async def complete_plan(
    plan_id: int,
    use_case: CompletePlanUseCase = Depends(get_complete_plan_use_case),
):
    """
    Mark a plan as completed.

    Args:
        plan_id: Plan identifier
        use_case: Injected CompletePlanUseCase

    Returns:
        Completed plan
    """
    try:
        response = await use_case.execute(plan_id)

        return response.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete plan: {str(e)}",
        )


@router.delete("/{plan_id}", status_code=status.HTTP_200_OK)
async def delete_plan(
    plan_id: int,
    plan_repository=Depends(get_plan_repository),
):
    """
    Delete a plan.

    Args:
        plan_id: Plan identifier
        plan_repository: Injected plan repository

    Returns:
        Deletion confirmation
    """
    try:
        success = await plan_repository.delete_plan(plan_id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        return {"message": "Plan deleted successfully", "plan_id": plan_id}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete plan: {str(e)}",
        )
