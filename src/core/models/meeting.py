from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class Meeting:
    """
    Domain model representing a supervisory meeting with an intern.

    This class mirrors the structure of the `meetings` table in the database.
    It tracks whether the intern was present and when the meeting occurred.

    Attributes:
        meeting_id (Optional[int]): Unique database identifier.
        intern_id (int): Identifier of the associated intern.
        meeting_date (str): Date of the meeting (ISO format preferred for DB).
        is_intern_present (int): 1 if present, 0 if absent.
    """

    intern_id: int
    meeting_date: str
    is_intern_present: bool
    meeting_id: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: Any) -> Optional["Meeting"]:
        """
        Creates a Meeting instance from a database row.

        Args:
            row (Any): A dictionary-like object representing a row from the database's 'meetings' table.

        Returns:
            Optional[Meeting]: A Meeting instance populated with data from the row, or None if the input row is None.
        """
        if not row:
            return None
        return cls(
            meeting_id=row["meeting_id"],
            intern_id=row["intern_id"],
            meeting_date=row["meeting_date"],
            # O Python converte 1 -> True e 0 -> False automaticamente
            is_intern_present=bool(row["is_intern_present"]),
        )
