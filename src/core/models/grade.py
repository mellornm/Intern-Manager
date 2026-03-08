from typing import Optional, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.intern import Intern
    from core.models.evaluation_criteria import EvaluationCriteria


class Grade(Base):
    """
    SQLAlchemy model representing a grade assigned to an intern.

    Each Grade links a specific Intern to a specific EvaluationCriteria
    and stores the numerical value achieved. This serves as the
    intersection entity for the student's report card.
    """

    __tablename__ = "grades"

    # Primary key
    grade_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Numerical score achieved
    value: Mapped[float] = mapped_column(Float, nullable=False)

    # Audit column - defaults to current timestamp on SQLite
    last_update: Mapped[Optional[str]] = mapped_column(
        String,
        server_default=func.datetime("now", "localtime"),
        onupdate=func.datetime("now", "localtime"),
    )

    # Foreign key relationship to the intern
    intern_id: Mapped[int] = mapped_column(
        ForeignKey("interns.intern_id", ondelete="CASCADE"), nullable=False
    )

    # Foreign key relationship to the criteria
    criteria_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_criteria.criteria_id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    # Uses string references to avoid circular imports during runtime
    intern: Mapped["Intern"] = relationship("Intern", back_populates="grades")
    criteria: Mapped["EvaluationCriteria"] = relationship(
        "EvaluationCriteria", back_populates="grades"
    )

    # Ensure an intern only has one grade per criteria
    __table_args__ = (
        UniqueConstraint("intern_id", "criteria_id", name="uq_intern_criteria"),
    )

    def __repr__(self) -> str:
        """Returns a string representation of the Grade instance."""
        return f"<Grade(id={self.grade_id}, intern_id={self.intern_id}, criteria_id={self.criteria_id}, value={self.value})>"
