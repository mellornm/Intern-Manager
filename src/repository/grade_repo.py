from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.grade import Grade
from data.database import db_manager


class GradeRepository:
    """
    Repository responsible for persistence and retrieval of Grade entities.

    This class manages the specific grades assigned to interns based on
    evaluation criteria using SQLAlchemy 2.0.
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

    def get_all(self) -> List[Grade]:
        """
        Retrieves all grades stored in the database.

        The results are ordered by the last update timestamp in descending order.

        Returns:
            List[Grade]: A list of all Grade model instances.
        """
        stmt = select(Grade).order_by(Grade.last_update.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_intern_id(self, intern_id: int) -> List[Grade]:
        """
        Retrieves all grades associated with a specific intern.

        Args:
            intern_id (int): The ID of the intern.

        Returns:
            List[Grade]: A list of Grade instances for that intern.
        """
        stmt = select(Grade).where(Grade.intern_id == intern_id)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        """
        Retrieves a single grade by its ID.

        Args:
            grade_id (int): The unique identifier of the grade.

        Returns:
            Optional[Grade]: The Grade instance if found, otherwise None.
        """
        return self.session.get(Grade, grade_id)

    def save(self, grade: Grade) -> int:
        """
        Persists a new Grade entity to the database.

        Args:
            grade (Grade): The entity to be saved.

        Returns:
            int: The generated ID for the new grade.
        """
        self.session.add(grade)
        self.session.commit()
        return grade.grade_id

    def update(self, grade: Grade) -> bool:
        """
        Updates an existing Grade record.

        Args:
            grade (Grade): The grade instance with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(grade)
        self.session.commit()
        return True

    def delete(self, grade_id: int) -> bool:
        """
        Permanently deletes a Grade record by its ID.

        Args:
            grade_id (int): The unique identifier of the grade to delete.

        Returns:
            bool: True if the deletion was successful.
        """
        grade = self.get_by_id(grade_id)
        if grade:
            self.session.delete(grade)
            self.session.commit()
            return True
        return False
