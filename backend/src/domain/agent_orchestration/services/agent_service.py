"""AgentService Protocol - Abstract interface for LLM/Agent providers."""

from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Optional

from ...conversation.entities.message import Message
from ..value_objects.agent_response import AgentResponse


class AgentService(ABC):
    """
    Abstract service interface for agent/LLM providers.

    Defines the contract for interacting with AI agents (Ollama, OpenAI, etc).
    Follows Dependency Inversion Principle - domain defines the abstraction.
    """

    @abstractmethod
    async def invoke(
        self,
        messages: List[Message],
        thread_id: str,
        system_prompt: Optional[str] = None
    ) -> AgentResponse:
        """
        Invoke the agent with a list of messages.

        Args:
            messages: Conversation history
            thread_id: Thread identifier for state management
            system_prompt: Optional system prompt override

        Returns:
            Agent's response with content and/or tool calls

        Raises:
            AgentServiceError: If invocation fails
        """
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Message],
        thread_id: str,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream agent responses token by token.

        Args:
            messages: Conversation history
            thread_id: Thread identifier for state management
            system_prompt: Optional system prompt override

        Yields:
            Response tokens as they're generated

        Raises:
            AgentServiceError: If streaming fails
        """
        pass

    @abstractmethod
    async def invoke_with_tools(
        self,
        messages: List[Message],
        thread_id: str,
        available_tools: List[str],
        system_prompt: Optional[str] = None
    ) -> AgentResponse:
        """
        Invoke agent with tool-calling capabilities.

        Args:
            messages: Conversation history
            thread_id: Thread identifier
            available_tools: List of tool names the agent can use
            system_prompt: Optional system prompt override

        Returns:
            Agent's response, potentially with tool calls

        Raises:
            AgentServiceError: If invocation fails
        """
        pass

    @abstractmethod
    async def get_checkpoint(self, thread_id: str) -> Optional[dict]:
        """
        Get the current checkpoint/state for a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            Checkpoint data or None if no checkpoint exists
        """
        pass

    @abstractmethod
    async def save_checkpoint(
        self,
        thread_id: str,
        checkpoint_data: dict
    ) -> None:
        """
        Save a checkpoint/state for a thread.

        Args:
            thread_id: Thread identifier
            checkpoint_data: Data to persist

        Raises:
            AgentServiceError: If save fails
        """
        pass

    @abstractmethod
    async def clear_checkpoint(self, thread_id: str) -> bool:
        """
        Clear the checkpoint/state for a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            True if checkpoint was cleared, False if none existed
        """
        pass
