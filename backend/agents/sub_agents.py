"""Sub-agents for specialized tasks - Can be invoked by the deep agent."""
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from agents.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from tools.custom_tools import calculate, analyze_sentiment, search_knowledge_base


def get_ollama_model(temperature: float = 0.7):
    """Get configured Ollama model."""
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
    )


def create_research_agent():
    """
    Create a research specialist sub-agent.

    This agent is optimized for information retrieval and research tasks.
    """
    system_prompt = """You are a Research Specialist.

Your role:
- Search for accurate information in the knowledge base
- Provide well-researched, factual answers
- Cite sources when available
- Be thorough and precise

When you complete your task, provide a clear summary of your findings."""

    return create_react_agent(
        get_ollama_model(temperature=0.3),
        tools=[search_knowledge_base],
        prompt=system_prompt,
    )


def create_analyst_agent():
    """
    Create an analyst specialist sub-agent.

    This agent is optimized for data analysis and calculations.
    """
    system_prompt = """You are a Data Analyst Specialist.

Your role:
- Perform accurate calculations
- Analyze sentiment in text
- Provide detailed analytical insights
- Explain your analytical process

Always show your work and reasoning."""

    return create_react_agent(
        get_ollama_model(temperature=0.2),
        tools=[calculate, analyze_sentiment],
        prompt=system_prompt,
    )


def create_conversation_agent():
    """
    Create a conversation specialist sub-agent.

    This agent is optimized for natural, engaging dialogue.
    """
    system_prompt = """You are a Conversation Specialist.

Your role:
- Engage in natural, friendly dialogue
- Handle general questions and small talk
- Be warm, empathetic, and helpful
- Maintain context across the conversation

Focus on being conversational and approachable."""

    return create_react_agent(
        get_ollama_model(temperature=0.9),
        tools=[],  # Conversation agent doesn't need special tools
        prompt=system_prompt,
    )


# Registry of available sub-agents
SUB_AGENTS = {
    "research": create_research_agent,
    "analyst": create_analyst_agent,
    "conversation": create_conversation_agent,
}


def get_sub_agent(agent_type: str):
    """
    Get a sub-agent by type.

    Args:
        agent_type: The type of agent ('research', 'analyst', 'conversation')

    Returns:
        The requested sub-agent or None if not found
    """
    factory = SUB_AGENTS.get(agent_type)
    if factory:
        return factory()
    return None