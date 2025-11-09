"""SQLAlchemy ORM model for Note."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class NoteModel(Base):
    """
    SQLAlchemy ORM model for Note entity.

    Maps to the 'notes' table in the database.
    """

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # Legacy field
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
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

    # Relationship
    thread: Mapped["ThreadModel"] = relationship("ThreadModel", back_populates="notes")

    def __repr__(self) -> str:
        return f"<NoteModel(id={self.id}, thread_id='{self.thread_id}', title='{self.title}')>"
