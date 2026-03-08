"""
Application entry point and startup configuration.

This script initializes the application's components, including the database,
service layer, and user interface using SQLAlchemy 2.0.
"""

import sys
import ctypes
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from ui.main_window import MainWindow

from data.database import db_manager

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

    This function serves as the main entry point using SQLAlchemy for data access.
    """
    myappid = "mycompany.internmanager.pro.2026"
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)

    print("\n=== SYSTEM STARTUP (SQLAlchemy 2.0) ===\n")

    print("INITIALIZING DATABASE")
    try:
        # Bootstrap tables if they don't exist
        db_manager.create_tables()
        print("   -> Database ready\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize database. Details: {e}\n")
        QMessageBox.critical(None, "Erro Fatal", f"Falha ao inicializar banco de dados:\n{e}")
        return

    print("INITIALIZING SERVICES")
    try:
        # Initialize repositories (they use db_manager.get_session internally)
        repo_venue = VenueRepository()
        repo_intern = InternRepository()
        repo_doc = DocumentRepository()
        repo_obs = ObservationRepository()
        repo_criteria = EvaluationCriteriaRepository()
        repo_grade = GradeRepository()
        repo_meeting = MeetingRepository()
        repo_visit = VisitRepository()

        # Initialize services
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
        
        # ExportService now uses SQLAlchemy engine
        export_service = ExportService()
        
        print("   -> Services initialized successfully\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize services. Details: {e}\n")
        QMessageBox.critical(None, "Erro Fatal", f"Falha ao carregar componentes do sistema:\n{e}")
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
            print(f"   -> Successfully imported: {csv_path.name}")
        except Exception as e:
            print(f"ERROR: Failed to process import file. Details: {e}\n")
    else:
        print("   -> No CSV found or ignored. Starting with current database.\n")

    print("LAUNCHING GUI...")

    # Ensure all existing interns have their document tracking initialized
    try:
        all_interns = i_service.get_all_interns()
        for intern in all_interns:
            if intern.intern_id:
                d_service.create_initial_documents_batch(intern.intern_id)
    except Exception as e:
        print(f"WARNING: Consistency check failed: {e}")

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
    """
    imports_dir = DB_DIR / "imports"

    if not imports_dir.exists():
        return None

    csv_files = list(imports_dir.glob("*.csv"))

    if not csv_files:
        return None

    if len(csv_files) > 1:
        print(f"WARNING: Múltiplos CSVs encontrados. Usando {csv_files[0].name}")

    return csv_files[0]


if __name__ == "__main__":
    main()
