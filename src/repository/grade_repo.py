from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.grade import Grade
from data.database import db_manager


class GradeRepository:
    """
    Repository responsible for persistence and retrieval of Grade entities.

    This class manages the specific grades assigned to interns based on
    evaluation criteria using SQLAlchemy 2.0 with managed session lifecycle.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_all(self) -> List[Grade]:
        """
        Retrieves all grades stored in the database.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Grade).order_by(Grade.last_update.desc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_intern_id(self, intern_id: int) -> List[Grade]:
        """
        Retrieves all grades associated with a specific intern.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Grade).where(Grade.intern_id == intern_id)
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        """
        Retrieves a single grade by its ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Grade, grade_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, grade: Grade) -> int:
        """
        Persists a new Grade entity to the database.
        """
        if self._session:
            self._session.add(grade)
            self._session.flush()
            return grade.grade_id

        with db_manager.session_scope() as session:
            session.add(grade)
            session.flush()
            return grade.grade_id

    def update(self, grade: Grade) -> bool:
        """
        Updates an existing Grade record.
        """
        if self._session:
            self._session.merge(grade)
            return True

        with db_manager.session_scope() as session:
            session.merge(grade)
            return True

    def delete(self, grade_id: int) -> bool:
        """
        Permanently deletes a Grade record by its ID.
        """
        if self._session:
            grade = self._session.get(Grade, grade_id)
            if grade:
                self._session.delete(grade)
                return True
            return False

        with db_manager.session_scope() as session:
            grade = session.get(Grade, grade_id)
            if grade:
                session.delete(grade)
                return True
            return False
