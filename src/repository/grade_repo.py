from data.database import DatabaseConnector
from core.models.grade import Grade
from typing import Optional, List
from sqlite3 import Connection, Cursor


class GradeRepository:
    """
    Repository responsible for persistence and retrieval of Grade entities.

    This class manages the specific grades assigned to interns based on
    evaluation criteria. It maps directly to the `grades` table.

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

    def get_all(self) -> List[Grade]:
        """
        Retrieves all grades stored in the database.

        The results are ordered by the last update timestamp in descending order.

        Returns:
            List[Grade]: A list of all recorded grades.
        """
        sql_query = """
        SELECT grade_id, intern_id, criteria_id, value, last_update
        FROM grades
        ORDER BY last_update DESC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [
            Grade(
                grade_id=row["grade_id"],
                intern_id=row["intern_id"],
                criteria_id=row["criteria_id"],
                value=row["value"],
                last_update=row["last_update"],
            )
            for row in results
        ]

    def get_by_intern_id(self, intern_id: int) -> List[Grade]:
        """
        Retrieves all grades for a specific intern (The Report Card).

        Args:
            intern_id (int): The unique identifier of the intern.

        Returns:
            List[Grade]: A list of Grade objects associated with the intern,
            ordered by criteria ID.
        """
        sql_query = """
        SELECT grade_id, intern_id, criteria_id, value, last_update
        FROM grades
        WHERE intern_id = ?
        ORDER BY criteria_id ASC
        """
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        return [
            Grade(
                grade_id=row["grade_id"],
                intern_id=row["intern_id"],
                criteria_id=row["criteria_id"],
                value=row["value"],
                last_update=row["last_update"],
            )
            for row in results
        ]

    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        """
        Retrieves a grade by its unique database identifier.

        Args:
            grade_id (int): The unique identifier of the grade.

        Returns:
            Optional[Grade]: The Grade object if found, otherwise None.
        """
        sql_query = """
        SELECT grade_id, intern_id, criteria_id, value, last_update
        FROM grades
        WHERE grade_id = ?
        """
        self.cursor.execute(sql_query, (grade_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Grade(
            grade_id=row["grade_id"],
            intern_id=row["intern_id"],
            criteria_id=row["criteria_id"],
            value=row["value"],
            last_update=row["last_update"],
        )

    def save(self, grade: Grade) -> int:
        """
        Persists a new Grade entity.

        Args:
            grade (Grade): The grade entity to save. Must not have an ID yet.

        Returns:
            int: The unique identifier (primary key) of the newly created record.

        Raises:
            ValueError: If the grade object already has an assigned ID.
            RuntimeError: If the database fails to generate an ID.
            sqlite3.IntegrityError: If a duplicate (intern_id, criteria_id) exists.
        """
        if grade.grade_id is not None:
            raise ValueError(
                "Cannot save a grade that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO grades (intern_id, criteria_id, value)
        VALUES (?, ?, ?)
        """
        data = (grade.intern_id, grade.criteria_id, grade.value)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new grade.")

        return self.cursor.lastrowid

    def update(self, grade: Grade) -> bool:
        """
        Updates an existing Grade record.

        Updates the value and automatically sets `last_update` to the current
        local time via SQLite's strftime.

        Args:
            grade (Grade): The grade entity with updated data. Must have an ID.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the grade object does not have an ID.
        """
        if grade.grade_id is None:
            raise ValueError("Cannot update a grade without an ID.")

        sql_query = """
        UPDATE grades SET
            value = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE grade_id = ?
        """

        data = (grade.value, grade.grade_id)

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, grade_id: int) -> bool:
        if not grade_id:
            raise ValueError("ID inválido para deleção.")

        # SQL direto usando o ID
        sql_query = "DELETE FROM grades WHERE grade_id = ?"
        self.cursor.execute(sql_query, (grade_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
