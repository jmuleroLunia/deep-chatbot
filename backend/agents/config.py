"""Configuration for the multi-agent system."""
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState, add_messages


class AgentState(MessagesState):
    """Extended state for multi-agent system."""

    # Track which agent is currently active
    current_agent: str = "supervisor"

    # Track conversation context
    context: dict = {}

    # Track completed tasks
    completed_tasks: list[str] = []


# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # You can change this to any model you have installed

# Agent names
SUPERVISOR_NAME = "supervisor"
RESEARCH_AGENT_NAME = "research_agent"
CONVERSATION_AGENT_NAME = "conversation_agent"
ANALYSIS_AGENT_NAME = "analysis_agent"