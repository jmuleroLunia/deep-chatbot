"""ThreadRepository implementation using SQLAlchemy."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....domain.conversation import Message, Thread, ThreadId, ThreadRepository
from ..sqlalchemy import mappers
from ..sqlalchemy.models import MessageModel, ThreadModel


class ThreadRepositoryImpl(ThreadRepository):
    """
    SQLAlchemy implementation of ThreadRepository.

    Implements the repository contract defined in the domain layer.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_thread(self, thread: Thread) -> Thread:
        """Create a new thread."""
        thread_model = mappers.thread_entity_to_model(thread)
        self.session.add(thread_model)
        await self.session.flush()  # Get the ID without committing
        return mappers.thread_model_to_entity(thread_model)

    async def get_thread_by_id(self, thread_id: ThreadId) -> Optional[Thread]:
        """Retrieve a thread by its ID (without messages)."""
        result = await self.session.execute(
            select(ThreadModel).where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if not thread_model:
            return None

        return mappers.thread_model_to_entity(thread_model)

    async def get_thread_with_messages(
        self, thread_id: ThreadId
    ) -> Optional[Thread]:
        """Retrieve a thread with all its messages loaded."""
        result = await self.session.execute(
            select(ThreadModel)
            .options(selectinload(ThreadModel.messages))
            .where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if not thread_model:
            return None

        # Convert thread
        thread = mappers.thread_model_to_entity(thread_model)

        # Convert and attach messages
        thread.messages = [
            mappers.message_model_to_entity(msg_model)
            for msg_model in thread_model.messages
        ]

        return thread

    async def save_message(self, message: Message) -> Message:
        """Save a message to a thread."""
        # Verify thread exists
        if not await self.thread_exists(ThreadId.from_string(message.thread_id)):
            raise ValueError(f"Thread '{message.thread_id}' does not exist")

        message_model = mappers.message_entity_to_model(message)
        self.session.add(message_model)
        await self.session.flush()

        return mappers.message_model_to_entity(message_model)

    async def get_messages_by_thread(
        self, thread_id: ThreadId, limit: Optional[int] = None
    ) -> List[Message]:
        """Retrieve all messages for a thread."""
        query = (
            select(MessageModel)
            .where(MessageModel.thread_id == str(thread_id))
            .order_by(MessageModel.created_at)
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        message_models = result.scalars().all()

        return [
            mappers.message_model_to_entity(model) for model in message_models
        ]

    async def delete_thread(self, thread_id: ThreadId) -> bool:
        """Delete a thread and all its messages."""
        result = await self.session.execute(
            select(ThreadModel).where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if not thread_model:
            return False

        await self.session.delete(thread_model)
        await self.session.flush()
        return True

    async def thread_exists(self, thread_id: ThreadId) -> bool:
        """Check if a thread exists."""
        result = await self.session.execute(
            select(ThreadModel.id).where(ThreadModel.id == str(thread_id))
        )
        return result.scalar_one_or_none() is not None

    async def update_thread_metadata(
        self, thread_id: ThreadId, metadata: dict
    ) -> bool:
        """Update thread metadata."""
        result = await self.session.execute(
            select(ThreadModel).where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if not thread_model:
            return False

        thread_model.metadata = metadata
        await self.session.flush()
        return True

    async def list_all_threads(self) -> List[Thread]:
        """List all threads."""
        result = await self.session.execute(
            select(ThreadModel).order_by(ThreadModel.created_at.desc())
        )
        thread_models = result.scalars().all()

        return [
            mappers.thread_model_to_entity(model) for model in thread_models
        ]
