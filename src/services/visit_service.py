import shutil
import uuid
from pathlib import Path

from repository.visit_repo import VisitRepository

from config import USER_DATA_ROOT
from core.models.visit import Visit
from services.base_service import BaseService
from utils.text_utils import sanitize_filename
from utils.validations import parse_date_to_iso

REQUIRED_FIELDS = {
    "intern_id": "ID do Estagiário",
    "visit_date": "Data da Reunião",
}


class VIsitService(BaseService[Visit]):
    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: VisitRepository):
        super().__init__(repo)

    def add_new_visit(self, visit: Visit):
        self._validate_required_fields(visit)

        try:
            visit.visit_date = parse_date_to_iso(visit.visit_date)
        except ValueError:
            pass

        return self.repo.save(visit)

    def update_visit(self, visit: Visit):
        self._ensure_has_id(visit, "visit")
        self._validate_required_fields(visit)
        return self.repo.update(visit)

    def delete_visit(self, visit: Visit):
        return self.delete(visit, "visit")

    def get_visits_by_intern(self, intern_id: int):
        return self.repo.get_by_intern_id(intern_id)

    def save_photo(
        self, original_path_str: str, intern_name: str, venue_name: str, visit_date: str
    ) -> str:
        original_path = Path(original_path_str)
        if not original_path.exists():
            return ""

        photos_dir = USER_DATA_ROOT / "photos"
        photos_dir.mkdir(parents=True, exist_ok=True)

        safe_intern = sanitize_filename(intern_name)
        safe_venue = sanitize_filename(venue_name)

        short_hash = uuid.uuid4().hex[:4]

        filename = f"{visit_date}__{safe_intern}__{safe_venue}__{short_hash}{original_path.suffix}"

        destination = photos_dir / filename

        shutil.copy(original_path, destination)

        return filename
