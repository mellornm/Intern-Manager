from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from core.models.intern import Intern
from data.database import db_manager


class InternRepository:
    """
    Repository responsible for persistence and retrieval of Intern entities.

    This class encapsulates database operations for interns, mapping directly
    to the `interns` table using SQLAlchemy 2.0 with proper session lifecycle.
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initializes the repository with an optional SQLAlchemy session.

        Args:
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_all(self) -> List[Intern]:
        """
        Retrieves all interns from the database, ordered by name.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Intern).order_by(Intern.name.asc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, intern_id: int) -> Optional[Intern]:
        """
        Retrieves an intern by their unique ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Intern, intern_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_registration_number(self, ra: str) -> Optional[Intern]:
        """
        Retrieves an intern by their unique registration number (RA).
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Intern).where(Intern.registration_number == ra)
            return session.scalars(stmt).first()
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_name(self, name: str) -> Optional[Intern]:
        """
        Retrieves an intern by their name.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Intern).where(Intern.name == name)
            return session.scalars(stmt).first()
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, intern: Intern) -> int:
        """
        Persists a new Intern entity using a transactional scope.
        """
        if self._session:
            self._session.add(intern)
            self._session.flush()
            return intern.intern_id

        with db_manager.session_scope() as session:
            session.add(intern)
            session.flush()
            # ID is available after flush even before commit
            return intern.intern_id

    def update(self, intern: Intern) -> bool:
        """
        Updates an existing Intern record.
        """
        if self._session:
            self._session.merge(intern)
            return True

        with db_manager.session_scope() as session:
            session.merge(intern)
            return True

    def delete(self, intern_id: int) -> bool:
        """
        Deletes an intern record by their ID.
        """
        if self._session:
            intern = self._session.get(Intern, intern_id)
            if intern:
                self._session.delete(intern)
                return True
            return False

        with db_manager.session_scope() as session:
            intern = session.get(Intern, intern_id)
            if intern:
                session.delete(intern)
                return True
            return False

    def count_total(self) -> int:
        """Counts total number of interns."""
        session = self._session or db_manager.get_session()
        try:
            stmt = select(func.count(Intern.intern_id))
            return session.scalar(stmt) or 0
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def count_without_venue(self) -> int:
        """Counts interns that are not allocated to any venue."""
        session = self._session or db_manager.get_session()
        try:
            stmt = select(func.count(Intern.intern_id)).where(Intern.venue_id == None)
            return session.scalar(stmt) or 0
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()
