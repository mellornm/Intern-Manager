"""
Application entry point and startup configuration.

This script initializes the application's components, including the database,
service layer, and user interface. It is responsible for orchestrating the
dependency injection process and launching the main Qt window.
"""

import sys
import ctypes
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.main_window import MainWindow


from data.database import DatabaseConnector

# Repositories
from repository.document_repo import DocumentRepository
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository
from repository.grade_repo import GradeRepository
from repository.intern_repo import InternRepository
from repository.meeting_repo import MeetingRepository
from repository.observation_repo import ObservationRepository
from repository.venue_repo import VenueRepository
from repository.visit_repo import VisitRepository


# Services
from services.document_service import DocumentService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.export_service import ExportService
from services.grade_service import GradeService
from services.import_service import ImportService
from services.intern_service import InternService
from services.meeting_service import MeetingService
from services.observation_service import ObservationService
from services.report_service import ReportService
from services.update_service import check_for_updates
from services.venue_service import VenueService
from services.visit_service import VisitService


# Utils
from utils.seeder import seed_default_criteria

# Config
from config import DB_DIR


def main():
    """
    Initializes and runs the Intern Manager application.

    This function serves as the main entry point. It performs the following
    steps in order:
    1.  Initializes the QApplication.
    2.  Connects to the SQLite database.
    3.  Sets up the dependency injection container by creating repositories
        and injecting them into the corresponding service classes.
    4.  Seeds the database with default data (e.g., evaluation criteria) if
        it is being run for the first time.
    5.  Checks a designated directory for a CSV file to perform an automatic
        data import on startup.
    6.  Ensures all existing interns have their required documents.
    7.  Instantiates and displays the main application window (`MainWindow`).
    8.  Enters the Qt event loop.
    """
    myappid = "mycompany.internmanager.pro.2026"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)

    print("\n=== SYSTEM STARTUP ===\n")

    print("INITIALIZING DATABASE CONNECTION")
    try:
        db = DatabaseConnector()
        print("   -> Connection successful\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to connect to database. Details: {e}\n")
        return

    # Ensure the database connection is cleanly closed when the app exits.
    app.aboutToQuit.connect(db.close)

    print("INITIALIZING SERVICES")
    try:
        repo_venue = VenueRepository(db)
        repo_intern = InternRepository(db)
        repo_doc = DocumentRepository(db)
        repo_obs = ObservationRepository(db)
        repo_criteria = EvaluationCriteriaRepository(db)
        repo_grade = GradeRepository(db)
        repo_meeting = MeetingRepository(db)
        repo_visit = VisitRepository(db)
        report_service = ReportService()

        v_service = VenueService(repo_venue)
        i_service = InternService(repo_intern)
        d_service = DocumentService(repo_doc)
        obs_service = ObservationService(repo_obs)
        m_service = MeetingService(repo_meeting)
        vis_service = VisitService(repo_visit)
        criteria_service = EvaluationCriteriaService(repo_criteria)

        grade_service = GradeService(repo=repo_grade, criteria_repo=repo_criteria)
        report_service = ReportService()

        imp_service = ImportService(
            intern_service=i_service,
            venue_service=v_service,
            document_service=d_service,
        )
        export_service = ExportService(db)
        print("   -> Services initialized successfully\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize services. Details: {e}\n")
        return

    # Populate the database with default evaluation criteria if it's a fresh setup.
    try:
        seed_default_criteria(criteria_service)
    except Exception as e:
        print(f"WARNING: Failed to seed default criteria. Details: {e}\n")

    print("CHECKING FOR CSV IMPORT...")
    csv_path = get_csv_path()

    if csv_path:
        try:
            imp_service.read_file(csv_path)
            if db.conn:
                db.conn.commit()
            else:
                print("ERRO CRÍTICO: Conexão perdida ao tentar salvar importação.")
        except Exception as e:
            print(f"ERROR: Failed to process import file. Details: {e}\n")
    else:
        print("   -> No CSV found or ignored. Starting with current database.\n")

    print("LAUNCHING GUI...")

    all_interns = i_service.get_all_interns()
    for intern in all_interns:
        if intern.intern_id:
            d_service.create_initial_documents_batch(intern.intern_id)

    window = MainWindow(
        intern_service=i_service,
        criteria_service=criteria_service,
        grade_service=grade_service,
        observation_service=obs_service,
        venue_service=v_service,
        document_service=d_service,
        meeting_service=m_service,
        visit_service=vis_service,
        report_service=report_service,
        import_service=imp_service,
        export_service=export_service,
    )

    window.show()
    QTimer.singleShot(2000, lambda: check_for_updates(window))

    print("\n=== SYSTEM RUNNING (GUI) ===")

    sys.exit(app.exec())


def get_csv_path() -> Optional[Path]:
    """
    Finds the path to a CSV file for automatic import.

    This function scans the `data/imports` directory for any file ending
    with the `.csv` extension. If multiple CSV files are found, it selects
    the first one alphabetically and logs a warning.

    Returns:
        An optional `Path` object pointing to the first CSV file found,
        or `None` if no CSV files are present in the import directory.
    """
    # Standard location for pending import files.
    imports_dir = DB_DIR / "imports"

    if not imports_dir.exists():
        return None

    csv_files = list(imports_dir.glob("*.csv"))

    if not csv_files:
        return None

    # Only one file is processed per run
    # If there's more than one, it uses the first one and warns the user.
    if len(csv_files) > 1:
        print(f"WARNING: Múltiplos CSVs encontrados. Usando {csv_files[0].name}")

    return csv_files[0]


if __name__ == "__main__":
    main()
