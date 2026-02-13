from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class Visit:
    """
    Domain model representing a technical visit by an intern to a venue.

    This class maps to the 'visits' table and handles tracking of visit
    locations, dates, and optional evidence like photos and observations.
    """

    intern_id: int
    venue_id: int
    visit_date: str

    observation: Optional[str] = None
    photo_path: Optional[str] = None
    visit_id: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: Any) -> Optional["Visit"]:
        """
        Hydrates a Visit instance from a database dictionary row.

        Args:
            row (Any): A row-like object (dict or sqlite3.Row).

        Returns:
            Optional[Visit]: A populated Visit instance or None if row is empty.
        """
        if not row:
            return None

        return cls(
            intern_id=row["intern_id"],
            venue_id=row["venue_id"],
            visit_date=row["visit_date"],
            observation=row["observation"],
            photo_path=row["photo_path"],
            visit_id=row["visit_id"],
        )
