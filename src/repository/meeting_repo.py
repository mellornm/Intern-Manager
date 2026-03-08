from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.meeting import Meeting
from data.database import db_manager


class MeetingRepository:
    """
    Repository responsible for persistence and retrieval of Meeting entities.

    This class handles the database interactions for supervisory meetings
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

    def get_all(self) -> List[Meeting]:
        """
        Retrieves all meetings stored in the database.

        Results are ordered by date in descending order.

        Returns:
            List[Meeting]: A list of all Meeting model instances.
        """
        stmt = select(Meeting).order_by(Meeting.meeting_date.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_intern_id(self, intern_id: int) -> List[Meeting]:
        """
        Retrieves all meetings for a specific intern.

        Args:
            intern_id (int): The ID of the intern.

        Returns:
            List[Meeting]: A list of Meeting instances for that intern.
        """
        stmt = (
            select(Meeting)
            .where(Meeting.intern_id == intern_id)
            .order_by(Meeting.meeting_date.desc())
        )
        return list(self.session.scalars(stmt).all())

    # Keep alias for compatibility
    get_by_intern = get_by_intern_id

    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """
        Retrieves a single meeting by its ID.

        Args:
            meeting_id (int): The unique identifier.

        Returns:
            Optional[Meeting]: The Meeting instance if found, otherwise None.
        """
        return self.session.get(Meeting, meeting_id)

    def save(self, meeting: Meeting) -> int:
        """
        Persists a new Meeting entity to the database.

        Args:
            meeting (Meeting): The entity to be saved.

        Returns:
            int: The generated ID for the new meeting.
        """
        self.session.add(meeting)
        self.session.commit()
        return meeting.meeting_id

    def update(self, meeting: Meeting) -> bool:
        """
        Updates an existing Meeting record.

        Args:
            meeting (Meeting): The meeting instance with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(meeting)
        self.session.commit()
        return True

    def delete(self, meeting_id: int) -> bool:
        """
        Permanently deletes a Meeting record by its ID.

        Args:
            meeting_id (int): The unique identifier of the meeting.

        Returns:
            bool: True if the deletion was successful.
        """
        meeting = self.get_by_id(meeting_id)
        if meeting:
            self.session.delete(meeting)
            self.session.commit()
            return True
        return False
