from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class Meeting:
    """
    Domain model representing a supervisory meeting with an intern.

    This class mirrors the structure of the `meetings` table in the database.
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
            row (Any): A dictionary-like object representing a row.

        Returns:
            Optional[Meeting]: A Meeting instance or None.
        """
        if not row:
            return None

        return cls(
            intern_id=row["intern_id"],
            meeting_date=row["meeting_date"],
            is_intern_present=bool(row["is_intern_present"]),
            meeting_id=row["meeting_id"],
        )
