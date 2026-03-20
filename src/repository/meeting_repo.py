from typing import List, Optional, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from core.models.meeting import Meeting
from data.database import db_manager


class MeetingRepository:
    """
    Repository responsible for persistence and retrieval of Meeting entities.

    This class handles the database interactions for supervisory meetings
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

    def get_all(self) -> List[Meeting]:
        """
        Retrieves all meetings stored in the database.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Meeting).order_by(Meeting.meeting_date.desc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_intern_id(self, intern_id: int) -> List[Meeting]:
        """
        Retrieves all meetings for a specific intern.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = (
                select(Meeting)
                .where(Meeting.intern_id == intern_id)
                .order_by(Meeting.meeting_date.desc())
            )
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """
        Retrieves a single meeting by its ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Meeting, meeting_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, meeting: Meeting) -> int:
        """
        Persists a new Meeting entity to the database.
        """
        if self._session:
            self._session.add(meeting)
            self._session.flush()
            return meeting.meeting_id

        with db_manager.session_scope() as session:
            session.add(meeting)
            session.flush()
            return meeting.meeting_id

    def update(self, meeting: Meeting) -> bool:
        """
        Updates an existing Meeting record.
        """
        if self._session:
            self._session.merge(meeting)
            return True

        with db_manager.session_scope() as session:
            session.merge(meeting)
            return True

    def delete(self, meeting_id: int) -> bool:
        """
        Permanently deletes a Meeting record by its ID.
        """
        if self._session:
            meeting = self._session.get(Meeting, meeting_id)
            if meeting:
                self._session.delete(meeting)
                return True
            return False

        with db_manager.session_scope() as session:
            meeting = session.get(Meeting, meeting_id)
            if meeting:
                session.delete(meeting)
                return True
            return False

    def count_this_month(self) -> int:
        """
        Counts meetings that occurred in the current calendar month.
        """
        session = self._session or db_manager.get_session()
        try:
            # SQLite strftime format: %m for month (01-12)
            current_month = func.strftime("%m", "now")
            current_year = func.strftime("%Y", "now")

            stmt = select(func.count(Meeting.meeting_id)).where(
                func.strftime("%m", Meeting.meeting_date) == current_month,
                func.strftime("%Y", Meeting.meeting_date) == current_year,
            )
            return session.scalar(stmt) or 0
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_intern_ids_with_meetings_this_month(self) -> List[int]:
        """
        Returns IDs of interns who participated in at least one meeting this month.
        """
        session = self._session or db_manager.get_session()
        try:
            current_month = func.strftime("%m", "now")
            current_year = func.strftime("%Y", "now")

            stmt = select(Meeting.intern_id).where(
                func.strftime("%m", Meeting.meeting_date) == current_month,
                func.strftime("%Y", Meeting.meeting_date) == current_year,
            )
            result = session.scalars(stmt).all()
            return list(set(result))
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_meetings_in_range(self, start_date: str, end_date: str) -> List[Meeting]:
        """
        Retrieves all meetings within a specific date range (ISO format).
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Meeting).where(
                Meeting.meeting_date.between(start_date, end_date)
            ).order_by(Meeting.meeting_date.asc())
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()
