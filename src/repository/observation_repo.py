from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.observation import Observation
from data.database import db_manager


class ObservationRepository:
    """
    Repository responsible for persistence and retrieval of Observation entities.

    This class provides an interface to the `observations` table using
    SQLAlchemy 2.0 with managed session lifecycle.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_all(self) -> List[Observation]:
        """
        Retrieves all observations stored in the database.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Observation).order_by(Observation.last_update.desc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_intern_id(self, intern_id: int) -> List[Observation]:
        """
        Retrieves all observations associated with a specific intern.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = (
                select(Observation)
                .where(Observation.intern_id == intern_id)
                .order_by(Observation.last_update.desc())
            )
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, observation_id: int) -> Optional[Observation]:
        """
        Retrieves a single observation by its ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Observation, observation_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, observation: Observation) -> int:
        """
        Persists a new Observation entity to the database.
        """
        if self._session:
            self._session.add(observation)
            self._session.flush()
            return observation.observation_id

        with db_manager.session_scope() as session:
            session.add(observation)
            session.flush()
            return observation.observation_id

    def update(self, observation: Observation) -> bool:
        """
        Updates an existing Observation record in the database.
        """
        if self._session:
            self._session.merge(observation)
            return True

        with db_manager.session_scope() as session:
            session.merge(observation)
            return True

    def delete(self, observation_id: int) -> bool:
        """
        Permanently deletes an Observation record by its ID.
        """
        if self._session:
            observation = self._session.get(Observation, observation_id)
            if observation:
                self._session.delete(observation)
                return True
            return False

        with db_manager.session_scope() as session:
            observation = session.get(Observation, observation_id)
            if observation:
                session.delete(observation)
                return True
            return False
