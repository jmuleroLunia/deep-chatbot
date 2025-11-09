"""Custom tools for the agents."""
from langchain_core.tools import tool
from datetime import datetime
import json


@tool
def get_current_time() -> str:
    """Get the current time and date."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation as a string
    """
    try:
        # Safety: only allow basic math operations
        allowed_chars = set("0123456789+-*/()%. ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"

        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the internal knowledge base for information.

    Args:
        query: The search query

    Returns:
        Relevant information from the knowledge base
    """
    # This is a mock implementation - in production, this would query a real database
    knowledge = {
        "python": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
        "fastapi": "FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints.",
        "langgraph": "LangGraph is a framework for building stateful, multi-agent applications with LLMs.",
    }

    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return value

    return f"No information found for query: {query}"


@tool
def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of a given text.

    Args:
        text: The text to analyze

    Returns:
        Sentiment analysis result (positive, negative, or neutral)
    """
    # Simple mock sentiment analysis
    positive_words = ["good", "great", "excellent", "happy", "love", "wonderful"]
    negative_words = ["bad", "terrible", "awful", "hate", "horrible", "sad"]

    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        return f"Sentiment: Positive (confidence: {positive_count})"
    elif negative_count > positive_count:
        return f"Sentiment: Negative (confidence: {negative_count})"
    else:
        return "Sentiment: Neutral"


@tool
def save_note(note: str) -> str:
    """
    Save a note for later reference.

    Args:
        note: The note to save

    Returns:
        Confirmation message
    """
    # In production, this would save to a database
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Note saved at {timestamp}: '{note}'"