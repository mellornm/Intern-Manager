from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.intern import Intern
    from core.models.visit import Visit


class Venue(Base):
    """
    SQLAlchemy model representing a venue where interns are allocated.

    A Venue represents an organization, unit, or location responsible
    for hosting one or more interns. Each venue may be associated with
    multiple interns.
    """

    __tablename__ = "venues"

    # Primary key
    venue_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core identification
    venue_name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Supervisor contact information
    supervisor_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    supervisor_email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    supervisor_phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Audit column - defaults to current timestamp
    last_update: Mapped[Optional[str]] = mapped_column(
        String,
        server_default=func.strftime("%Y-%m-%d %H:%M:%S", "now", "localtime"),
        onupdate=func.strftime("%Y-%m-%d %H:%M:%S", "now", "localtime"),
    )

    # Relationships
    # One venue can host many interns and receive many visits
    interns: Mapped[List["Intern"]] = relationship("Intern", back_populates="venue")
    visits: Mapped[List["Visit"]] = relationship("Visit", back_populates="venue")

    def __repr__(self) -> str:
        """Returns a string representation of the Venue instance."""
        return f"<Venue(id={self.venue_id}, name='{self.venue_name}')>"
