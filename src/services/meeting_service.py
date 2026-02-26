from typing import Any

from core.models.meeting import Meeting
from repository.meeting_repo import MeetingRepository
from services.base_service import BaseService
from utils.validations import parse_date_to_iso

REQUIRED_FIELDS = {
    "intern_id": "ID do Estagiário",
    "meeting_date": "Data da Reunião",
}


class MeetingService(BaseService[Meeting]):
    """
    Service class responsible for business logic related to supervision meetings.

    This service manages the scheduling and recording of meetings between
    interns and supervisors, ensuring date formats are standardized for storage.

    Attributes:
        repo (MeetingRepository): The repository for meeting persistence.
        REQUIRED_FIELDS (Dict[str, str]): Mapping of required fields for validation.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: MeetingRepository):
        """
        Initializes the MeetingService with the specified repository.

        Args:
            repo (MeetingRepository): Repository for meeting persistence.
        """
        super().__init__(repo)

    def add_new_meeting(self, meeting: Meeting):
        """
        Validates date format and adds a new meeting.

        Attempts to convert the date from UI format (DD/MM/YYYY) to ISO (YYYY-MM-DD).
        If conversion fails, it silently proceeds with the original string.

        Args:
            meeting (Meeting): The meeting instance to be added.

        Returns:
            int: The ID of the newly created meeting.

        Raises:
            ValueError: If required fields are missing.
        """
        self._validate_required_fields(meeting)

        try:
            meeting.meeting_date = parse_date_to_iso(meeting.meeting_date)
        except ValueError:
            pass

        return self.repo.save(meeting)

    def get_meetings_by_intern(self, intern_id: int):
        """
        Retrieves all meetings associated with a specific intern.

        Args:
            intern_id (int): The unique identifier of the intern.

        Returns:
            List[Meeting]: A list of Meeting objects for that intern.
        """
        return self.repo.get_by_intern_id(intern_id)

    def delete_meeting(self, data_or_id: Any):
        """
        Removes a meeting from the system using the base service logic.

        Args:
            meeting (Meeting): The meeting instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return super().delete(data_or_id, "meeting")
