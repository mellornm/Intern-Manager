from sqlite3 import Connection, Cursor
from typing import List, Optional

from core.models.evaluation_criteria import EvaluationCriteria
from data.database import DatabaseConnector


class EvaluationCriteriaRepository:
    """
    Repository responsible for persistence and retrieval of EvaluationCriteria entities.

    This class encapsulates database operations for the criteria used in intern
    evaluations (e.g., "Assiduity", "Technical Knowledge"). It maps directly
    to the `evaluation_criteria` table.

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

    def get_all(self) -> List[EvaluationCriteria]:
        """
        Retrieves all evaluation criteria stored in the database.

        Returns:
            List[EvaluationCriteria]: A list of all criteria objects.
        """
        sql_query = (
            "SELECT criteria_id, name, description, weight FROM evaluation_criteria"
        )
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        criteria_list = []
        for row in results:
            criteria = EvaluationCriteria.from_db_row(row)
            if criteria:
                criteria_list.append(criteria)
        return criteria_list

    def get_by_id(self, criteria_id: int) -> Optional[EvaluationCriteria]:
        """
        Retrieves a single evaluation criteria by its ID.

        Args:
            criteria_id (int): The unique identifier of the criteria.

        Returns:
            Optional[EvaluationCriteria]: The criteria object if found, otherwise None.
        """
        sql_query = "SELECT criteria_id, name, description, weight FROM evaluation_criteria WHERE criteria_id = ?"
        self.cursor.execute(sql_query, (criteria_id,))
        row = self.cursor.fetchone()

        return EvaluationCriteria.from_db_row(row)

    def save(self, criteria: EvaluationCriteria) -> int:
        """
        Persists a new EvaluationCriteria entity to the database.

        Args:
            criteria (EvaluationCriteria): The entity to be saved.

        Returns:
            int: The ID of the newly created criteria.

        Raises:
            ValueError: If the criteria object already has an ID.
            RuntimeError: If the database fails to return the new ID.
        """
        if criteria.criteria_id is not None:
            raise ValueError(
                "Cannot save a criteria that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO evaluation_criteria (name, description, weight)
        VALUES (?, ?, ?)
        """
        data = (criteria.name, criteria.description, criteria.weight)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError(
                "Database failed to generate an ID for the new criteria."
            )

        return self.cursor.lastrowid

    def update(self, criteria: EvaluationCriteria) -> bool:
        """
        Updates an existing EvaluationCriteria record.

        Args:
            criteria (EvaluationCriteria): The entity with updated data. Must have an ID.

        Returns:
            bool: True if the update was successful (row modified), False otherwise.

        Raises:
            ValueError: If the criteria object does not have an ID.
        """
        if criteria.criteria_id is None:
            raise ValueError("Cannot update a criteria without an ID.")

        sql_query = """
        UPDATE evaluation_criteria SET
            name = ?, description = ?, weight = ?,
            last_update = datetime('now', 'localtime')
        WHERE criteria_id = ?
        """
        data = (
            criteria.name,
            criteria.description,
            criteria.weight,
            criteria.criteria_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, criteria_id: int) -> bool:
        """
        Deletes an evaluation criteria record from the database by its ID.

        Args:
            criteria_id (int): The unique identifier of the criteria to delete.

        Returns:
            bool: True if the deletion was successful (one row deleted), False otherwise.

        Raises:
            ValueError: If an invalid or non-positive criteria_id is provided.
        """
        if not criteria_id:
            raise ValueError("ID inválido para deleção.")

        sql_query = "DELETE FROM evaluation_criteria WHERE criteria_id = ?"
        self.cursor.execute(sql_query, (criteria_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
