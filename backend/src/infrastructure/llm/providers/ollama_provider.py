"""Ollama provider implementation for AgentService."""

from typing import AsyncGenerator, List, Optional

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ....domain.agent_orchestration import AgentResponse, AgentService, ToolCall
from ....domain.conversation import Message, MessageRole


class OllamaProvider(AgentService):
    """
    Ollama implementation of AgentService.

    Wraps LangChain's ChatOllama and LangGraph for agent orchestration.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gpt-oss:120b-cloud",
    ):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url
        self.model = model
        self.checkpoints = MemorySaver()

        # Initialize ChatOllama
        self.llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0.7,
        )

    def _convert_domain_messages_to_langchain(
        self, messages: List[Message]
    ) -> list:
        """Convert domain Message entities to LangChain messages."""
        lc_messages = []

        for msg in messages:
            if msg.role == MessageRole.HUMAN:
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.AI:
                lc_messages.append(AIMessage(content=msg.content))
            elif msg.role == MessageRole.SYSTEM:
                lc_messages.append(SystemMessage(content=msg.content))
            # Note: TOOL role would need special handling if we add tool support

        return lc_messages

    async def invoke(
        self,
        messages: List[Message],
        thread_id: str,
        system_prompt: Optional[str] = None,
    ) -> AgentResponse:
        """Invoke the agent with a list of messages."""
        # Convert domain messages to LangChain format
        lc_messages = self._convert_domain_messages_to_langchain(messages)

        # Add system prompt if provided
        if system_prompt:
            lc_messages.insert(0, SystemMessage(content=system_prompt))

        # Create a simple graph that just invokes the LLM
        workflow = StateGraph(MessagesState)

        async def call_model(state: MessagesState):
            """Call the LLM."""
            response = await self.llm.ainvoke(state["messages"])
            return {"messages": [response]}

        workflow.add_node("agent", call_model)
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)

        # Compile with checkpointing
        app = workflow.compile(checkpointer=self.checkpoints)

        # Invoke with thread-based state
        config = {"configurable": {"thread_id": thread_id}}
        result = await app.ainvoke(
            {"messages": lc_messages},
            config=config
        )

        # Extract response
        ai_message = result["messages"][-1]
        content = ai_message.content if hasattr(ai_message, "content") else str(ai_message)

        # TODO: Extract tool calls if present
        tool_calls = []

        return AgentResponse(
            content=content,
            tool_calls=tool_calls,
            metadata={}
        )

    async def stream(
        self,
        messages: List[Message],
        thread_id: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream agent responses token by token."""
        # Convert domain messages to LangChain format
        lc_messages = self._convert_domain_messages_to_langchain(messages)

        # Add system prompt if provided
        if system_prompt:
            lc_messages.insert(0, SystemMessage(content=system_prompt))

        # Stream from LLM
        async for chunk in self.llm.astream(lc_messages):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    async def invoke_with_tools(
        self,
        messages: List[Message],
        thread_id: str,
        available_tools: List[str],
        system_prompt: Optional[str] = None,
    ) -> AgentResponse:
        """
        Invoke agent with tool-calling capabilities.

        TODO: Implement tool binding and execution.
        For now, falls back to regular invoke.
        """
        # This will be implemented when we adapt the tools
        return await self.invoke(messages, thread_id, system_prompt)

    async def get_checkpoint(self, thread_id: str) -> Optional[dict]:
        """Get the current checkpoint/state for a thread."""
        config = {"configurable": {"thread_id": thread_id}}

        # Try to get checkpoint from MemorySaver
        try:
            checkpoint = self.checkpoints.get(config)
            if checkpoint:
                return checkpoint.dict() if hasattr(checkpoint, "dict") else dict(checkpoint)
        except Exception:
            pass

        return None

    async def save_checkpoint(
        self, thread_id: str, checkpoint_data: dict
    ) -> None:
        """
        Save a checkpoint/state for a thread.

        Note: MemorySaver handles checkpoints automatically,
        so this is primarily for manual checkpoint management.
        """
        # MemorySaver handles checkpoints automatically during graph execution
        # This method is here for interface compliance
        pass

    async def clear_checkpoint(self, thread_id: str) -> bool:
        """
        Clear the checkpoint/state for a thread.

        Note: MemorySaver doesn't provide a direct clear method,
        so we'll need to work around this.
        """
        # MemorySaver doesn't have a clear method
        # We could recreate the checkpoints dict, but that would affect all threads
        # For now, return False to indicate it's not supported
        return False
