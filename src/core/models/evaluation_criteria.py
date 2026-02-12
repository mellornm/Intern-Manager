from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class EvaluationCriteria:
    """
    Domain model representing a specific assessment criteria.

    This class defines the "rules" of an evaluation, such as its name
    (e.g., "Final Report") and its weight in the final grade calculation.
    It acts as a reference table for the Grade entries.

    This class mirrors the structure of the `evaluation_criteria` table in the database.

    Attributes:
        criteria_id (Optional[int]): Unique database identifier. None if the
            criteria has not yet been persisted.
        name (str): The display name of the criteria (e.g., "Supervisor Evaluation").
        description (Optional[str]): Detailed instructions or description of the criteria.
        weight (float): The weight of this criteria in the final grade average.
            Defaults to 1.0.
    """

    name: str
    description: str = ""
    weight: float = 1.0
    criteria_id: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: Any) -> Optional["EvaluationCriteria"]:
        """
        Creates a Evaluation Criteria instance from a database row.

        Args:
            row (Any): A dictionary-like object representing a row from the database's 'evaluation_createria' table.

        Returns:
            Optional[EvaluationCriteria]: An EvaluationCriteria instance populated with data from the row, or None if the input row is None.
        """
        if not row:
            return None
        return cls(
            criteria_id=row["criteria_id"],
            name=row["name"],
            description=row["description"],
            weight=float(row["weight"]),  # Garante float no peso
        )
