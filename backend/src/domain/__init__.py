"""
Domain Layer - Pure business logic (no framework dependencies).

This layer contains the core business entities, value objects, and repository
interfaces. It's the heart of Clean Architecture - everything else depends on it.

Modules:
- conversation: Chat threads and messages
- planning: Task planning and step management
- memory: Persistent notes and knowledge
- agent_orchestration: AI agent interaction protocols
"""

from .agent_orchestration import AgentResponse, AgentService, ToolCall
from .conversation import Message, MessageRole, Thread, ThreadId, ThreadRepository
from .memory import Note, NoteRepository
from .planning import Plan, PlanRepository, PlanStatus, Step

__all__ = [
    # Conversation
    "Message",
    "MessageRole",
    "Thread",
    "ThreadId",
    "ThreadRepository",
    # Planning
    "Plan",
    "Step",
    "PlanStatus",
    "PlanRepository",
    # Memory
    "Note",
    "NoteRepository",
    # Agent Orchestration
    "AgentService",
    "AgentResponse",
    "ToolCall",
]
