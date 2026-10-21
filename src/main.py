"""
Application entry point and startup configuration for InternManager Pro Web.

Initializes the database, runs migrations, seeds initial data, wires dependency injection,
and launches the NiceGUI web server.
"""

import logging
from pathlib import Path
from typing import Optional

from nicegui import app, ui

# Config
from config import (
    APP_HOST,
    APP_PORT,
    APP_RELOAD,
    APP_STORAGE_SECRET,
    DB_DIR,
    RESOURCES_DIR,
    UPLOADS_DIR,
    USER_DATA_ROOT,
    VERSION,
)
from data.database import db_manager
from services.migration_service import MigrationService
from ui.context import get_container
from ui.routes import register_routes
from utils.seeder import seed_default_criteria

logger = logging.getLogger("intern_manager")


def get_csv_path() -> Optional[Path]:
    """Finds path to a CSV file for automatic import if present."""
    imports_dir = DB_DIR / "imports"
    if not imports_dir.exists():
        return None

    csv_files = list(imports_dir.glob("*.csv"))
    if not csv_files:
        return None

    if len(csv_files) > 1:
        logger.warning("Múltiplos CSVs encontrados. Usando %s", csv_files[0].name)

    return csv_files[0]


def startup_system():
    """Bootstraps database, runs migrations, seeds criteria and consistency checks."""
    logger.info("=== SYSTEM STARTUP (InternManager Web NiceGUI) ===")

    # 1. Run database migrations
    try:
        MigrationService.run_auto_migration()
        logger.info("Database migrations executed successfully.")
    except Exception as e:
        logger.error("Failed to execute database migrations: %s", e)

    # 2. Bootstrap tables if needed
    try:
        db_manager.create_tables()
        logger.info("Database tables verified/created.")
    except Exception as e:
        logger.critical("Failed to initialize database: %s", e)
        raise e

    # 3. Initialize pure dependency injection container
    container = get_container()
    logger.info("Service container initialized.")

    # 4. Seed default evaluation criteria
    try:
        seed_default_criteria(container.criteria_service)
        logger.info("Default evaluation criteria seeded.")
    except Exception as e:
        logger.warning("Failed to seed default criteria: %s", e)

    # 5. Check for automatic CSV import in imports folder
    csv_path = get_csv_path()
    if csv_path:
        try:
            container.import_service.read_file(csv_path)
            logger.info("Auto-imported CSV file: %s", csv_path.name)
        except Exception as e:
            logger.error("Failed to process auto-import CSV: %s", e)

    # 6. Ensure document consistency for all interns
    try:
        all_interns = container.intern_service.get_all_interns()
        for intern in all_interns:
            if intern.intern_id:
                container.document_service.create_initial_documents_batch(intern.intern_id)
        logger.info("Document consistency check complete.")
    except Exception as e:
        logger.warning("Document consistency check warning: %s", e)

    # 7. Static file directories
    photos_dir = USER_DATA_ROOT / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    attachments_dir = USER_DATA_ROOT / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    app.add_static_files("/photos", str(photos_dir))
    app.add_static_files("/attachments", str(attachments_dir))
    app.add_static_files("/uploads", str(UPLOADS_DIR))

    # 8. Register all Web routes
    register_routes()


def main():
    """Main execution function."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    startup_system()

    favicon_path = RESOURCES_DIR / "app_icon.ico"
    favicon = str(favicon_path) if favicon_path.exists() else None

    logger.info("Launching NiceGUI Web Server on http://%s:%d", APP_HOST, APP_PORT)

    ui.run(
        host=APP_HOST,
        port=APP_PORT,
        title=f"InternManager Pro v{VERSION}",
        favicon=favicon,
        storage_secret=APP_STORAGE_SECRET,
        reload=APP_RELOAD,
        show=False,  # Don't auto-open browser on headless server
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
