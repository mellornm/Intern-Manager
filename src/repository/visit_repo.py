from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.visit import Visit
from data.database import db_manager


class VisitRepository:
    """
    Repository responsible for persistence and retrieval of Visit entities.

    This class handles the database interactions for technical visits 
    using SQLAlchemy 2.0 with managed session lifecycle.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_all(self) -> List[Visit]:
        """
        Retrieves all visits stored in the database.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Visit).order_by(Visit.visit_date.desc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_intern_id(self, intern_id: int) -> List[Visit]:
        """
        Retrieves all visits associated with a specific intern.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = (
                select(Visit)
                .where(Visit.intern_id == intern_id)
                .order_by(Visit.visit_date.desc())
            )
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    # Keep alias for compatibility
    get_by_intern = get_by_intern_id

    def get_by_id(self, visit_id: int) -> Optional[Visit]:
        """
        Retrieves a single visit by its ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Visit, visit_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, visit: Visit) -> int:
        """
        Persists a new Visit entity to the database.
        """
        if self._session:
            self._session.add(visit)
            self._session.flush()
            return visit.visit_id

        with db_manager.session_scope() as session:
            session.add(visit)
            session.flush()
            return visit.visit_id

    def update(self, visit: Visit) -> bool:
        """
        Updates an existing Visit record.
        """
        if self._session:
            self._session.merge(visit)
            return True

        with db_manager.session_scope() as session:
            session.merge(visit)
            return True

    def delete(self, visit_id: int) -> bool:
        """
        Deletes a visit record by its ID.
        """
        if self._session:
            visit = self._session.get(Visit, visit_id)
            if visit:
                self._session.delete(visit)
                return True
            return False

        with db_manager.session_scope() as session:
            visit = session.get(Visit, visit_id)
            if visit:
                session.delete(visit)
                return True
            return False
