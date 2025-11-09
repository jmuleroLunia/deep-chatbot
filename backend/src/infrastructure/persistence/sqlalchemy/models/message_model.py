"""SQLAlchemy ORM model for Message."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class MessageModel(Base):
    """
    SQLAlchemy ORM model for Message entity.

    Maps to the 'messages' table in the database.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "timestamp",  # Keep old column name for compatibility
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    thread: Mapped["ThreadModel"] = relationship(
        "ThreadModel", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<MessageModel(id={self.id}, thread_id='{self.thread_id}', role='{self.role}')>"
