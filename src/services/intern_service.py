from services.base_service import BaseService
from utils.text_utils import smart_title
from core.models.intern import Intern
from repository.intern_repo import InternRepository
from utils.validations import (
    validate_email_format,
    validate_date_range,
    parse_date_to_iso,
)
from typing import Optional, List

REQUIRED_FIELDS = {
    "name": "Nome do Aluno",
    "registration_number": "RA",
    "term": "Semestre",
    "start_date": "Data de Início",
    "end_date": "Data de Encerramento",
}


class InternService(BaseService[Intern]):
    """
    Service class responsible for business logic related to interns.

    This service handles the lifecycle of Intern entities, including
    data normalization (dates), validation of business rules (unique RA,
    valid email formats), and interaction with the persistence layer.

    Attributes:
        repo (InternRepository): The repository for intern persistence.
        REQUIRED_FIELDS (Dict[str, str]): Mapping of required fields for validation.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: InternRepository):
        """
        Initializes the InternService with the specified repository.

        Args:
            repo (InternRepository): Repository for intern persistence.
        """
        super().__init__(repo)

    def _validate_common_intern_data(self, intern: Intern) -> None:
        """
        Performs common validations for intern data (required fields, email, dates).

        Validates that the date range is logical (start < end), that all
        mandatory fields are present, and that the email format is correct.

        Args:
            intern (Intern): The intern instance to be validated.

        Raises:
            ValueError: If validation fails.
        """
        validate_date_range(str(intern.start_date), str(intern.end_date))
        self._validate_required_fields(intern)
        if intern.email:
            validate_email_format(str(intern.email))

    def _normalize_intern_dates(self, intern_data: Intern) -> None:
        """
        Converts date strings from UI format to ISO format for database storage.

        Args:
            intern_data (Intern): The intern instance containing dates to normalize.

        Raises:
            ValueError: If start or end dates are missing/None at this stage.
            AssertionError: If dates are None (checked via assert statements).
        """
        if intern_data.start_date is None or intern_data.end_date is None:
            raise ValueError("Datas não podem ser nulas neste ponto do fluxo.")

        assert intern_data.start_date is not None
        assert intern_data.end_date is not None

        intern_data.start_date = parse_date_to_iso(intern_data.start_date)
        intern_data.end_date = parse_date_to_iso(intern_data.end_date)

    def get_by_name(self, name: str) -> Optional[Intern]:
        """
        Retrieves an intern by name (encapsulating the repository).

        Args:
            name (str): The name (or partial name) to search for.

        Returns:
            Optional[Intern]: The found intern or None.
        """
        return self.repo.get_by_name(name)

    def add_new_intern(self, intern: Intern):
        """
        Validates and adds a new intern to the system.

        Checks for duplicate Registration Numbers (RA) before proceeding with
        normalization and persistence.

        Args:
            intern (Intern): The intern instance to be added.

        Returns:
            int: The ID of the newly created intern.

        Raises:
            ValueError: If the RA is already in use by another intern.
        """
        if self.repo.get_by_registration_number(intern.registration_number):
            raise ValueError("RA já cadastrado.")

        intern.name = smart_title(intern.name)

        self._normalize_intern_dates(intern)
        self._validate_common_intern_data(intern)

        return self.repo.save(intern)

    def update_intern(self, intern: Intern):
        """
        Updates an existing intern record after validation.

        Ensures that if the RA is being changed, it does not conflict with
        an existing RA belonging to a different intern.

        Args:
            intern (Intern): The intern instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the RA belongs to another intern or validation fails.
        """
        self._ensure_has_id(intern, "intern")
        existing = self.repo.get_by_registration_number(intern.registration_number)
        if existing and existing.intern_id != intern.intern_id:
            raise ValueError("Este RA pertence a outro estagiário.")

        intern.name = smart_title(intern.name)

        self._validate_common_intern_data(intern)
        self._normalize_intern_dates(intern)

        return self.repo.update(intern)

    def delete_intern(self, intern: Intern):
        """
        Removes an intern from the system using the base service logic.

        Args:
            intern (Intern): The intern instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(intern, "intern")

    def get_all_interns(self) -> List[Intern]:
        """
        Returns a list of all interns registered in the system.
        Used by the UI to populate the table.

        Returns:
            List[Intern]: A list of all interns.
        """
        return self.repo.get_all()

    def get_by_id(self, entity_id: int) -> Optional[Intern]:
        """
        Retrieves a single intern by their unique ID.

        Args:
            entity_id (int): The unique identifier.

        Returns:
            Optional[Intern]: The intern object if found, None otherwise.
        """
        return self.repo.get_by_id(entity_id)
