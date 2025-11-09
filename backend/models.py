"""
Database models for Thread and Message management.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Thread(Base):
    """
    Thread model representing a conversation thread.

    Attributes:
        id: Unique thread identifier (UUID string)
        title: Thread title (auto-generated or user-set)
        created_at: Timestamp when thread was created
        updated_at: Timestamp when thread was last updated
        metadata: JSON field for additional thread data
        messages: Relationship to Message objects
    """
    __tablename__ = "threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    thread_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.timestamp"
    )
    plans: Mapped[list["Plan"]] = relationship(
        "Plan",
        back_populates="thread",
        cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Note.created_at"
    )

    def __repr__(self) -> str:
        return f"<Thread(id='{self.id}', title='{self.title}')>"


class Message(Base):
    """
    Message model representing a single message in a thread.

    Attributes:
        id: Unique message identifier
        thread_id: Foreign key to parent thread
        role: Message role ('user', 'assistant', 'system', 'tool')
        content: Message content text
        timestamp: When the message was created
        tool_calls: JSON field for tool call data (if role='assistant')
        tool_call_id: ID linking to a tool call (if role='tool')
        thread: Relationship to parent Thread
    """
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_call_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationship to thread
    thread: Mapped["Thread"] = relationship("Thread", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, thread_id='{self.thread_id}', role='{self.role}')>"


class Plan(Base):
    """
    Plan model representing a task plan for a thread.

    Attributes:
        id: Unique plan identifier
        thread_id: Foreign key to parent thread
        task: Description of the task being planned
        steps: JSON array of plan steps with status and description
        status: Overall plan status ('active', 'completed', 'cancelled')
        created_at: Timestamp when plan was created
        updated_at: Timestamp when plan was last updated
        thread: Relationship to parent Thread
    """
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship to thread
    thread: Mapped["Thread"] = relationship("Thread", back_populates="plans")

    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, thread_id='{self.thread_id}', task='{self.task[:50]}...')>"


class Note(Base):
    """
    Note model representing a saved note for a thread.

    Attributes:
        id: Unique note identifier
        thread_id: Foreign key to parent thread
        filename: Name of the note file
        content: Note content text
        created_at: Timestamp when note was created
        updated_at: Timestamp when note was last updated
        thread: Relationship to parent Thread
    """
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship to thread
    thread: Mapped["Thread"] = relationship("Thread", back_populates="notes")

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, thread_id='{self.thread_id}', filename='{self.filename}')>"
