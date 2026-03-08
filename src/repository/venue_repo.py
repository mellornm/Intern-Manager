from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.venue import Venue
from data.database import db_manager


class VenueRepository:
    """
    Repository responsible for persistence and retrieval of Venue entities.

    This class implements the Repository pattern using SQLAlchemy 2.0
    for data access related to the `Venue` domain model.
    """

    def __init__(self, db: Optional[Any] = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Optional[Any]): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Returns the active session or gets a new one from the manager."""
        return self._session or db_manager.get_session()

    def get_all(self) -> List[Venue]:
        """
        Retrieves all venues stored in the database, ordered by name.

        Returns:
            List[Venue]: A list of Venue model instances.
        """
        stmt = select(Venue).order_by(Venue.venue_name.asc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        """
        Retrieves a single venue by its unique ID.

        Args:
            venue_id (int): The primary key ID.

        Returns:
            Optional[Venue]: The Venue instance if found, otherwise None.
        """
        return self.session.get(Venue, venue_id)

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Retrieves a single venue by its name.

        Args:
            name (str): The name of the venue.

        Returns:
            Optional[Venue]: The Venue instance if found, otherwise None.
        """
        stmt = select(Venue).where(Venue.venue_name == name)
        return self.session.scalars(stmt).first()

    def save(self, venue: Venue) -> int:
        """
        Persists a new Venue entity to the database.

        Args:
            venue (Venue): The venue model instance to save.

        Returns:
            int: The generated ID for the new venue.
        """
        self.session.add(venue)
        self.session.commit()
        return venue.venue_id

    def update(self, venue: Venue) -> bool:
        """
        Updates an existing Venue record.

        Args:
            venue (Venue): The venue instance with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(venue)
        self.session.commit()
        return True

    def delete(self, venue_id: int) -> bool:
        """
        Deletes a venue record by its ID.

        Args:
            venue_id (int): The ID of the venue to remove.

        Returns:
            bool: True if the deletion was successful.
        """
        venue = self.get_by_id(venue_id)
        if venue:
            self.session.delete(venue)
            self.session.commit()
            return True
        return False
