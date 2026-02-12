from data.database import DatabaseConnector
from core.models.meeting import Meeting
from typing import List
from sqlite3 import Connection, Cursor


class MeetingRepository:
    def __init__(self, db: DatabaseConnector):
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_all(self) -> List[Meeting]:
        sql_query = "SELECT * FROM meetings ORDER BY meeting_date DESC"
        self.cursor.execute(sql_query)
        rows = self.cursor.fetchall()
        return [self._parse_row(row) for row in rows]

    def get_by_intern_id(self, intern_id: int) -> List[Meeting]:
        """
        Busca todas as reuniões de um estagiário específico.
        """
        sql_query = (
            "SELECT * FROM meetings WHERE intern_id = ? ORDER BY meeting_date DESC"
        )
        self.cursor.execute(sql_query, (intern_id,))
        rows = self.cursor.fetchall()
        return [self._parse_row(row) for row in rows]

    # Alias para compatibilidade
    get_by_intern = get_by_intern_id

    def save(self, meeting: Meeting) -> int:
        if meeting.meeting_id is not None:
            raise ValueError(
                "Cannot save a meeting that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO meetings (intern_id, meeting_date, is_intern_present)
        VALUES (?, ?, ?)
        """
        # Converte True/False para 1/0
        present_int = 1 if meeting.is_intern_present else 0

        data = (meeting.intern_id, meeting.meeting_date, present_int)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new meeting.")
        return self.cursor.lastrowid

    def delete(self, meeting_id: int) -> bool:
        if not meeting_id:
            raise ValueError("ID inválido para deleção.")

        # SQL direto usando o ID
        sql_query = "DELETE FROM meetings WHERE meeting_id = ?"
        self.cursor.execute(sql_query, (meeting_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def _parse_row(self, row) -> Meeting:
        return Meeting(
            meeting_id=row[0],
            intern_id=row[1],
            meeting_date=row[2],
            is_intern_present=bool(row[3]),
        )
