import os
import sys
import sqlite3
import logging
from typing import List, Type, Dict, Any, Optional

# 1. Adjust paths FIRST before any local imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sqlalchemy.orm import Session  # noqa: E402
from config import DB_PATH  # noqa: E402
from data.database import db_manager  # noqa: E402
from core.models.base import Base  # noqa: E402
from core.models.intern import Intern  # noqa: E402
from core.models.venue import Venue  # noqa: E402
from core.models.meeting import Meeting  # noqa: E402
from core.models.visit import Visit  # noqa: E402
from core.models.grade import Grade  # noqa: E402
from core.models.document import Document  # noqa: E402
from core.models.observation import Observation  # noqa: E402
from core.models.evaluation_criteria import EvaluationCriteria  # noqa: E402

# Configure logging for the migration process
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("migration")


def is_legacy_db(path: str) -> bool:
    """
    Checks if the database at the given path is using the legacy schema.
    Specifically checks for the absence of the 'meeting_topic' column.
    """
    if not os.path.exists(path):
        return False

    conn = sqlite3.connect(path)
    try:
        cursor = conn.cursor()
        # Check if meetings table exists and has the new column
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [row[1] for row in cursor.fetchall()]
        if not columns:  # Table doesn't exist at all
            return True
        return "meeting_topic" not in columns
    except Exception:
        return True
    finally:
        conn.close()


def get_legacy_rows(cursor: sqlite3.Cursor, table_name: str) -> List[sqlite3.Row]:
    """
    Safely fetches all rows from a table in the legacy database.
    """
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall()
    except sqlite3.OperationalError:
        logger.warning(f"Table '{table_name}' not found in legacy database. Skipping.")
        return []


def migrate_table(
    cursor: sqlite3.Cursor,
    session: Session,
    table_name: str,
    model_class: Type[Base],
    defaults: Optional[Dict[str, Any]] = None,
):
    """
    Pumps data from a legacy SQLite table into the SQLAlchemy-managed database.
    """
    rows = get_legacy_rows(cursor, table_name)
    if not rows:
        return

    logger.info(f"Migrating {len(rows)} records from '{table_name}'...")

    # Identify which columns the model actually expects
    valid_columns = {c.name for c in model_class.__table__.columns}

    for row in rows:
        data = dict(row)

        # Apply defaults for new columns
        if defaults:
            for key, value in defaults.items():
                if key not in data or data[key] is None:
                    data[key] = value

        # Filter to valid columns only
        filtered_data = {k: v for k, v in data.items() if k in valid_columns}

        # Use merge() to handle upserts
        obj = model_class(**filtered_data)
        session.merge(obj)

    session.commit()
    logger.info(f"Successfully migrated '{table_name}'.")


def run_migration():
    """
    Orchestrates the full database migration process.
    """
    logger.info("Starting database migration to SQLAlchemy...")

    legacy_db_path = str(DB_PATH)
    backup_path = legacy_db_path + ".legacy"

    # 1. Check if we need to swap the database file to allow fresh table creation
    if is_legacy_db(legacy_db_path):
        logger.info(
            f"Legacy database detected at {legacy_db_path}. Backing up to {backup_path}"
        )
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(legacy_db_path, backup_path)
        source_db = backup_path
    else:
        # If it's already a new DB or doesn't exist, we use it directly as source
        # (though if it doesn't exist, migration will just skip tables)
        source_db = legacy_db_path if os.path.exists(legacy_db_path) else None

    # 2. Ensure new schema exists in the target DB_PATH
    # (SQLAlchemy will create a fresh file here if we renamed the old one)
    db_manager.create_tables()

    if not source_db:
        logger.info("No source database found to migrate data from. Schema created.")
        return

    # 3. Connect to legacy database
    try:
        legacy_conn = sqlite3.connect(source_db)
        legacy_conn.row_factory = sqlite3.Row
        legacy_cursor = legacy_conn.cursor()
    except Exception as e:
        logger.error(f"Failed to connect to legacy database: {e}")
        return

    # 4. Initialize SQLAlchemy session
    session = db_manager.get_session()

    try:
        # --- Migration Order (Respecting FK Constraints) ---
        migrate_table(legacy_cursor, session, "venues", Venue)
        migrate_table(legacy_cursor, session, "evaluation_criteria", EvaluationCriteria)
        migrate_table(legacy_cursor, session, "interns", Intern)
        migrate_table(legacy_cursor, session, "documents", Document)
        migrate_table(legacy_cursor, session, "observations", Observation)

        migrate_table(
            legacy_cursor,
            session,
            "meetings",
            Meeting,
            defaults={"meeting_topic": "General Follow-up"},
        )

        migrate_table(legacy_cursor, session, "visits", Visit)
        migrate_table(legacy_cursor, session, "grades", Grade)

        logger.info("Database migration completed successfully!")

    except Exception as e:
        session.rollback()
        logger.error(f"Migration failed during execution: {e}")
        raise
    finally:
        session.close()
        legacy_conn.close()


if __name__ == "__main__":
    run_migration()
