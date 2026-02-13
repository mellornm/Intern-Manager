from typing import List
from services.base_service import BaseService
from core.models.grade import Grade
from repository.grade_repo import GradeRepository
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository
from utils.validations import validate_required_fields

REQUIRED_FIELDS = {
    "intern_id": "Estagiário",
    "criteria_id": "Critério de Avaliação",
    "value": "Nota (Valor)",
}


class GradeService(BaseService[Grade]):
    """
    Service class responsible for business logic related to grades.

    This service manages the assignment of grades, ensuring that values are
    within valid ranges defined by the associated EvaluationCriteria.

    Attributes:
        repo (GradeRepository): Repository for grade persistence.
        criteria_repo (EvaluationCriteriaRepository): Repository to fetch criteria limits.
    """

    def __init__(
        self, repo: GradeRepository, criteria_repo: EvaluationCriteriaRepository
    ):
        """
        Initializes the service with necessary repositories.

        Args:
            repo (GradeRepository): Main repository for grades.
            criteria_repo (EvaluationCriteriaRepository): Repository to validate weights.
        """
        super().__init__(repo)
        self.criteria_repo = criteria_repo

    def _validate_grade_value(self, grade: Grade):
        """
        Ensures the grade value is positive and DOES NOT EXCEED the criteria limit.

        Args:
            grade (Grade): The grade entity to validate.

        Raises:
            ValueError: If grade is negative, criteria is not found, or grade > max weight.
        """

        if grade.value < 0:
            raise ValueError("A nota não pode ser negativa.")

        criteria = self.criteria_repo.get_by_id(grade.criteria_id)

        if not criteria:
            raise ValueError(
                f"Critério de avaliação {grade.criteria_id} não encontrado."
            )

        if grade.value > criteria.weight:
            raise ValueError(
                f"A nota ({grade.value}) não pode ser maior que o valor máximo deste critério "
                f"({criteria.name}: Max {criteria.weight})."
            )

    def get_intern_grades(self, intern_id: int) -> List[Grade]:
        """
        Retrieves all grades associated with a specific intern.

        Args:
            intern_id (int): The intern's identifier.

        Returns:
            List[Grade]: A list of Grade objects.
        """
        return self.repo.get_by_intern_id(intern_id)

    def add_new_grade(self, grade: Grade) -> int:
        """
        Validates business rules and saves a new grade.

        Args:
            grade (Grade): The grade to be saved.

        Returns:
            int: The ID of the newly created grade.
        """
        validate_required_fields(grade, REQUIRED_FIELDS)
        self._validate_grade_value(grade)
        return self.repo.save(grade)

    def update_grade(self, grade) -> bool:
        """
        Validates and updates an existing grade.

        Args:
            grade (Grade): The grade to be updated.

        Returns:
            bool: True if successful.
        """
        self._ensure_has_id(grade, "grade")
        self._validate_required_fields(grade)
        return self.repo.update(grade)

    def delete_grade(self, grade: Grade) -> bool:
        """
        Removes a grade from the system.

        Args:
            grade (Grade): The grade to be deleted.

        Returns:
            bool: True if successful.
        """
        return self.delete(grade, "grade")

    def get_grades_by_intern(self, intern_id: int) -> list[Grade]:
        """
        Retrieves all grades for a specific intern (Safe Version).

        Unlike `get_intern_grades`, this method handles empty/None IDs gracefully.

        Args:
            intern_id (int): The intern's identifier.

        Returns:
            list[Grade]: List of grades or an empty list if ID is invalid.
        """
        if not intern_id:
            return []
        return self.repo.get_by_intern_id(intern_id)

    def save_batch_grades(self, grades: list[Grade]):
        """
        Processes and persists a list of grades using an optimized Upsert strategy.

        This method minimizes database round-trips by pre-fetching existing grades
        for the associated intern. It determines whether to update an existing
        entry or create a new one based on the criteria ID.

        Business Rules:
            - All grades in the batch are assumed to belong to the same intern.
            - Each grade is validated against criteria limits before persistence.

        Args:
            grades (list[Grade]): List of Grade objects to process.

        Raises:
            ValueError: If any grade value is invalid, negative, or exceeds the criteria limit.
        """
        if not grades:
            return

        intern_id = grades[0].intern_id

        existing_grades = self.repo.get_by_intern_id(intern_id)

        existing_map = {g.criteria_id: g for g in existing_grades}

        for grade in grades:
            self._validate_grade_value(grade)

            if grade.criteria_id in existing_map:
                target_grade = existing_map[grade.criteria_id]

                target_grade.value = grade.value

                self.repo.update(target_grade)
            else:
                self.repo.save(grade)
