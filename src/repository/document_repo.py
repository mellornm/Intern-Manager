from typing import List, Optional, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from core.models.document import Document
from data.database import db_manager


class DocumentRepository:
    """
    Repository responsible for persistence and retrieval of Document entities.

    This class encapsulates database operations for the documents associated
    with an Intern using SQLAlchemy 2.0 with managed session lifecycle.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    def get_by_intern_id(self, intern_id: int) -> List[Document]:
        """
        Retrieves all documents associated with a specific intern.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Document).where(Document.intern_id == intern_id)
            return list(session.scalars(stmt).all())
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieves a single document by its ID.
        """
        session = self._session or db_manager.get_session()
        try:
            return session.get(Document, document_id)
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def save(self, document: Document) -> int:
        """
        Persists a new Document entity to the database.
        """
        if self._session:
            self._session.add(document)
            self._session.flush()
            return document.document_id

        with db_manager.session_scope() as session:
            session.add(document)
            session.flush()
            return document.document_id

    def update(self, document: Document) -> bool:
        """
        Updates an existing Document record.
        """
        if self._session:
            self._session.merge(document)
            return True

        with db_manager.session_scope() as session:
            session.merge(document)
            return True

    def delete(self, document_id: int) -> bool:
        """
        Deletes a document record by its ID.
        """
        if self._session:
            doc = self._session.get(Document, document_id)
            if doc:
                self._session.delete(doc)
                return True
            return False

        with db_manager.session_scope() as session:
            doc = session.get(Document, document_id)
            if doc:
                session.delete(doc)
                return True
            return False

    def create_batch(self, documents: List[Document]):
        """
        Saves multiple Document entities in a single transaction.
        """
        if self._session:
            self._session.add_all(documents)
            return

        with db_manager.session_scope() as session:
            session.add_all(documents)

    def count_pending(self) -> int:
        """
        Counts the total number of documents that are not in 'Aprovado' status.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(func.count(Document.document_id)).where(
                Document.status != "Aprovado"
            )
            return session.scalar(stmt) or 0
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()

    def get_intern_ids_with_pending_docs(self, document_name: Optional[str] = None) -> List[int]:
        """
        Identifies all interns who have at least one document that is not 'Aprovado'.
        Can be filtered by a specific document name.
        """
        session = self._session or db_manager.get_session()
        try:
            stmt = select(Document.intern_id).where(Document.status != "Aprovado")
            if document_name and document_name != "Todos":
                stmt = stmt.where(Document.document_name.like(f"%{document_name}%"))
            
            # Use set to avoid duplicates and return as list
            result = session.scalars(stmt).all()
            return list(set(result))
        finally:
            if self._session is None:
                db_manager.SessionLocal.remove()
