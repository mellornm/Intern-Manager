import os
import traceback
from PySide6.QtCore import QThread, Signal


class BatchReportWorker(QThread):
    """
    Worker thread for generating multiple PDF reports in the background.
    """

    progress_changed = Signal(int, str)  # (current_count, current_name)
    finished = Signal(int, int)  # (success_count, total_count)
    error_occurred = Signal(str)

    def __init__(self, target_folder, selected_intern_ids, services):
        """
        Initializes the worker with required data and services.

        Args:
            target_folder: Where to save the PDFs.
            selected_intern_ids: List of intern IDs to process.
            services: Dictionary containing all required services.
        """
        super().__init__()
        self.target_folder = target_folder
        self.intern_ids = selected_intern_ids
        self.services = services
        self._is_cancelled = False

    def stop(self):
        """Signals the worker to stop processing as soon as possible."""
        self._is_cancelled = True

    def run(self):
        """Processes each intern in the list and generates their PDF report."""
        success_count = 0
        total = len(self.intern_ids)

        # Extract services for easier access
        i_service = self.services.get("intern")
        v_service = self.services.get("venue")
        c_service = self.services.get("criteria")
        g_service = self.services.get("grade")
        d_service = self.services.get("document")
        m_service = self.services.get("meeting")
        o_service = self.services.get("observation")
        vi_service = self.services.get("visit")
        r_service = self.services.get("report")

        try:
            for i, intern_id in enumerate(self.intern_ids):
                if self._is_cancelled:
                    break

                # 1. Fetch Intern
                intern = i_service.get_by_id(intern_id)
                if not intern:
                    continue

                self.progress_changed.emit(i + 1, intern.name)

                # 2. Collect all data for report
                venue = (
                    v_service.get_by_id(intern.venue_id) if intern.venue_id else None
                )
                criteria = c_service.list_active_criteria()
                grades = g_service.get_by_intern_id(intern_id)
                docs = d_service.get_by_intern_id(intern_id)
                meetings = m_service.get_by_intern_id(intern_id)
                observations = o_service.get_by_intern_id(intern_id)
                visits = vi_service.get_by_intern_id(intern_id) if vi_service else []

                # 3. Define safe filename
                safe_name = (
                    "".join(c for c in intern.name if c.isalnum() or c in (" ", "_"))
                    .strip()
                    .replace(" ", "_")
                )
                ra_suffix = (
                    f"_{intern.registration_number}"
                    if intern.registration_number
                    else ""
                )
                filename = f"Relatorio_{safe_name}{ra_suffix}.pdf"
                filepath = os.path.join(self.target_folder, filename)

                # 4. Generate PDF
                r_service.generate_pdf(
                    filepath,
                    intern,
                    venue,
                    criteria,
                    grades,
                    docs,
                    meetings,
                    observations,
                    visits,
                )

                success_count += 1

            self.finished.emit(success_count, total)

        except Exception as e:
            traceback.print_exc()
            self.error_occurred.emit(str(e))
