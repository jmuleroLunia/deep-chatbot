"""StreamChat Use Case - Handles streaming chat responses."""

from typing import AsyncGenerator, Optional

from ....domain.agent_orchestration import AgentService
from ....domain.conversation import (
    Message,
    MessageRole,
    ThreadId,
    ThreadRepository,
)
from ..dtos.chat_request import ChatRequest


class StreamChatUseCase:
    """
    Use case for streaming chat responses token by token.

    Similar to SendMessage but streams the AI response.
    """

    def __init__(
        self,
        thread_repository: ThreadRepository,
        agent_service: AgentService
    ):
        """
        Initialize use case with dependencies.

        Args:
            thread_repository: Repository for thread persistence
            agent_service: Service for AI agent interaction
        """
        self.thread_repository = thread_repository
        self.agent_service = agent_service

    async def execute(
        self,
        request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """
        Execute the stream chat use case.

        Args:
            request: Chat request with message and thread ID

        Yields:
            Response tokens as they're generated

        Raises:
            UseCaseError: If execution fails
        """
        thread_id = ThreadId.from_string(request.thread_id)

        # Ensure thread exists
        thread = await self.thread_repository.get_thread_by_id(thread_id)
        if not thread:
            # Create new thread
            from ....domain.conversation import Thread
            thread = Thread(thread_id=thread_id)
            thread = await self.thread_repository.create_thread(thread)

        # Save user message
        user_message = Message(
            role=MessageRole.HUMAN,
            content=request.message,
            thread_id=str(thread_id)
        )
        await self.thread_repository.save_message(user_message)

        # Get conversation history
        messages = await self.thread_repository.get_messages_by_thread(
            thread_id
        )

        # Collect the full response for saving later
        full_response = []

        # Stream AI response
        async for token in self.agent_service.stream(
            messages=messages,
            thread_id=str(thread_id),
            system_prompt=request.system_prompt
        ):
            full_response.append(token)
            yield token

        # Save complete AI response
        ai_message = Message(
            role=MessageRole.AI,
            content="".join(full_response),
            thread_id=str(thread_id)
        )
        await self.thread_repository.save_message(ai_message)
