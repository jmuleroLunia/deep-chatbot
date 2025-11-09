"""SQLAlchemy ORM model for Thread."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class ThreadModel(Base):
    """
    SQLAlchemy ORM model for Thread entity.

    Maps to the 'threads' table in the database.
    """

    __tablename__ = "threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, default="New Conversation"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    thread_metadata: Mapped[Optional[dict]] = mapped_column(
        "thread_metadata", JSON, nullable=True
    )

    # Relationships
    messages: Mapped[list["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at",
    )
    plans: Mapped[list["PlanModel"]] = relationship(
        "PlanModel",
        back_populates="thread",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="NoteModel.created_at",
    )

    def __repr__(self) -> str:
        return f"<ThreadModel(id='{self.id}')>"
