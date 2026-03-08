from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from utils.validations import format_date_to_br

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.venue import Venue
    from core.models.document import Document
    from core.models.grade import Grade
    from core.models.meeting import Meeting
    from core.models.observation import Observation
    from core.models.visit import Visit


class Intern(Base):
    """
    SQLAlchemy model representing an intern in the system.

    This class maps to the 'interns' table and stores all personal and
    contractual information for a student participating in the program.
    """

    __tablename__ = "interns"

    # Primary key with auto-increment is handled by SQLAlchemy for Integer PKs
    intern_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core identity fields
    name: Mapped[str] = mapped_column(String, nullable=False)
    registration_number: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Internship period and scheduling
    start_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    working_days: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    working_hours: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Academic classification
    term: Mapped[str] = mapped_column(String, nullable=False)

    # Audit column - defaults to current timestamp on SQLite
    last_update: Mapped[Optional[str]] = mapped_column(
        String,
        server_default=func.strftime("%Y-%m-%d %H:%M:%S", "now", "localtime"),
        onupdate=func.strftime("%Y-%m-%d %H:%M:%S", "now", "localtime"),
    )

    # Foreign key relationship to the venue
    venue_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("venues.venue_id"), nullable=True
    )

    # Relationships to other models
    # Uses a string reference to avoid circular imports during runtime
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="interns")
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="intern", cascade="all, delete-orphan"
    )
    grades: Mapped[List["Grade"]] = relationship(
        "Grade", back_populates="intern", cascade="all, delete-orphan"
    )
    meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting", back_populates="intern", cascade="all, delete-orphan"
    )
    observations: Mapped[List["Observation"]] = relationship(
        "Observation", back_populates="intern", cascade="all, delete-orphan"
    )
    visits: Mapped[List["Visit"]] = relationship(
        "Visit", back_populates="intern", cascade="all, delete-orphan"
    )

    @property
    def status(self) -> str:
        """
        Dynamically determines the intern's status based on current date.
        
        Returns:
            str: 'Ativo', 'Concluído', 'A Iniciar', or 'Incompleto'.
        """
        if not self.start_date or not self.end_date:
            return "Incompleto"

        try:
            # Assumes dates are stored in ISO format (YYYY-MM-DD)
            today = datetime.now().date()
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()

            if today < start:
                return "A Iniciar"
            elif start <= today <= end:
                return "Ativo"
            else:
                return "Concluído"
        except (ValueError, TypeError):
            return "Erro de Data"

    @property
    def formatted_start_date(self) -> str:
        """Returns the start date in BR format (DD/MM/YYYY)."""
        return format_date_to_br(self.start_date) or "-"

    @property
    def formatted_end_date(self) -> str:
        """Returns the end date in BR format (DD/MM/YYYY)."""
        return format_date_to_br(self.end_date) or "-"

    def __repr__(self) -> str:
        """Returns a string representation of the Intern instance."""
        return f"<Intern(id={self.intern_id}, name='{self.name}', ra='{self.registration_number}')>"
