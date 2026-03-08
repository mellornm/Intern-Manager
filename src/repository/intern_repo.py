from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.intern import Intern
from data.database import db_manager


class InternRepository:
    """
    Repository responsible for persistence and retrieval of Intern entities.

    This class encapsulates database operations for interns, mapping directly
    to the `interns` table using SQLAlchemy 2.0.
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initializes the repository with a SQLAlchemy session.

        Args:
            session (Optional[Session]): An active SQLAlchemy session. 
                If None, it uses the global db_manager.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Returns the active session or gets a new one from the manager."""
        return self._session or db_manager.get_session()

    def get_all(self) -> List[Intern]:
        """
        Retrieves all interns from the database, ordered by name.

        Returns:
            List[Intern]: A list of Intern model instances.
        """
        stmt = select(Intern).order_by(Intern.name.asc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, intern_id: int) -> Optional[Intern]:
        """
        Retrieves an intern by their unique ID.

        Args:
            intern_id (int): The primary key ID.

        Returns:
            Optional[Intern]: The Intern instance if found, otherwise None.
        """
        return self.session.get(Intern, intern_id)

    def get_by_registration_number(self, ra: str) -> Optional[Intern]:
        """
        Retrieves an intern by their unique registration number (RA).

        Args:
            ra (str): The registration number to search for.

        Returns:
            Optional[Intern]: The Intern instance if found, otherwise None.
        """
        stmt = select(Intern).where(Intern.registration_number == ra)
        return self.session.scalars(stmt).first()

    def save(self, intern: Intern) -> int:
        """
        Persists a new Intern entity to the database.

        Args:
            intern (Intern): The intern model instance to save.

        Returns:
            int: The generated ID for the new intern.
        """
        self.session.add(intern)
        self.session.commit()
        return intern.intern_id

    def update(self, intern: Intern) -> bool:
        """
        Updates an existing Intern record in the database.

        Args:
            intern (Intern): The intern instance with updated data.

        Returns:
            bool: True if the update was successful.
        """
        # In SQLAlchemy, merge or simply committing an attached object handles updates.
        # We use merge to ensure it's attached to the current session.
        self.session.merge(intern)
        self.session.commit()
        return True

    def delete(self, intern_id: int) -> bool:
        """
        Deletes an intern record by their ID.

        Args:
            intern_id (int): The ID of the intern to remove.

        Returns:
            bool: True if the deletion was successful.
        """
        intern = self.get_by_id(intern_id)
        if intern:
            self.session.delete(intern)
            self.session.commit()
            return True
        return False
