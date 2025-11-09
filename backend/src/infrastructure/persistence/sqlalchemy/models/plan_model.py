"""SQLAlchemy ORM models for Plan and Step."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class PlanModel(Base):
    """
    SQLAlchemy ORM model for Plan entity.

    Maps to the 'plans' table in the database.
    """

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)  # Legacy field for compatibility
    steps_json: Mapped[list] = mapped_column("steps", JSON, nullable=False, default=list)  # Legacy JSON field
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
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
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    thread: Mapped["ThreadModel"] = relationship("ThreadModel", back_populates="plans")
    steps: Mapped[list["StepModel"]] = relationship(
        "StepModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="StepModel.step_number",
    )

    def __repr__(self) -> str:
        return f"<PlanModel(id={self.id}, thread_id='{self.thread_id}', title='{self.title[:50]}')>"


class StepModel(Base):
    """
    SQLAlchemy ORM model for Step entity.

    Maps to the 'steps' table in the database.
    """

    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    plan: Mapped["PlanModel"] = relationship("PlanModel", back_populates="steps")

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"<StepModel(id={self.id}, plan_id={self.plan_id}, #{self.step_number} {status})>"
