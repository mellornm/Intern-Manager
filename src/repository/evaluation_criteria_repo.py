from data.database import DatabaseConnector
from core.models.evaluation_criteria import EvaluationCriteria
from typing import Optional, List
from sqlite3 import Connection, Cursor


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

        The results are ordered alphabetically by the criteria name to facilitate
        UI rendering.

        Returns:
            List[EvaluationCriteria]: A list of all available criteria.
        """
        sql_query = """
        SELECT criteria_id, name, description, weight
        FROM evaluation_criteria
        ORDER BY name ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [
            EvaluationCriteria(
                criteria_id=row["criteria_id"],
                name=row["name"],
                description=row["description"],
                weight=row["weight"],
            )
            for row in results
        ]

    def get_by_id(self, criteria_id: int) -> Optional[EvaluationCriteria]:
        """
        Retrieves a single criteria by its unique database identifier.

        Args:
            criteria_id (int): The unique identifier of the criteria.

        Returns:
            Optional[EvaluationCriteria]: The criteria object if found, otherwise None.
        """
        sql_query = """
        SELECT criteria_id, name, description, weight
        FROM evaluation_criteria
        WHERE criteria_id = ?
        """
        self.cursor.execute(sql_query, (criteria_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return EvaluationCriteria(
            criteria_id=row["criteria_id"],
            name=row["name"],
            description=row["description"],
            weight=row["weight"],
        )

    def save(self, criteria: EvaluationCriteria) -> int:
        """
        Persists a new EvaluationCriteria entity.

        Args:
            criteria (EvaluationCriteria): The entity to save. Must not have an ID yet.

        Returns:
            int: The unique identifier (primary key) of the newly created record.

        Raises:
            ValueError: If the criteria object already has an assigned ID.
            RuntimeError: If the database fails to return the last row ID.
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
            name = ?, description = ?, weight = ?
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
        if not criteria_id:
            raise ValueError("ID inválido para deleção.")

        # SQL direto usando o ID
        sql_query = "DELETE FROM evaluation_criteria WHERE criteria_id = ?"
        self.cursor.execute(sql_query, (criteria_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
