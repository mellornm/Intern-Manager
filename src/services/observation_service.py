from services.base_service import BaseService
from core.models.observation import Observation
from repository.observation_repo import ObservationRepository

REQUIRED_FIELDS = {
    "observation": "Comentário",
    "intern_id": "ID do Estagiário",
}


class ObservationService(BaseService[Observation]):
    """
    Service class responsible for business logic related to intern observations.

    This service acts as the bridge between the UI and the persistence layer
    for free-text notes/observations, ensuring all required data is present
    before saving.

    Attributes:
        repo (ObservationRepository): The repository for observation persistence.
        REQUIRED_FIELDS (Dict[str, str]): Mapping of required fields for validation.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: ObservationRepository):
        """
        Initializes the ObservationService with the specified repository.

        Args:
            repo (ObservationRepository): Repository for observation persistence.
        """
        super().__init__(repo)

    def add_new_observation(self, observation: Observation):
        """
        Validates and adds a new observation to the system.

        Args:
            observation (Observation): The observation instance to be added.

        Returns:
            int: The ID of the newly created observation.

        Raises:
            ValueError: If required fields (comment, intern_id) are missing.
        """
        self._validate_required_fields(observation)
        return self.repo.save(observation)

    def update_observation(self, observation: Observation):
        """
        Updates an existing observation after ensuring it has a valid ID.

        Args:
            observation (Observation): The observation instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the observation has no ID or fields are missing.
        """
        self._ensure_has_id(observation, "observation")
        self._validate_required_fields(observation)
        return self.repo.update(observation)

    def delete_observation(self, observation: Observation):
        """
        Removes a observation from the system using the base service logic.

        Args:
            observation (Observation): The observation instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(observation, "observation")

    def get_observations_by_intern(self, intern_id: int):
        """Retorna todas as observações de um estagiário."""
        return self.repo.get_by_intern_id(intern_id)
