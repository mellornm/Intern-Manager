from sqlite3 import Connection, Cursor
from typing import List

from core.models.visit import Visit
from data.database import DatabaseConnector


class VisitRepository:
    def __init__(self, db: DatabaseConnector):
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )

        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_all(self) -> List[Visit]:
        sql_query = "SELECT visit_id, intern_id, venue_id, visit_date, observation, photo_path FROM visits ORDER BY visit_date DESC"
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        visits = []
        for row in results:
            visit = Visit.from_db_row(row)
            if visit:
                visits.append(visit)
        return visits

    def get_by_intern_id(self, intern_id: int) -> List[Visit]:
        sql_query = "SELECT visit_id, intern_id, venue_id, visit_date, observation, photo_path FROM visits WHERE intern_id = ? ORDER BY visit_date DESC"
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        visits = []
        for row in results:
            visit = Visit.from_db_row(row)
            if visit:
                visits.append(visit)
        return visits

    get_by_intern = get_by_intern_id

    def save(self, visit: Visit) -> int:
        if visit.visit_id is not None:
            raise ValueError(
                "Cannot save a visit that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO visits (intern_id, venue_id, visit_date, observation, photo_path)
        VALUES (?, ?, ?, ?, ?)
        """

        data = (
            visit.intern_id,
            visit.venue_id,
            visit.visit_date,
            visit.observation,
            visit.photo_path,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new visit.")
        return self.cursor.lastrowid

    def update(self, visit: Visit) -> bool:
        if visit.visit_id is None:
            raise ValueError("Cannot update a visit without ID.")

        sql_query = """
        UPDATE visits SET
        intern_id = ?, 
        venue_id = ?, 
        visit_date = ?, 
        observation = ?, 
        photo_path = ?
        WHERE visit_id = ?
        """

        data = (
            visit.intern_id,
            visit.venue_id,
            visit.visit_date,
            visit.observation,
            visit.photo_path,
            visit.visit_id,  # <--- IMPORTANTE: O ID entra aqui no final
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0
