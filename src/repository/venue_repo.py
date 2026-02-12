from data.database import DatabaseConnector
from core.models.venue import Venue
from typing import Optional, List
from sqlite3 import Connection, Cursor


class VenueRepository:
    """
    Repository responsible for persistence and retrieval of Venue entities.

    This class implements the Repository pattern, encapsulating all direct
    database access related to the `Venue` domain model.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the VenueRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                SQLite connection and cursor.
        """
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_all(self) -> List[Venue]:
        """
        Retrieves all venues stored in the database.

        Returns:
            List[Venue]: A list of Venue objects ordered by name.
        """
        sql_query = """
        SELECT venue_id, venue_name, address as venue_address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues 
        ORDER BY venue_name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        venues = []
        for row in results:
            venue = Venue.from_db_row(row)
            if venue:
                venues.append(venue)
        return venues

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        """
        Retrieves a single venue by its ID.

        Args:
            venue_id (int): The unique identifier of the venue.

        Returns:
            Optional[Venue]: The Venue object if found, otherwise None.
        """
        sql_query = """
        SELECT venue_id, venue_name, address as venue_address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues 
        WHERE venue_id = ?
        """
        self.cursor.execute(sql_query, (venue_id,))
        row = self.cursor.fetchone()

        return Venue.from_db_row(row)

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Retrieves a single venue by its name.

        Args:
            name (str): The name of the venue.

        Returns:
            Optional[Venue]: The Venue object if found, otherwise None.
        """
        sql_query = """
        SELECT venue_id, venue_name, address as venue_address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues 
        WHERE venue_name = ?
        """
        self.cursor.execute(sql_query, (name,))
        row = self.cursor.fetchone()

        return Venue.from_db_row(row)

    def save(self, venue: Venue) -> int:
        """
        Persists a new Venue entity to the database.

        Args:
            venue (Venue): The venue object to be saved.

        Returns:
            int: The ID of the newly created venue.

        Raises:
            ValueError: If the venue already has an ID (use update instead).
        """
        if venue.venue_id is not None:
            raise ValueError("Cannot save a Venue that already has an ID.")

        sql_query = """
        INSERT INTO venues (venue_name, address, supervisor_name, supervisor_email, supervisor_phone)
        VALUES (?, ?, ?, ?, ?)
        """
        data = (
            venue.venue_name,
            venue.venue_address,
            venue.supervisor_name,
            venue.supervisor_email,
            venue.supervisor_phone,
        )
        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID.")

        return self.cursor.lastrowid

    def update(self, venue: Venue) -> bool:
        """
        Updates an existing Venue record.

        Args:
            venue (Venue): Venue entity with updated data.

        Returns:
            bool: True if the update was successful.
        """

        if venue.venue_id is None:
            raise ValueError("Cannot update a Venue without an ID.")

        sql_query = """
        UPDATE venues SET
            venue_name = ?, address = ?, supervisor_name = ?, supervisor_email = ?, 
            supervisor_phone = ?, 
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE venue_id = ?
        """
        data = (
            venue.venue_name,
            venue.venue_address,
            venue.supervisor_name,
            venue.supervisor_email,
            venue.supervisor_phone,
            venue.venue_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, venue_id: int) -> bool:
        if not venue_id:
            raise ValueError("ID inválido para deleção.")

        sql_query = "DELETE FROM venues WHERE venue_id = ?"
        self.cursor.execute(sql_query, (venue_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
