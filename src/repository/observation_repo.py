from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.observation import Observation
from data.database import db_manager


class ObservationRepository:
    """
    Repository responsible for persistence and retrieval of Observation entities.

    This class provides an interface to the `observations` table using 
    SQLAlchemy 2.0 for management of free-text notes associated with interns.
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

    def get_all(self) -> List[Observation]:
        """
        Retrieves all observations stored in the database.

        The results are ordered by the last update timestamp in descending order.

        Returns:
            List[Observation]: A list of all Observation model instances.
        """
        stmt = select(Observation).order_by(Observation.last_update.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_intern_id(self, intern_id: int) -> List[Observation]:
        """
        Retrieves all observations associated with a specific intern.

        Args:
            intern_id (int): The ID of the intern.

        Returns:
            List[Observation]: A list of Observation instances for that intern.
        """
        stmt = (
            select(Observation)
            .where(Observation.intern_id == intern_id)
            .order_by(Observation.last_update.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, observation_id: int) -> Optional[Observation]:
        """
        Retrieves a single observation by its ID.

        Args:
            observation_id (int): The unique identifier.

        Returns:
            Optional[Observation]: The Observation instance if found, otherwise None.
        """
        return self.session.get(Observation, observation_id)

    def save(self, observation: Observation) -> int:
        """
        Persists a new Observation entity to the database.

        Args:
            observation (Observation): The entity to be saved.

        Returns:
            int: The generated ID for the new observation.
        """
        self.session.add(observation)
        self.session.commit()
        return observation.observation_id

    def update(self, observation: Observation) -> bool:
        """
        Updates an existing Observation record in the database.

        Args:
            observation (Observation): The entity with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(observation)
        self.session.commit()
        return True

    def delete(self, observation_id: int) -> bool:
        """
        Permanently deletes an Observation record by its ID.

        Args:
            observation_id (int): The unique identifier of the observation.

        Returns:
            bool: True if the deletion was successful.
        """
        observation = self.get_by_id(observation_id)
        if observation:
            self.session.delete(observation)
            self.session.commit()
            return True
        return False
