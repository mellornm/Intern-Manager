from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class Observation:
    """
    Domain model representing a observation associated with an intern.

    Each Observation stores a textual annotation linked to a specific Intern.
    An intern may have multiple observations, typically used for notes,
    observations, or administrative records.

    This class mirrors the structure of the `observations` table in the database.

    Attributes:
        observation_id (Optional[int]): Unique database identifier. None if the
            observation has not yet been persisted.
        intern_id (int): Identifier of the associated intern.
        observation (str): Textual content of the observation.
        last_update (Optional[str]): Date string representing the last modification.
    """

    intern_id: int
    observation: str
    observation_id: Optional[int] = None
    last_update: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: Any) -> Optional["Observation"]:
        """
        Creates an Observation instance from a database row.

        Args:
            row (Any): A dictionary-like object representing a row from the database's 'observations' table.

        Returns:
            Optional[Observation]: An Observation instance populated with data from the row, or None if the input row is None.
        """
        if not row:
            return None
        return cls(
            observation_id=row["observation_id"],
            intern_id=row["intern_id"],
            observation=row["observation"],
            last_update=row["last_update"],
        )
