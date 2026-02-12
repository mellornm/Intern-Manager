from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class Grade:
    """
    Domain model representing a grade assigned to an intern.

    Each Grade links a specific Intern to a specific EvaluationCriteria
    and stores the numerical value achieved. This is the intersection
    entity that effectively represents the student's report card.

    This class mirrors the structure of the `grades` table in the database.

    Attributes:
        grade_id (Optional[int]): Unique database identifier. None if the
            grade has not yet been persisted.
        intern_id (int): Identifier of the evaluated intern.
        criteria_id (int): Identifier of the evaluation criteria being applied.
        value (float): The numerical score achieved by the intern.
        last_update (Optional[str]): Timestamp of the last modification.
    """

    intern_id: int
    criteria_id: int
    value: float
    grade_id: Optional[int] = None
    last_update: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: Any) -> Optional["Grade"]:
        """
        Creates a Grade instance from a database row.

        Args:
            row (Any): A dictionary-like object representing a row from the database's 'grades' table.

        Returns:
            Optional[Grade]: A Grade instance populated with data from the row, or None if the input row is None.
        """
        if not row:
            return None
        return cls(
            grade_id=row["grade_id"],
            intern_id=row["intern_id"],
            criteria_id=row["criteria_id"],
            value=float(row["value"]),
            last_update=row["last_update"],
        )
