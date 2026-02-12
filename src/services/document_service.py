from core.constants import DEFAULT_DOCUMENTS_LIST
from core.models.document import Document
from repository.document_repo import DocumentRepository
from services.base_service import BaseService

REQUIRED_FIELDS = {
    "document_name": "Nome do Documento",
    "intern_id": "ID do Estagiário",
}


class DocumentService(BaseService[Document]):
    """
    Service layer for managing Document entities.

    This class provides business logic for document-related operations,
    including validation, creation of default document sets for interns,
    and interaction with the DocumentRepository.

    Inherits from BaseService, providing common CRUD operations.

    Attributes:
        REQUIRED_FIELDS (dict): A dictionary defining required fields for a Document, used for validation.
        repo (DocumentRepository): The repository instance for database interaction.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: DocumentRepository):
        super().__init__(repo)

    def add_new_document(self, document: Document):
        """
        Adds a new document to the database after validating its required fields.

        Args:
            document (Document): The Document object to be saved.

        Returns:
            Any: The result of the repository's save operation, typically the ID of the new document.
        """
        self._validate_required_fields(document)
        return self.repo.save(document)

    def update_document(self, document: Document):
        """
        Updates an existing document in the database after validating its required fields.

        Ensures the document has an ID before proceeding with the update.

        Args:
            document (Document): The Document object with updated data. Must have its ID set.

        Returns:
            bool: True if the update was successful (one row modified), False otherwise.
        """
        self._ensure_has_id(document, "document")
        self._validate_required_fields(document)
        return self.repo.update(document)

    def delete_document(self, document: Document):
        return self.delete(document, "document")

    def get_documents_by_intern(self, intern_id: int):
        return self.repo.get_by_intern_id(intern_id)

    def get_document_by_id(self, doc_id: int):
        return self.repo.get_by_id(doc_id)

    def create_initial_documents_batch(self, intern_id: int):
        existing = self.repo.get_by_intern_id(intern_id)
        if existing:
            return

        docs_to_create = []
        for name in DEFAULT_DOCUMENTS_LIST:
            docs_to_create.append(
                Document(intern_id=intern_id, document_name=name, status="Pendente")
            )

        self.repo.create_batch(docs_to_create)

    def count_total_pending(self) -> int:
        return self.repo.count_pending()
