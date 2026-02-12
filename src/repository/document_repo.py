from sqlite3 import Connection, Cursor
from data.database import DatabaseConnector
from core.models.document import Document
from typing import List, Optional


class DocumentRepository:
    """
    Repository responsible for persistence and retrieval of Document entities.

    This class encapsulates database operations for the documents associated with an Intern.
    It maps directly to the `documents` table.

    Attributes:
        db (DatabaseConnector): The database connector instance.
        conn (Connection): Active SQLite connection.
        cursor (Cursor): Active SQLite cursor.
    """

    def __init__(self, db: DatabaseConnector):
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_by_intern_id(self, intern_id: int) -> List[Document]:
        sql_query = """
        SELECT document_id, intern_id, document_name, status, feedback, last_update 
        FROM documents 
        WHERE intern_id = ?
        """
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        documents = []
        for row in results:
            doc = Document.from_db_row(row)
            if doc:
                documents.append(doc)
        return documents

    def get_by_id(self, document_id: int) -> Optional[Document]:
        sql_query = """
        SELECT document_id, intern_id, document_name, status, feedback, last_update 
        FROM documents 
        WHERE document_id = ?
        """
        self.cursor.execute(sql_query, (document_id,))
        row = self.cursor.fetchone()

        return Document.from_db_row(row)

    def save(self, document: Document) -> int:
        if document.document_id is not None:
            raise ValueError(
                "Cannot save a document that already has an ID. Use update instead."
            )

        sql_query = """
            INSERT INTO documents (intern_id, document_name, status, feedback) 
            VALUES (?, ?, ?, ?)
        """
        data = (
            document.intern_id,
            document.document_name,
            document.status,
            document.feedback,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID.")
        return self.cursor.lastrowid

    def update(self, document: Document) -> bool:
        if document.document_id is None:
            raise ValueError("Cannot update a document without an ID.")

        sql_query = """
                UPDATE documents 
                SET document_name = ?, 
                    status = ?, 
                    feedback = ?, 
                    last_update = datetime('now', 'localtime') 
                WHERE document_id = ?
            """

        data = (
            document.document_name,
            document.status,
            document.feedback,
            document.document_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, document_id: int) -> bool:
        if not document_id:
            raise ValueError("ID inválido para deleção.")

        sql_query = "DELETE FROM documents WHERE document_id = ?"
        self.cursor.execute(sql_query, (document_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def create_batch(self, documents: List[Document]):
        query = "INSERT INTO documents (intern_id, document_name, status, feedback) VALUES (?, ?, ?, ?)"
        data = [
            (doc.intern_id, doc.document_name, doc.status, doc.feedback)
            for doc in documents
        ]
        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
