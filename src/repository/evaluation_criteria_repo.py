from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.evaluation_criteria import EvaluationCriteria
from data.database import db_manager


class EvaluationCriteriaRepository:
    """
    Repository responsible for persistence and retrieval of EvaluationCriteria entities.

    This class encapsulates database operations for the criteria used in intern
    evaluations using SQLAlchemy 2.0.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Returns the active session or gets a new one from the manager."""
        return self._session or db_manager.get_session()

    def get_all(self) -> List[EvaluationCriteria]:
        """
        Retrieves all evaluation criteria stored in the database.

        Returns:
            List[EvaluationCriteria]: A list of all criteria model instances.
        """
        stmt = select(EvaluationCriteria).order_by(EvaluationCriteria.name.asc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, criteria_id: int) -> Optional[EvaluationCriteria]:
        """
        Retrieves a single evaluation criteria by its ID.

        Args:
            criteria_id (int): The unique identifier of the criteria.

        Returns:
            Optional[EvaluationCriteria]: The criteria instance if found, otherwise None.
        """
        return self.session.get(EvaluationCriteria, criteria_id)

    def save(self, criteria: EvaluationCriteria) -> int:
        """
        Persists a new EvaluationCriteria entity to the database.

        Args:
            criteria (EvaluationCriteria): The entity to be saved.

        Returns:
            int: The generated ID for the new criteria.
        """
        self.session.add(criteria)
        self.session.commit()
        return criteria.criteria_id

    def update(self, criteria: EvaluationCriteria) -> bool:
        """
        Updates an existing EvaluationCriteria record.

        Args:
            criteria (EvaluationCriteria): The entity with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(criteria)
        self.session.commit()
        return True

    def delete(self, criteria_id: int) -> bool:
        """
        Deletes an evaluation criteria record from the database by its ID.

        Args:
            criteria_id (int): The unique identifier of the criteria to delete.

        Returns:
            bool: True if the deletion was successful.
        """
        criteria = self.get_by_id(criteria_id)
        if criteria:
            self.session.delete(criteria)
            self.session.commit()
            return True
        return False
