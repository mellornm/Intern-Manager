import calendar
import shutil
import uuid
from datetime import date
from pathlib import Path
from typing import List


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


class VisitService(BaseService[Visit]):
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
        """
        Remove a visita do banco e, se tiver sucesso, apaga a foto associada do disco.
        """
        full_visit_data = self.repo.get_by_id(visit.visit_id)

        if not full_visit_data:
            return False

        db_success = self.repo.delete(visit.visit_id)

        if db_success and full_visit_data.photo_path:
            self._delete_physical_photo(full_visit_data.photo_path)

        return db_success

    def _delete_physical_photo(self, filename: str):
        try:
            import os
            from config import USER_DATA_ROOT

            photo_path = USER_DATA_ROOT / "photos" / filename

            if photo_path.exists():
                os.remove(photo_path)

        except Exception as e:
            print(f"Aviso: Não foi possível deletar a imagem {filename}: {e}")

    def get_by_intern_id(self, intern_id: int):
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

    def export_batch_photos(
        self, intern_data: list[tuple[int, str]], target_folder: str
    ) -> tuple[int, int]:
        photos_root = USER_DATA_ROOT / "photos"
        count_success = 0
        count_errors = 0

        for int_id, int_name in intern_data:
            visits = self.repo.get_by_intern_id(int_id)

            visits_with_photos = [v for v in visits if v.photo_path]

            if not visits_with_photos:
                continue

            safe_name = sanitize_filename(int_name)
            student_dir = Path(target_folder) / safe_name

            try:
                student_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                count_errors += 1
                continue

            for v in visits_with_photos:
                source_file = photos_root / v.photo_path

                if source_file.exists():
                    ext = source_file.suffix
                    new_name = f"{v.visit_date}_Visita_{v.visit_id}{ext}"
                    dest_file = student_dir / new_name

                    try:
                        shutil.copy2(source_file, dest_file)
                        count_success += 1
                    except Exception:
                        count_errors += 1
                else:
                    count_errors += 1

        return count_success, count_errors

    def get_calendar_events(self, month: int, year: int) -> List[Visit]:
        """
        Retrieves all visits for a specific month and year.

        Args:
            month (int): The month (1-12).
            year (int): The year (e.g., 2024).

        Returns:
            List[Visit]: Visits within the specified month range.
        """
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1).isoformat()
        end_date = date(year, month, last_day).isoformat()
        return self.repo.get_visits_in_range(start_date, end_date)
