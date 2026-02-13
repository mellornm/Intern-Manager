from data.database import DatabaseConnector
from core.models.observation import Observation
from typing import Optional, List
from sqlite3 import Connection, Cursor


class ObservationRepository:
    """
    Repository responsible for persistence and retrieval of Observation entities.

    This class provides an interface to the `observations` table, allowing
    the management of free-text notes associated with interns.

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

    def get_all(self) -> List[Observation]:
        """
        Retrieves all observations stored in the database.

        The results are ordered by the last update timestamp in descending order,
        showing the most recent notes first.

        Returns:
            List[Observation]: A list of all Observation objects.
        """
        sql_query = "SELECT observation_id, intern_id, observation, last_update FROM observations ORDER BY last_update DESC"
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        observations = []
        for row in results:
            obs = Observation.from_db_row(row)
            if obs:
                observations.append(obs)
        return observations

    def get_by_intern_id(self, intern_id: int) -> List[Observation]:
        """
        Retrieves all observations associated with a specific intern.

        Args:
            intern_id (int): The ID of the intern.

        Returns:
            List[Observation]: A list of Observation objects for that intern.
        """
        sql_query = "SELECT observation_id, intern_id, observation, last_update FROM observations WHERE intern_id = ? ORDER BY last_update DESC"
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        observations = []
        for row in results:
            obs = Observation.from_db_row(row)
            if obs:
                observations.append(obs)
        return observations

    def get_by_id(self, observation_id: int) -> Optional[Observation]:
        """
        Retrieves a single observation by its ID.

        Args:
            observation_id (int): The unique identifier.

        Returns:
            Optional[Observation]: The Observation object if found, otherwise None.
        """
        sql_query = "SELECT observation_id, intern_id, observation, last_update FROM observations WHERE observation_id = ?"
        self.cursor.execute(sql_query, (observation_id,))
        row = self.cursor.fetchone()

        return Observation.from_db_row(row)

    def save(self, observation: Observation) -> int:
        """
        Persists a new Observation entity to the database.

        Args:
            observation (Observation): The entity to be saved.

        Returns:
            int: The ID of the newly created observation.

        Raises:
            ValueError: If the observation object already has an ID.
            RuntimeError: If the database fails to return the new ID.
        """
        if observation.observation_id is not None:
            raise ValueError(
                "Cannot save an observation that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO observations (intern_id, observation)
        VALUES (?, ?)
        """
        data = (observation.intern_id, observation.observation)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError(
                "Database failed to generate an ID for the new observation."
            )
        return self.cursor.lastrowid

    def update(self, observation: Observation) -> bool:
        """
        Updates an existing Observation record in the database.

        Updates the text content and automatically refreshes the `last_update`
        timestamp using SQLite's local time function.

        Args:
            observation (Observation): The entity with updated data. Must have an ID.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the observation object does not have an ID.
        """
        if observation.observation_id is None:
            raise ValueError("Cannot update an observation without an ID.")

        sql_query = """
        UPDATE observations SET
            observation = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE observation_id = ?
        """

        data = (
            observation.observation,
            observation.observation_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, observation_id: int) -> bool:
        """
        Permanently deletes an Observation record by its ID.

        Args:
            observation_id (int): The unique identifier of the observation.

        Returns:
            bool: True if the deletion was successful.

        Raises:
            ValueError: If the observation_id is invalid.
        """
        if not observation_id:
            raise ValueError("ID inválido para deleção.")

        # SQL direto usando o ID
        sql_query = "DELETE FROM observations WHERE observation_id = ?"
        self.cursor.execute(sql_query, (observation_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
