from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.document import Document
from data.database import db_manager


class DocumentRepository:
    """
    Repository responsible for persistence and retrieval of Document entities.

    This class encapsulates database operations for the documents associated 
    with an Intern using SQLAlchemy 2.0.
    """

    def __init__(self, db: Any = None, session: Optional[Session] = None):
        """
        Initializes the repository.

        Args:
            db (Any): Legacy db connector (ignored but kept for compatibility).
            session (Optional[Session]): An active SQLAlchemy session.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Returns the active session or gets a new one from the manager."""
        return self._session or db_manager.get_session()

    def get_by_intern_id(self, intern_id: int) -> List[Document]:
        """
        Retrieves all documents associated with a specific intern.

        Args:
            intern_id (int): ID of the intern.

        Returns:
            List[Document]: List of document instances.
        """
        stmt = select(Document).where(Document.intern_id == intern_id)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieves a single document by its ID.

        Args:
            document_id (int): The primary key ID.

        Returns:
            Optional[Document]: The Document instance if found, otherwise None.
        """
        return self.session.get(Document, document_id)

    def save(self, document: Document) -> int:
        """
        Persists a new Document entity to the database.

        Args:
            document (Document): The document instance to save.

        Returns:
            int: The generated ID for the new document.
        """
        self.session.add(document)
        self.session.commit()
        return document.document_id

    def update(self, document: Document) -> bool:
        """
        Updates an existing Document record.

        Args:
            document (Document): The document instance with updated data.

        Returns:
            bool: True if the update was successful.
        """
        self.session.merge(document)
        self.session.commit()
        return True

    def delete(self, document_id: int) -> bool:
        """
        Deletes a document record by its ID.

        Args:
            document_id (int): The ID of the document to remove.

        Returns:
            bool: True if the deletion was successful.
        """
        doc = self.get_by_id(document_id)
        if doc:
            self.session.delete(doc)
            self.session.commit()
            return True
        return False

    def create_batch(self, documents: List[Document]):
        """
        Saves multiple Document entities in a single transaction.

        Args:
            documents (List[Document]): List of document instances to save.
        """
        try:
            self.session.add_all(documents)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
