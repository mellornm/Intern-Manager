from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.intern import Intern


class Observation(Base):
    """
    SQLAlchemy model representing a pedagogical observation or incident report about an intern.

    This class maps to the 'observations' table and stores notes, medical/field incidents,
    and optional supporting document attachments for individual students.
    """

    __tablename__ = "observations"

    # Primary key
    observation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core observation content
    observation: Mapped[str] = mapped_column(String, nullable=False)

    # Incident / Alert flag (True = Ocorrência/Intercorrência, False = Observação comum)
    is_incident: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False
    )

    # Optional physical attachment filename stored in USER_DATA_ROOT / "attachments"
    attachment_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Audit column - defaults to current timestamp on SQLite
    last_update: Mapped[Optional[str]] = mapped_column(
        String,
        server_default=func.strftime("%Y-%m-%d %H:%M:%S", "now", "localtime"),
        onupdate=func.strftime("%Y-%m-%d %H:%M:%S", "now", "localtime"),
    )

    # Foreign key relationship to the intern
    intern_id: Mapped[int] = mapped_column(
        ForeignKey("interns.intern_id", ondelete="CASCADE"), nullable=False
    )

    # Relationship to the Intern model
    # Uses a string reference to avoid circular imports during runtime
    intern: Mapped["Intern"] = relationship("Intern", back_populates="observations")

    def __repr__(self) -> str:
        """Returns a string representation of the Observation instance."""
        return (
            f"<Observation(id={self.observation_id}, intern_id={self.intern_id}, "
            f"incident={self.is_incident}, attachment={self.attachment_path})>"
        )
