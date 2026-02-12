from sqlite3 import Connection, Cursor
from data.database import DatabaseConnector
from core.models.document import Document
from typing import List, Optional


class DocumentRepository:
    def __init__(self, db: DatabaseConnector):
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_by_intern_id(self, intern_id: int) -> List[Document]:
        sql_query = "SELECT document_id, intern_id, document_name, status, feedback FROM documents WHERE intern_id = ?"
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()
        return [
            Document(
                document_id=row["document_id"],
                intern_id=row["intern_id"],
                document_name=row["document_name"],
                status=row["status"],
                feedback=row["feedback"],
            )
            for row in results
        ]

    def get_by_id(self, document_id: int) -> Optional[Document]:
        sql_query = "SELECT document_id, intern_id, document_name, status, feedback FROM documents WHERE document_id = ?"
        self.cursor.execute(sql_query, (document_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return Document(
            document_id=row["document_id"],
            intern_id=row["intern_id"],
            document_name=row["document_name"],
            status=row["status"],
            feedback=row["feedback"],
        )

    def count_pending(self) -> int:
        """Retorna o total de documentos com status = Pendente."""
        sql_query = "SELECT COUNT(*) FROM documents WHERE status = 'Pendente' "
        self.cursor.execute(sql_query)
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def save(self, document: Document) -> int:
        if document.document_id is not None:
            raise ValueError("Cannot save a document that already has an ID.")
        sql_query = "INSERT INTO documents (intern_id, document_name, status, feedback) VALUES (?, ?, ?, ?)"
        data = (
            document.intern_id,
            document.document_name,
            document.status,
            document.feedback,
        )
        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.lastrowid  # type: ignore

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

        # SQL direto usando o ID
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
