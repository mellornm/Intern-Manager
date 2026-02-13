from services.base_service import BaseService
from core.models.evaluation_criteria import EvaluationCriteria
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository


REQUIRED_FIELDS = {
    "name": "Nome do Critério",
    "weight": "Peso da Nota",
}


class EvaluationCriteriaService(BaseService[EvaluationCriteria]):
    """
    Service class responsible for business logic related to evaluation criteria.

    This service ensures that grading criteria meet specific business rules,
    such as having a valid name and a positive numerical weight.

    Attributes:
        repo (EvaluationCriteriaRepository): The repository for criteria persistence.
    """

    def __init__(self, repo: EvaluationCriteriaRepository):
        """
        Initializes the service with the specific repository.

        Args:
            repo (EvaluationCriteriaRepository): Repository for criteria persistence.
        """
        super().__init__(repo)

    def _validate_weight(self, criteria: EvaluationCriteria):
        """
        Ensures the weight is a positive number.

        Args:
            criteria (EvaluationCriteria): The criteria to validate.

        Raises:
            ValueError: If the weight is less than or equal to zero.
        """
        if criteria.weight <= 0:
            raise ValueError("O peso do critério deve ser maior que zero.")

    def add_new_criteria(self, criteria: EvaluationCriteria) -> int:
        """
        Validates and adds a new evaluation criteria to the system.

        Args:
            criteria (EvaluationCriteria): The criteria instance to be added.

        Returns:
            int: The ID of the newly created criteria.

        Raises:
            ValueError: If required fields are missing or weight is invalid.
        """

        self._validate_required_fields(criteria)

        self._validate_weight(criteria)

        return self.repo.save(criteria)

    def update_criteria(self, criteria: EvaluationCriteria) -> bool:
        """
        Updates an existing criteria after ensuring it has a valid ID.

        Args:
            criteria (EvaluationCriteria): The criteria instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If ID is missing, fields are missing, or weight is invalid.
        """
        self._ensure_has_id(criteria, "evaluation criteria")

        self._validate_required_fields(criteria)
        self._validate_weight(criteria)

        return self.repo.update(criteria)

    def delete_criteria(self, criteria: EvaluationCriteria) -> bool:
        """
        Removes a criteria from the system.

        Args:
            criteria (EvaluationCriteria): The criteria instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(criteria, "evaluation criteria")

    def list_active_criteria(self):
        """
        Retrieves all registered evaluation criteria.

        Returns:
            List[EvaluationCriteria]: A list of all available criteria.
        """
        return self.repo.get_all()
