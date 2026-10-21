import os
import shutil
import uuid
from datetime import date
from pathlib import Path
from typing import Any

from config import USER_DATA_ROOT
from core.models.observation import Observation
from repository.observation_repo import ObservationRepository
from services.base_service import BaseService
from utils.text_utils import sanitize_filename

REQUIRED_FIELDS = {
    "observation": "Comentário / Relato",
    "intern_id": "ID do Estagiário",
}


class ObservationService(BaseService[Observation]):
    """
    Service class responsible for business logic related to intern observations
    and medical/field incident reports with optional file attachments.

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
        Validates and adds a new observation or incident to the system.

        Args:
            observation (Observation): The observation instance to be added.

        Returns:
            int: The ID of the newly created observation.

        Raises:
            ValueError: If required fields (observation, intern_id) are missing.
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

    def delete_observation(self, data_or_id: Any):
        """
        Removes an observation from the system and deletes its physical attachment if present.

        Args:
            data_or_id (Any): The Observation instance or observation_id to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        obs_id = getattr(data_or_id, "observation_id", None) or (
            data_or_id if isinstance(data_or_id, int) else None
        )
        full_obs = self.repo.get_by_id(obs_id) if obs_id else None

        db_success = self.delete(data_or_id, "observation")

        if db_success and full_obs and full_obs.attachment_path:
            self._delete_physical_attachment(full_obs.attachment_path)

        return db_success

    def save_attachment(self, original_path_str: str, intern_name: str) -> str:
        """
        Copies an uploaded attachment (PDF, image, document) into USER_DATA_ROOT / 'attachments'
        with a standardized, sanitized filename.
        """
        original_path = Path(original_path_str)
        if not original_path.exists():
            return ""

        attachments_dir = USER_DATA_ROOT / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)

        safe_intern = sanitize_filename(intern_name)
        today_str = date.today().isoformat()
        short_hash = uuid.uuid4().hex[:6]

        filename = f"{today_str}__{safe_intern}__{short_hash}{original_path.suffix}"
        destination = attachments_dir / filename

        shutil.copy2(original_path, destination)
        return filename

    def get_attachment_full_path(self, filename: str) -> Path:
        """Returns the full Path to an attachment file in USER_DATA_ROOT / 'attachments'."""
        return USER_DATA_ROOT / "attachments" / filename

    def _delete_physical_attachment(self, filename: str):
        try:
            att_path = self.get_attachment_full_path(filename)
            if att_path.exists():
                os.remove(att_path)
        except Exception as e:
            print(f"Aviso: Não foi possível deletar o anexo {filename}: {e}")

    def get_by_intern_id(self, intern_id: int):
        """Retorna todas as observações e ocorrências de um estagiário."""
        return self.repo.get_by_intern_id(intern_id)
