from data.database import DatabaseConnector
from core.models.intern import Intern
from typing import Optional, List
from sqlite3 import Connection, Cursor, Row


class InternRepository:
    def __init__(self, db: DatabaseConnector):
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

        # GARANTIA: Força o modo de dicionário para não dependermos da ordem das colunas
        self.conn.row_factory = Row

    def _parse_row(self, row: Row) -> Intern:
        """Converte linha do banco para Objeto Intern de forma segura."""
        return Intern(
            intern_id=row["intern_id"],
            name=row["name"],
            registration_number=row["registration_number"],
            term=row["term"],
            email=row["email"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            working_days=row["working_days"],
            working_hours=row["working_hours"],
            venue_id=row["venue_id"],
        )

    def get_all(self) -> List[Intern]:
        # Selecionamos explicitamente para garantir que as colunas existam
        sql_query = """
        SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
        working_days, working_hours, venue_id FROM interns ORDER BY name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()
        return [self._parse_row(row) for row in results]

    def get_by_id(self, intern_id: int) -> Optional[Intern]:
        sql_query = """
        SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
        working_days, working_hours, venue_id FROM interns WHERE intern_id = ?
        """
        self.cursor.execute(sql_query, (intern_id,))
        row = self.cursor.fetchone()
        return self._parse_row(row) if row else None

    def get_by_registration_number(self, ra: str) -> Optional[Intern]:
        sql_query = """
        SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
        working_days, working_hours, venue_id FROM interns WHERE registration_number = ?
        """
        self.cursor.execute(sql_query, (ra,))
        row = self.cursor.fetchone()
        return self._parse_row(row) if row else None

    def save(self, intern: Intern) -> int:
        if intern.intern_id is not None:
            raise ValueError("Cannot save an intern that already has an ID.")

        # A ordem aqui deve bater EXATAMENTE com a ordem do 'data' abaixo
        sql_query = """
        INSERT INTO interns (
            name, registration_number, term, email, 
            start_date, end_date, working_days, working_hours, venue_id
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        data = (
            intern.name,
            intern.registration_number,
            intern.term,
            intern.email,
            intern.start_date,
            intern.end_date,
            intern.working_days,  # Confirme que isso é Dias
            intern.working_hours,  # Confirme que isso é Horas
            intern.venue_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID.")
        return self.cursor.lastrowid

    def update(self, intern: Intern) -> bool:
        if intern.intern_id is None:
            raise ValueError("Cannot update an intern without an ID.")

        sql_query = """
        UPDATE interns SET
            name = ?, registration_number = ?, term = ?, email = ?, 
            start_date = ?, end_date = ?, working_days = ?, working_hours = ?, 
            venue_id = ?, 
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE intern_id = ?
        """
        data = (
            intern.name,
            intern.registration_number,
            intern.term,
            intern.email,
            intern.start_date,
            intern.end_date,
            intern.working_days,
            intern.working_hours,
            intern.venue_id,
            intern.intern_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, intern_id: int) -> bool:
        if not intern_id:
            raise ValueError("ID inválido para deleção.")

        # SQL direto usando o ID
        sql_query = "DELETE FROM interns WHERE intern_id = ?"
        self.cursor.execute(sql_query, (intern_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
