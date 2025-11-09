"""SendMessage Use Case - Handles sending a message and getting AI response."""

from typing import Optional

from ....domain.agent_orchestration import AgentService
from ....domain.conversation import (
    Message,
    MessageRole,
    ThreadId,
    ThreadRepository,
)
from ..dtos.chat_request import ChatRequest
from ..dtos.chat_response import ChatResponse


class SendMessageUseCase:
    """
    Use case for sending a message and receiving an AI response.

    Orchestrates:
    1. Creating/retrieving thread
    2. Saving user message
    3. Getting AI response
    4. Saving AI response
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
    ) -> ChatResponse:
        """
        Execute the send message use case.

        Args:
            request: Chat request with message and thread ID

        Returns:
            Chat response with AI reply

        Raises:
            UseCaseError: If execution fails
        """
        thread_id = ThreadId.from_string(request.thread_id)

        # Ensure thread exists
        thread = await self.thread_repository.get_thread_by_id(thread_id)
        if not thread:
            # Create new thread if it doesn't exist
            from ....domain.conversation import Thread
            thread = Thread(thread_id=thread_id)
            thread = await self.thread_repository.create_thread(thread)

        # Save user message
        user_message = Message(
            role=MessageRole.HUMAN,
            content=request.message,
            thread_id=str(thread_id)
        )
        user_message = await self.thread_repository.save_message(user_message)

        # Get conversation history
        messages = await self.thread_repository.get_messages_by_thread(
            thread_id
        )

        # Get AI response
        agent_response = await self.agent_service.invoke(
            messages=messages,
            thread_id=str(thread_id),
            system_prompt=request.system_prompt
        )

        # Save AI response
        ai_message = Message(
            role=MessageRole.AI,
            content=agent_response.content,
            thread_id=str(thread_id)
        )
        ai_message = await self.thread_repository.save_message(ai_message)

        # Convert tool calls to dict format
        tool_calls_dict = [
            {
                "tool_name": tc.tool_name,
                "arguments": tc.arguments,
                "call_id": tc.call_id
            }
            for tc in agent_response.tool_calls
        ]

        return ChatResponse(
            response=agent_response.content,
            thread_id=str(thread_id),
            message_id=ai_message.id,
            tool_calls=tool_calls_dict,
            metadata=agent_response.metadata
        )
