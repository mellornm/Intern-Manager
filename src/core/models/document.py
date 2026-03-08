from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    # Import for type checking only to avoid circular dependency
    from core.models.intern import Intern


class Document(Base):
    """
    SQLAlchemy model representing a document associated with an intern.

    This class maps to the 'documents' table and tracks the status and
    feedback for various internship-related files.
    """

    __tablename__ = "documents"

    # Primary key
    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Core document fields
    document_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, server_default="Pendente")
    feedback: Mapped[Optional[str]] = mapped_column(String, nullable=True)

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
    intern: Mapped["Intern"] = relationship("Intern", back_populates="documents")

    def __repr__(self) -> str:
        """Returns a string representation of the Document instance."""
        return f"<Document(id={self.document_id}, name='{self.document_name}', status='{self.status}')>"
