from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.evaluation_criteria import EvaluationCriteria
from data.database import db_manager


class EvaluationCriteriaRepository:
    """
    Repository responsible for persistence and retrieval of EvaluationCriteria entities.

    This class encapsulates database operations for the criteria used in intern
    evaluations using SQLAlchemy 2.0 with managed session lifecycle.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_all(self) -> List[EvaluationCriteria]:
        """
        Retrieves all evaluation criteria stored in the database.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(EvaluationCriteria).order_by(EvaluationCriteria.name.asc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, criteria_id: int) -> Optional[EvaluationCriteria]:
        """
        Retrieves a single evaluation criteria by its ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(EvaluationCriteria, criteria_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, criteria: EvaluationCriteria) -> int:
        """
        Persists a new EvaluationCriteria entity to the database.
        """
        if self._session:
            self._session.add(criteria)
            self._session.flush()
            return criteria.criteria_id

        with db_manager.session_scope() as session:
            session.add(criteria)
            session.flush()
            return criteria.criteria_id

    def update(self, criteria: EvaluationCriteria) -> bool:
        """
        Updates an existing EvaluationCriteria record.
        """
        if self._session:
            self._session.merge(criteria)
            return True

        with db_manager.session_scope() as session:
            session.merge(criteria)
            return True

    def delete(self, criteria_id: int) -> bool:
        """
        Deletes an evaluation criteria record from the database by its ID.
        """
        if self._session:
            criteria = self._session.get(EvaluationCriteria, criteria_id)
            if criteria:
                self._session.delete(criteria)
                return True
            return False

        with db_manager.session_scope() as session:
            criteria = session.get(EvaluationCriteria, criteria_id)
            if criteria:
                session.delete(criteria)
                return True
            return False
