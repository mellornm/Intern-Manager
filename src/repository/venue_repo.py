from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from core.models.venue import Venue
from data.database import db_manager


class VenueRepository:
    """
    Repository responsible for persistence and retrieval of Venue entities.

    This class implements the Repository pattern using SQLAlchemy 2.0
    with managed session lifecycle.
    """

    def __init__(self, db: Optional[Any] = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Optional[Any]): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_all(self) -> List[Venue]:
        """
        Retrieves all venues stored in the database, ordered by name.
        """
        session = self._session or db_manager.get_session()
        try:
            # Eagerly load interns to check status in UI filters
            stmt = select(Venue).options(selectinload(Venue.interns)).order_by(Venue.venue_name.asc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        """
        Retrieves a single venue by its unique ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Venue, venue_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Retrieves a single venue by its unique name.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Venue).where(Venue.venue_name == name)
            return session.scalars(stmt).first()
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, venue: Venue) -> int:
        """
        Persists a new Venue entity to the database.
        """
        if self._session:
            self._session.add(venue)
            self._session.flush()
            return venue.venue_id

        with db_manager.session_scope() as session:
            session.add(venue)
            session.flush()
            return venue.venue_id

    def update(self, venue: Venue) -> bool:
        """
        Updates an existing Venue record.
        """
        if self._session:
            self._session.merge(venue)
            return True

        with db_manager.session_scope() as session:
            session.merge(venue)
            return True

    def delete(self, venue_id: int) -> bool:
        """
        Deletes a venue record by its ID.
        """
        if self._session:
            venue = self._session.get(Venue, venue_id)
            if venue:
                self._session.delete(venue)
                return True
            return False

        with db_manager.session_scope() as session:
            venue = session.get(Venue, venue_id)
            if venue:
                session.delete(venue)
                return True
            return False
