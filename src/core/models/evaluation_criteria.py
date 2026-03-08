from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.grade import Grade


class EvaluationCriteria(Base):
    """
    SQLAlchemy model representing a specific assessment criteria.

    This class defines the "rules" of an evaluation, such as its name
    (e.g., "Final Report") and its weight in the final grade calculation.
    It acts as a reference table for individual Grade entries.
    """

    __tablename__ = "evaluation_criteria"

    # Primary key
    criteria_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Criteria definition
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    weight: Mapped[float] = mapped_column(Float, server_default="1.0", nullable=False)

    # Audit column - defaults to current timestamp on SQLite
    last_update: Mapped[Optional[str]] = mapped_column(
        String,
        server_default=func.datetime("now", "localtime"),
        onupdate=func.datetime("now", "localtime"),
    )

    # Relationship to Grades
    # One criteria can have many grades assigned (one per intern)
    grades: Mapped[List["Grade"]] = relationship(
        "Grade", back_populates="criteria", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Returns a string representation of the EvaluationCriteria instance."""
        return f"<EvaluationCriteria(id={self.criteria_id}, name='{self.name}', weight={self.weight})>"
