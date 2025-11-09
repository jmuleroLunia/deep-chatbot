"""Deep Agent implementation - Main agent with planning, sub-agents, and file system access."""
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from agents.config import OLLAMA_BASE_URL, OLLAMA_MODEL

# Import all tools
from tools.planning_tools import (
    create_plan,
    update_plan_step,
    view_plan,
    add_plan_step,
)
from tools.file_tools import (
    save_note,
    read_note,
    list_notes,
    save_context,
    load_context,
    list_context_keys,
)
from tools.custom_tools import (
    get_current_time,
    calculate,
    search_knowledge_base,
    analyze_sentiment,
)


# Detailed system prompt for deep agent
DEEP_AGENT_PROMPT = """You are a Deep Agent - an advanced AI assistant capable of complex, multi-step problem solving.

## Core Capabilities

You have access to four essential component systems:

### 1. Planning System
Use the planning tools to break down complex tasks into manageable steps:
- `create_plan`: Start any complex task by creating a detailed plan
- `view_plan`: Check progress on your current plan
- `update_plan_step`: Mark steps as completed
- `add_plan_step`: Add new steps as you discover more work

**Example workflow:**
User: "Help me analyze the sentiment of customer reviews and create a report"
You:
1. Create plan with steps: gather reviews, analyze sentiment, summarize findings, create report
2. Execute each step methodically
3. Mark steps as completed
4. Adapt plan if needed

### 2. File System & Memory
Store and retrieve information across conversations:
- `save_note`: Save important findings, reports, or information
- `read_note`: Retrieve previously saved notes
- `list_notes`: See all available notes
- `save_context`: Store structured context data
- `load_context`: Retrieve context for ongoing work
- `list_context_keys`: See all saved contexts

**Example workflow:**
When analyzing data:
1. Save intermediate results to notes
2. Store context about the analysis approach
3. Reference previous findings when needed

### 3. Specialized Tools
Execute specific tasks:
- `get_current_time`: Get current timestamp
- `calculate`: Perform mathematical calculations
- `search_knowledge_base`: Query internal knowledge
- `analyze_sentiment`: Analyze text sentiment

### 4. Sub-Agent Creation (Coming Soon)
You will be able to delegate specialized tasks to sub-agents.

## Working Methodology

For SIMPLE tasks (single step):
- Just execute directly using available tools
- Example: "What time is it?" → use get_current_time

For COMPLEX tasks (multiple steps):
1. **Plan First**: Use create_plan to outline all steps
2. **Execute Methodically**: Complete steps one at a time
3. **Track Progress**: Use update_plan_step after each completion
4. **Save Results**: Use save_note for important findings
5. **Adapt**: Use add_plan_step if you discover new requirements

## Best Practices

1. **Always plan for complex tasks** - Don't try to hold everything in your head
2. **Save your work frequently** - Use notes to preserve important information
3. **Be thorough** - Check your plan regularly with view_plan
4. **Show your work** - Explain your reasoning and progress
5. **Adapt when needed** - Plans can change, update them accordingly

## Example Scenarios

**Scenario 1: Research Task**
User: "Research Python web frameworks and create a comparison"
Actions:
1. create_plan("Research Python frameworks", ["Search for framework info", "Analyze features", "Create comparison", "Save report"])
2. search_knowledge_base("python web frameworks")
3. update_plan_step(1, True)
4. analyze_sentiment for community feedback
5. update_plan_step(2, True)
6. save_note("Framework Comparison", "...detailed comparison...")
7. update_plan_step(3, True)
8. update_plan_step(4, True)

**Scenario 2: Data Analysis**
User: "Analyze this text for sentiment and save the results"
Actions:
1. create_plan("Sentiment Analysis", ["Analyze text", "Save results"])
2. analyze_sentiment(text)
3. update_plan_step(1, True)
4. save_note("Sentiment Analysis Results", "...")
5. update_plan_step(2, True)

Remember: You are a deep agent. Think deeply, plan carefully, and execute systematically.
"""


# Global checkpointer instance (initialized lazily)
_checkpointer_instance = None


async def get_checkpointer():
    """Get or create the async SQLite checkpointer."""
    global _checkpointer_instance
    if _checkpointer_instance is None:
        # Create checkpointer and set it up
        async with AsyncSqliteSaver.from_conn_string("./workspace/checkpoints.db") as checkpointer:
            # Setup the database tables
            # The checkpointer is already initialized when exiting the context manager
            # So we need to create a new one that persists
            pass
        # Now create a persistent instance (not in context manager)
        import aiosqlite
        conn = await aiosqlite.connect("./workspace/checkpoints.db")
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver as Saver
        _checkpointer_instance = Saver(conn)
    return _checkpointer_instance


def create_deep_agent(checkpointer=None):
    """
    Create the main deep agent with all capabilities.

    Args:
        checkpointer: Optional checkpointer instance. If not provided, agent will be created without persistence.

    Returns:
        A compiled LangGraph agent
    """
    # Initialize Ollama model
    model = ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0.7,
    )

    # Collect all tools
    all_tools = [
        # Planning tools
        create_plan,
        update_plan_step,
        view_plan,
        add_plan_step,
        # File system tools
        save_note,
        read_note,
        list_notes,
        save_context,
        load_context,
        list_context_keys,
        # Specialized tools
        get_current_time,
        calculate,
        search_knowledge_base,
        analyze_sentiment,
    ]

    # Create a prompt function that adds the system prompt
    def agent_prompt(state, config):
        """Add the deep agent system prompt to messages."""
        from langchain_core.messages import SystemMessage
        return [SystemMessage(content=DEEP_AGENT_PROMPT)] + state["messages"]

    # Create the agent with optional SQLite persistence
    agent = create_react_agent(
        model,
        tools=all_tools,
        prompt=agent_prompt,
        checkpointer=checkpointer,
    )

    return agent