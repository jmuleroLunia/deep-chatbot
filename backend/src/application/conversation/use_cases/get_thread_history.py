"""GetThreadHistory Use Case - Retrieves conversation history."""

from typing import Optional

from ....domain.conversation import ThreadId, ThreadRepository
from ..dtos.thread_history_response import MessageDTO, ThreadHistoryResponse


class GetThreadHistoryUseCase:
    """
    Use case for retrieving conversation history for a thread.

    Returns all messages in chronological order.
    """

    def __init__(self, thread_repository: ThreadRepository):
        """
        Initialize use case with dependencies.

        Args:
            thread_repository: Repository for thread persistence
        """
        self.thread_repository = thread_repository

    async def execute(
        self,
        thread_id: str,
        limit: Optional[int] = None
    ) -> ThreadHistoryResponse:
        """
        Execute the get thread history use case.

        Args:
            thread_id: Thread identifier
            limit: Optional limit on number of messages

        Returns:
            Thread history response with messages

        Raises:
            UseCaseError: If thread not found
        """
        thread_id_vo = ThreadId.from_string(thread_id)

        # Get messages
        messages = await self.thread_repository.get_messages_by_thread(
            thread_id_vo,
            limit=limit
        )

        # Convert to DTOs
        message_dtos = [
            MessageDTO(
                role=str(msg.role),
                content=msg.content,
                timestamp=msg.created_at.isoformat(),
                message_id=msg.id or 0
            )
            for msg in messages
        ]

        return ThreadHistoryResponse(
            thread_id=thread_id,
            messages=message_dtos,
            total_messages=len(message_dtos)
        )
