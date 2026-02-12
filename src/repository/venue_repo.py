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
        SELECT venue_id, venue_name, address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues 
        ORDER BY venue_name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        venues = []
        for row in results:
            venues.append(
                Venue(
                    venue_id=row["venue_id"],
                    venue_name=row["venue_name"],
                    venue_address=row["address"],
                    supervisor_name=row["supervisor_name"],
                    supervisor_email=row["supervisor_email"],
                    supervisor_phone=row["supervisor_phone"],
                )
            )
        return venues

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        """
        Retrieves a venue by its unique database identifier.

        Args:
            venue_id (int): Unique identifier of the venue.

        Returns:
            Optional[Venue]: The Venue object if found, or None otherwise.
        """
        sql_query = """
        SELECT venue_id, venue_name, address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues WHERE venue_id = ?
        """
        self.cursor.execute(sql_query, (venue_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Venue(
            venue_id=row["venue_id"],
            venue_name=row["venue_name"],
            venue_address=row["address"],
            supervisor_name=row["supervisor_name"],
            supervisor_email=row["supervisor_email"],
            supervisor_phone=row["supervisor_phone"],
        )

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Retrieves the first venue whose name partially matches the given value.

        Args:
            name (str): Partial or full name of the venue.

        Returns:
            Optional[Venue]: The first matching Venue object, or None.
        """
        sql_query = """
        SELECT venue_id, venue_name, address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues WHERE venue_name LIKE ?
        ORDER BY venue_name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query, (f"%{name}%",))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Venue(
            venue_id=row["venue_id"],
            venue_name=row["venue_name"],
            venue_address=row["address"],
            supervisor_name=row["supervisor_name"],
            supervisor_email=row["supervisor_email"],
            supervisor_phone=row["supervisor_phone"],
        )

    def save(self, venue: Venue) -> Optional[int]:
        """
        Persists a new Venue entity in the database.

        Args:
            venue (Venue): Venue entity to be persisted.

        Returns:
            Optional[int]: The generated database ID, or None if it already has one.
        """
        if venue.venue_id is not None:
            raise ValueError(
                "Cannot save a Venue that already has an ID. Use update insteade."
            )

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

        # SQL direto usando o ID
        sql_query = "DELETE FROM venues WHERE venue_id = ?"
        self.cursor.execute(sql_query, (venue_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
