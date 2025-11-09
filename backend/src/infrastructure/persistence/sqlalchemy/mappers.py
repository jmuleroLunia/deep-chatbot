"""
Mappers between ORM models and Domain entities.

Converts between infrastructure (SQLAlchemy) and domain layers.
"""

from ....domain.conversation import Message, MessageRole, Thread, ThreadId
from ....domain.memory import Note
from ....domain.planning import Plan, PlanStatus, Step
from .models import (
    MessageModel,
    NoteModel,
    PlanModel,
    StepModel,
    ThreadModel,
)


# ===== Thread Mappers =====


def thread_model_to_entity(model: ThreadModel) -> Thread:
    """Convert ThreadModel (ORM) to Thread (domain entity)."""
    thread = Thread(
        thread_id=ThreadId.from_string(model.id),
        id=None,  # Domain Thread doesn't use database ID
        created_at=model.created_at,
        updated_at=model.updated_at,
        messages=[],  # Messages loaded separately if needed
        metadata=model.thread_metadata or {},
    )
    return thread


def thread_entity_to_model(entity: Thread) -> ThreadModel:
    """Convert Thread (domain entity) to ThreadModel (ORM)."""
    return ThreadModel(
        id=str(entity.thread_id),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        thread_metadata=entity.metadata,
    )


# ===== Message Mappers =====


def message_model_to_entity(model: MessageModel) -> Message:
    """Convert MessageModel (ORM) to Message (domain entity)."""
    return Message(
        id=model.id,
        role=MessageRole.from_string(model.role),
        content=model.content,
        thread_id=model.thread_id,
        created_at=model.created_at,
        metadata={},
    )


def message_entity_to_model(entity: Message) -> MessageModel:
    """Convert Message (domain entity) to MessageModel (ORM)."""
    model_dict = {
        "role": str(entity.role),
        "content": entity.content,
        "thread_id": entity.thread_id,
        "created_at": entity.created_at,
    }

    if entity.id is not None:
        model_dict["id"] = entity.id

    return MessageModel(**model_dict)


# ===== Plan and Step Mappers =====


def step_model_to_entity(model: StepModel) -> Step:
    """Convert StepModel (ORM) to Step (domain entity)."""
    # Handle legacy data with empty descriptions
    description = model.description if model.description and model.description.strip() else "Empty step"

    return Step(
        id=model.id,
        plan_id=model.plan_id,
        step_number=model.step_number,
        description=description,
        completed=model.completed,
        completed_at=model.completed_at,
    )


def step_entity_to_model(entity: Step) -> StepModel:
    """Convert Step (domain entity) to StepModel (ORM)."""
    model_dict = {
        "step_number": entity.step_number,
        "description": entity.description,
        "completed": entity.completed,
        "completed_at": entity.completed_at,
    }

    if entity.id is not None:
        model_dict["id"] = entity.id

    if entity.plan_id is not None:
        model_dict["plan_id"] = entity.plan_id

    return StepModel(**model_dict)


def plan_model_to_entity(model: PlanModel) -> Plan:
    """Convert PlanModel (ORM) to Plan (domain entity)."""
    # Convert steps
    steps = [step_model_to_entity(step_model) for step_model in model.steps]

    return Plan(
        id=model.id,
        thread_id=model.thread_id,
        title=model.title,
        steps=steps,
        status=PlanStatus.from_string(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
        completed_at=model.completed_at,
    )


def plan_entity_to_model(entity: Plan) -> PlanModel:
    """Convert Plan (domain entity) to PlanModel (ORM)."""
    model_dict = {
        "thread_id": entity.thread_id,
        "title": entity.title,
        "task": entity.title,  # Duplicate for legacy compatibility
        "status": str(entity.status),
        "created_at": entity.created_at,
        "updated_at": entity.updated_at,
        "completed_at": entity.completed_at,
    }

    if entity.id is not None:
        model_dict["id"] = entity.id

    plan_model = PlanModel(**model_dict)

    # Convert and attach steps
    plan_model.steps = [step_entity_to_model(step) for step in entity.steps]

    return plan_model


# ===== Note Mappers =====


def note_model_to_entity(model: NoteModel) -> Note:
    """Convert NoteModel (ORM) to Note (domain entity)."""
    return Note(
        id=model.id,
        thread_id=model.thread_id,
        title=model.title,
        content=model.content,
        tags=model.tags or [],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def note_entity_to_model(entity: Note) -> NoteModel:
    """Convert Note (domain entity) to NoteModel (ORM)."""
    model_dict = {
        "thread_id": entity.thread_id,
        "title": entity.title,
        "filename": entity.title.replace(" ", "_") + ".md",  # Generate filename from title
        "content": entity.content,
        "tags": entity.tags,
        "created_at": entity.created_at,
        "updated_at": entity.updated_at,
    }

    if entity.id is not None:
        model_dict["id"] = entity.id

    return NoteModel(**model_dict)
