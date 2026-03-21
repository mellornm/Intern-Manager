from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.intern import Intern


class Meeting(Base):
    """
    SQLAlchemy model representing a supervisory meeting with an intern.

    This class maps to the 'meetings' table and tracks attendance for
    individual supervision sessions.
    """

    __tablename__ = "meetings"

    # Primary key
    meeting_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key relationship to the intern (matches legacy order)
    intern_id: Mapped[int] = mapped_column(
        ForeignKey("interns.intern_id", ondelete="CASCADE"), nullable=False
    )

    # Core meeting fields
    meeting_date: Mapped[str] = mapped_column(String, nullable=False)

    # Boolean stored as Integer (0 or 1) in SQLite
    is_intern_present: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Added field (at the end for safer migration)
    meeting_topic: Mapped[str] = mapped_column(
        String, server_default="General Follow-up", nullable=False
    )

    # Relationship to the Intern model
    intern: Mapped["Intern"] = relationship("Intern", back_populates="meetings")

    def __repr__(self) -> str:
        """Returns a string representation of the Meeting instance."""
        return f"<Meeting(id={self.meeting_id}, date='{self.meeting_date}', present={self.is_intern_present})>"
