from services.base_service import BaseService
from utils.text_utils import smart_title
from core.models.venue import Venue
from repository.venue_repo import VenueRepository
from utils.validations import validate_email_format

from typing import Optional

REQUIRED_FIELDS = {
    "venue_name": "Nome do local de Estágio",
    "supervisor_name": "Nome do Supervisor",
}


class VenueService(BaseService[Venue]):
    """
    Service class responsible for business logic related to internship venues.

    This service manages the lifecycle of 'Venue' entities (hospitals, clinics,
    companies), ensuring that contact information like supervisor email is
    validated before persistence.

    Attributes:
        repo (VenueRepository): The repository for venue persistence.
        REQUIRED_FIELDS (Dict[str, str]): Mapping of required fields for validation.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: VenueRepository):
        """
        Initializes the VenueService with the specified repository.

        Args:
            repo (VenueRepository): Repository for venue persistence.
        """
        super().__init__(repo)

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Searches for a Venue by its name.

        Args:
            name (str): The name (or partial name) to search for.

        Returns:
            Optional[Venue]: The Venue object if found, or None.
        """
        return self.repo.get_by_name(name)

    def add_new_venue(self, venue: Venue):
        """
        Validates and adds a new venue to the system.

        Performs field validation and checks the supervisor's email format
        if provided.

        Args:
            venue (Venue): The venue instance to be added.

        Returns:
            int: The ID of the newly created venue.

        Raises:
            ValueError: If required fields are missing or email format is invalid.
        """
        self._validate_required_fields(venue)

        if venue.supervisor_email:
            validate_email_format(str(venue.supervisor_email))

        venue.venue_name = smart_title(venue.venue_name)

        return self.repo.save(venue)

    def update_venue(self, venue: Venue):
        """
        Updates an existing venue after ensuring it has a valid ID.

        Args:
            venue (Venue): The venue instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the venue object does not have an ID.
        """
        self._ensure_has_id(venue, "venue")
        self._validate_required_fields(venue)

        if venue.supervisor_email:
            validate_email_format(str(venue.supervisor_email))

        venue.venue_name = smart_title(venue.venue_name)

        return self.repo.update(venue)

    def delete_venue(self, venue: Venue):
        """
        Removes a venue from the system using the base service logic.

        Args:
            venue (Venue): The venue instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(venue, "venue")
