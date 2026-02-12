from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Intern:
    """
    Domain model representing an intern.

    This class mirrors the structure of the `interns` table in the database.

    Attributes:
        name (str): The intern's full name.
        registration_number (str): Unique registration number for the intern.
        term (str): The academic term or period of the internship.
        intern_id (Optional[int]): Unique database identifier. None if the intern has not yet been persisted.
        email (Optional[str]): The intern's email address.
        start_date (Optional[str]): The start date of the internship in 'YYYY-MM-DD' format.
        end_date (Optional[str]): The end date of the internship in 'YYYY-MM-DD' format.
        working_days (Optional[str]): Description of the intern's working days.
        working_hours (Optional[str]): Description of the intern's working hours.
        venue_id (Optional[int]): Foreign key to the venue where the intern works.
    """

    name: str
    registration_number: str
    term: str

    intern_id: Optional[int] = None
    email: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    working_days: Optional[str] = None
    working_hours: Optional[str] = None

    venue_id: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: Any) -> Optional["Intern"]:
        """
        Creates an Intern instance from a database row.

        Args:
            row (Any): A dictionary-like object representing a row from the database's 'interns' table.

        Returns:
            Optional[Intern]: An Intern instance populated with data from the row, or None if the input row is None.
        """
        if not row:
            return None

        return cls(
            intern_id=row["intern_id"],
            name=row["name"],
            registration_number=row["registration_number"],
            term=row["term"],
            email=row["email"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            working_days=row["working_days"],
            working_hours=row["working_hours"],
            venue_id=row["venue_id"],
        )

    @property
    def status(self) -> str:
        if not self.end_date:
            return "Ativo"
        try:
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            return "Concluído" if end < datetime.now() else "Ativo"
        except ValueError:
            return "Ativo"

    @property
    def formatted_start_date(self) -> str:
        if not self.start_date:
            return "-"
        try:
            return datetime.strptime(self.start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return self.start_date

    @property
    def formatted_end_date(self) -> str:
        if not self.end_date:
            return "-"
        try:
            return datetime.strptime(self.end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return self.end_date
