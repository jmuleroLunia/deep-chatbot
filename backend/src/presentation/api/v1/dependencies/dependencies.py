"""
Dependency injection for FastAPI.

Provides factory functions for use cases and repositories.
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .....application.conversation import (
    GetThreadHistoryUseCase,
    SendMessageUseCase,
    StreamChatUseCase,
)
from .....application.memory import (
    RetrieveNotesUseCase,
    SaveNoteUseCase,
    UpdateNoteUseCase,
)
from .....application.planning import (
    CompletePlanUseCase,
    CreatePlanUseCase,
    GetActivePlanUseCase,
    UpdateStepUseCase,
)
from .....domain.agent_orchestration import AgentService
from .....domain.conversation import ThreadRepository
from .....domain.memory import NoteRepository
from .....domain.planning import PlanRepository
from .....infrastructure.llm import OllamaProvider
from .....infrastructure.persistence.repositories import (
    NoteRepositoryImpl,
    PlanRepositoryImpl,
    ThreadRepositoryImpl,
)
from .....infrastructure.persistence.sqlalchemy.base import get_async_session


# ===== Database Session =====


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.

    Yields:
        AsyncSession for database operations
    """
    async for session in get_async_session():
        yield session


# ===== Repository Dependencies =====


def get_thread_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ThreadRepository:
    """Get ThreadRepository implementation."""
    return ThreadRepositoryImpl(session)


def get_plan_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PlanRepository:
    """Get PlanRepository implementation."""
    return PlanRepositoryImpl(session)


def get_note_repository(
    session: AsyncSession = Depends(get_db_session),
) -> NoteRepository:
    """Get NoteRepository implementation."""
    return NoteRepositoryImpl(session)


# ===== Agent Service Dependency =====


_agent_service_instance: AgentService | None = None


def get_agent_service() -> AgentService:
    """
    Get AgentService implementation (singleton).

    Returns:
        OllamaProvider instance
    """
    global _agent_service_instance

    if _agent_service_instance is None:
        # TODO: Load from config/environment
        _agent_service_instance = OllamaProvider(
            base_url="http://localhost:11434",
            model="gpt-oss:120b-cloud",
        )

    return _agent_service_instance


# ===== Conversation Use Case Dependencies =====


def get_send_message_use_case(
    thread_repository: ThreadRepository = Depends(get_thread_repository),
    agent_service: AgentService = Depends(get_agent_service),
) -> SendMessageUseCase:
    """Get SendMessageUseCase instance."""
    return SendMessageUseCase(thread_repository, agent_service)


def get_get_thread_history_use_case(
    thread_repository: ThreadRepository = Depends(get_thread_repository),
) -> GetThreadHistoryUseCase:
    """Get GetThreadHistoryUseCase instance."""
    return GetThreadHistoryUseCase(thread_repository)


def get_stream_chat_use_case(
    thread_repository: ThreadRepository = Depends(get_thread_repository),
    agent_service: AgentService = Depends(get_agent_service),
) -> StreamChatUseCase:
    """Get StreamChatUseCase instance."""
    return StreamChatUseCase(thread_repository, agent_service)


# ===== Planning Use Case Dependencies =====


def get_create_plan_use_case(
    plan_repository: PlanRepository = Depends(get_plan_repository),
) -> CreatePlanUseCase:
    """Get CreatePlanUseCase instance."""
    return CreatePlanUseCase(plan_repository)


def get_update_step_use_case(
    plan_repository: PlanRepository = Depends(get_plan_repository),
) -> UpdateStepUseCase:
    """Get UpdateStepUseCase instance."""
    return UpdateStepUseCase(plan_repository)


def get_get_active_plan_use_case(
    plan_repository: PlanRepository = Depends(get_plan_repository),
) -> GetActivePlanUseCase:
    """Get GetActivePlanUseCase instance."""
    return GetActivePlanUseCase(plan_repository)


def get_complete_plan_use_case(
    plan_repository: PlanRepository = Depends(get_plan_repository),
) -> CompletePlanUseCase:
    """Get CompletePlanUseCase instance."""
    return CompletePlanUseCase(plan_repository)


# ===== Memory Use Case Dependencies =====


def get_save_note_use_case(
    note_repository: NoteRepository = Depends(get_note_repository),
) -> SaveNoteUseCase:
    """Get SaveNoteUseCase instance."""
    return SaveNoteUseCase(note_repository)


def get_retrieve_notes_use_case(
    note_repository: NoteRepository = Depends(get_note_repository),
) -> RetrieveNotesUseCase:
    """Get RetrieveNotesUseCase instance."""
    return RetrieveNotesUseCase(note_repository)


def get_update_note_use_case(
    note_repository: NoteRepository = Depends(get_note_repository),
) -> UpdateNoteUseCase:
    """Get UpdateNoteUseCase instance."""
    return UpdateNoteUseCase(note_repository)
