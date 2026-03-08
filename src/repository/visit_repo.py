from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.visit import Visit
from data.database import db_manager


class VisitRepository:
    """
    Repository responsible for persistence and retrieval of Visit entities.

    This class handles the database interactions for technical visits 
    using SQLAlchemy 2.0.
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

    def get_all(self) -> List[Visit]:
        """
        Retrieves all visits stored in the database.

        Results are ordered by date in descending order.

        Returns:
            List[Visit]: A list of all Visit model instances.
        """
        stmt = select(Visit).order_by(Visit.visit_date.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_intern_id(self, intern_id: int) -> List[Visit]:
        """
        Retrieves all visits associated with a specific intern.

        Args:
            intern_id (int): The ID of the intern.

        Returns:
            List[Visit]: A list of Visit instances for that intern.
        """
        stmt = (
            select(Visit)
            .where(Visit.intern_id == intern_id)
            .order_by(Visit.visit_date.desc())
        )
        return list(self.session.scalars(stmt).all())

    # Keep alias for compatibility
    get_by_intern = get_by_intern_id

    def get_by_id(self, visit_id: int) -> Optional[Visit]:
        """
        Retrieves a single visit by its ID.

        Args:
            visit_id (int): The unique identifier.

        Returns:
            Optional[Visit]: The Visit instance if found, otherwise None.
        """
        return self.session.get(Visit, visit_id)

    def save(self, visit: Visit) -> int:
        """
        Persists a new Visit entity to the database.

        Args:
            visit (Visit): The entity to be saved.

        Returns:
            int: The generated ID for the new visit.
        """
        self.session.add(visit)
        self.session.commit()
        return visit.visit_id

    def update(self, visit: Visit) -> bool:
        """
        Updates an existing Visit record.

        Args:
            visit (Visit): The visit instance with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(visit)
        self.session.commit()
        return True

    def delete(self, visit_id: int) -> bool:
        """
        Deletes a visit record by its ID.

        Args:
            visit_id (int): The unique identifier of the visit.

        Returns:
            bool: True if the deletion was successful.
        """
        visit = self.get_by_id(visit_id)
        if visit:
            self.session.delete(visit)
            self.session.commit()
            return True
        return False
