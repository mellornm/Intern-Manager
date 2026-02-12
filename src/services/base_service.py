from typing import Generic, TypeVar, Optional, Dict, Any
from utils.validations import validate_required_fields

T = TypeVar("T")  # Domain model (Intern, Venue, etc)


class BaseService(Generic[T]):
    """
    Base service class providing common CRUD validations and behavior.

    Concrete services should extend this class and implement
    entity-specific validation rules.

    Attributes:
        repo (Any): Repository instance for the specific entity.
        REQUIRED_FIELDS (Dict[str, str]): Dictionary mapping field names to human-readable names.
    """

    REQUIRED_FIELDS: Dict[str, str] = {}

    def __init__(self, repo: Any):
        """
        Initializes the service with a repository.

        Args:
            repo (Any): A repository instance that follows the standard interface.
        """
        self.repo = repo

    def _validate_required_fields(self, data: T) -> None:
        """
        Validates required fields defined by the concrete service.

        Args:
            data (T): The entity instance to validate.

        Raises:
            ValueError: If a required field is missing or empty.
        """
        if self.REQUIRED_FIELDS:
            validate_required_fields(data, self.REQUIRED_FIELDS)

    def _ensure_has_id(self, data: T, entity_name: str) -> None:
        """
        Ensures the entity has an ID before update or delete operations.

        Args:
            data (T): The entity instance to check.
            entity_name (str): The name of the entity (e.g., 'intern').

        Raises:
            ValueError: If the ID (entity_name_id) is None.
        """
        entity_id = getattr(data, f"{entity_name}_id", None)
        if entity_id is None:
            raise ValueError(
                f"{entity_name.capitalize()} has no ID and cannot be updated or deleted."
            )

    def get_all(self) -> Any:
        """
        Retrieves all records for the entity from the repository.

        Returns:
            List[T]: A list of all entity instances found.
        """
        return self.repo.get_all()

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Retrieves a single record by its unique ID.

        Args:
            entity_id (int): The unique identifier.

        Returns:
            Optional[T]: The entity instance if found, or None.
        """
        return self.repo.get_by_id(entity_id)

    def delete(self, data_or_id: Any, entity_name: str) -> bool:
        pk = 0
        print(
            f"DEBUG DELETE: Tentando deletar {entity_name}. Dado recebido: {data_or_id}"
        )  # ADD ISSO

        attr_name = f"{entity_name}_id"
        if hasattr(data_or_id, attr_name):
            pk = getattr(data_or_id, attr_name)
        elif isinstance(data_or_id, int):
            pk = data_or_id
        else:
            pk = getattr(data_or_id, "id", None)

        print(f"DEBUG DELETE: ID extraído = {pk}")

        if not pk:
            raise ValueError(
                f"Não foi possível encontrar um ID válido para deletar {entity_name}."
            )

        return self.repo.delete(pk)
