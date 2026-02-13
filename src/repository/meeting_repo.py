from data.database import DatabaseConnector
from core.models.meeting import Meeting
from typing import Optional, List
from sqlite3 import Connection, Cursor


class MeetingRepository:
    """
    Repository responsible for persistence and retrieval of Meeting entities.

    This class handles the database interactions for supervisory meetings,
    tracking attendance and dates. It maps directly to the `meetings` table.

    Attributes:
        db (DatabaseConnector): The database connector instance.
        conn (Connection): Active SQLite connection.
        cursor (Cursor): Active SQLite cursor.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the repository with an active database connection.

        Args:
            db (DatabaseConnector): An initialized connector with an open connection.

        Raises:
            RuntimeError: If the connector does not hold a valid connection or cursor.
        """
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_all(self) -> List[Meeting]:
        """
        Retrieves all meetings stored in the database.

        Results are ordered by date in descending order (newest first).

        Returns:
            List[Meeting]: A list of all Meeting objects.
        """
        sql_query = "SELECT meeting_id, intern_id, meeting_date, is_intern_present FROM meetings ORDER BY meeting_date DESC"
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        meetings = []
        for row in results:
            meeting = Meeting.from_db_row(row)
            if meeting:
                meetings.append(meeting)
        return meetings

    def get_by_intern_id(self, intern_id: int) -> List[Meeting]:
        """
        Retrieves all meetings for a specific intern.

        Args:
            intern_id (int): The ID of the intern.

        Returns:
            List[Meeting]: A list of Meeting objects for that intern.
        """
        sql_query = "SELECT meeting_id, intern_id, meeting_date, is_intern_present FROM meetings WHERE intern_id = ? ORDER BY meeting_date DESC"
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        meetings = []
        for row in results:
            meeting = Meeting.from_db_row(row)
            if meeting:
                meetings.append(meeting)
        return meetings

    get_by_intern = get_by_intern_id

    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """
        Retrieves a single meeting by its ID.

        Args:
            meeting_id (int): The unique identifier.

        Returns:
            Optional[Meeting]: The Meeting object if found, otherwise None.
        """
        sql_query = "SELECT meeting_id, intern_id, meeting_date, is_intern_present FROM meetings WHERE meeting_id = ?"
        self.cursor.execute(sql_query, (meeting_id,))
        row = self.cursor.fetchone()

        return Meeting.from_db_row(row)

    def save(self, meeting: Meeting) -> int:
        """
        Persists a new Meeting entity to the database.

        Args:
            meeting (Meeting): The entity to be saved.

        Returns:
            int: The ID of the newly created meeting.

        Raises:
            ValueError: If the meeting object already has an ID.
            RuntimeError: If the database fails to return the new ID.
        """
        if meeting.meeting_id is not None:
            raise ValueError(
                "Cannot save a meeting that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO meetings (intern_id, meeting_date, is_intern_present)
        VALUES (?, ?, ?)
        """
        # Converts True/False to 1/0 for SQLite
        present_int = 1 if meeting.is_intern_present else 0

        data = (meeting.intern_id, meeting.meeting_date, present_int)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new meeting.")
        return self.cursor.lastrowid

    def delete(self, meeting_id: int) -> bool:
        """
        Permanently deletes a Meeting record by its ID.

        Args:
            meeting_id (int): The unique identifier of the meeting.

        Returns:
            bool: True if the deletion was successful.

        Raises:
            ValueError: If the meeting_id is invalid.
        """
        if not meeting_id:
            raise ValueError("ID inválido para deleção.")

        # SQL direto usando o ID
        sql_query = "DELETE FROM meetings WHERE meeting_id = ?"
        self.cursor.execute(sql_query, (meeting_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update(self, meeting: Meeting) -> bool:
        """
        Atualiza um Meeting existente.

        Args:
            meeting (Meeting): Entidade com meeting_id preenchido.

        Returns:
            bool: True se alguma linha foi atualizada.
        """
        if meeting.meeting_id is None:
            raise ValueError("Não é possível atualizar um meeting sem ID.")

        sql_query = """
        UPDATE meetings
        SET intern_id = ?, meeting_date = ?, is_intern_present = ?
        WHERE meeting_id = ?
        """
        present_int = 1 if meeting.is_intern_present else 0
        data = (
            meeting.intern_id,
            meeting.meeting_date,
            present_int,
            meeting.meeting_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0
