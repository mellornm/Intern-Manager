from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.intern import Intern
    from core.models.venue import Venue


class Visit(Base):
    """
    SQLAlchemy model representing a technical visit by an intern to a venue.

    This class maps to the 'visits' table and tracks when and where an
    intern performed a technical activity, including photos and notes.
    """

    __tablename__ = "visits"

    # Primary key
    visit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core visit details
    visit_date: Mapped[str] = mapped_column(String, nullable=False)
    observation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Foreign key to the intern performing the visit
    intern_id: Mapped[int] = mapped_column(
        ForeignKey("interns.intern_id", ondelete="CASCADE"), nullable=False
    )

    # Foreign key to the venue visited
    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venues.venue_id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    # Uses string references to avoid circular imports during runtime
    intern: Mapped["Intern"] = relationship("Intern", back_populates="visits")
    venue: Mapped["Venue"] = relationship("Venue", back_populates="visits")

    def __repr__(self) -> str:
        """Returns a string representation of the Visit instance."""
        return f"<Visit(id={self.visit_id}, intern_id={self.intern_id}, venue_id={self.venue_id}, date='{self.visit_date}')>"
