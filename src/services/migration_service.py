import os
import sqlite3
import logging
from datetime import datetime
from typing import Type, Dict, Any, Optional
from sqlalchemy.orm import Session

from config import DB_PATH
from data.database import db_manager
from core.models.base import Base
from core.models.intern import Intern
from core.models.venue import Venue
from core.models.meeting import Meeting
from core.models.visit import Visit
from core.models.grade import Grade
from core.models.document import Document
from core.models.observation import Observation
from core.models.evaluation_criteria import EvaluationCriteria

logger = logging.getLogger(__name__)


class MigrationService:
    """
    Handles the heavy lifting of moving data from raw SQLite to SQLAlchemy.

    It's basically a data pump with a safety net, ensuring your real-world
    data doesn't evaporate during the upgrade.
    """

    @staticmethod
    def needs_migration() -> bool:
        """
        Check if the current DB file is a legacy fossil.
        """
        if not os.path.exists(DB_PATH):
            return False

        if os.path.getsize(DB_PATH) == 0:
            return False

        # Initialize to None to satisfy linters and avoid unbound errors
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Check for alembic tracking
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
            )
            if cursor.fetchone():
                return False

            # Check for the interns table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='interns'"
            )
            if not cursor.fetchone():
                return False

            # Final check for the new column
            cursor.execute("PRAGMA table_info(meetings)")
            columns = [row[1] for row in cursor.fetchall()]
            return "meeting_topic" not in columns if columns else True

        except sqlite3.Error as e:
            logger.error(f"Failed to probe database for migration: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _migrate_table(
        legacy_cursor: sqlite3.Cursor,
        session: Session,
        table_name: str,
        model_class: Type[Base],
        defaults: Optional[Dict[str, Any]] = None,
    ):
        """
        Pumps rows from one table to another, filtering for what the model actually expects.
        """
        try:
            legacy_cursor.execute(f"SELECT * FROM {table_name}")
            rows = legacy_cursor.fetchall()
        except sqlite3.OperationalError:
            logger.warning(f"Table '{table_name}' missing in legacy DB. Skipping.")
            return

        if not rows:
            return

        logger.info(f"Pumping {len(rows)} records from '{table_name}'...")

        valid_columns = {c.name for c in model_class.__table__.columns}

        for row in rows:
            # Convert sqlite3.Row to a clean dictionary
            data = {key: row[key] for key in row.keys()}

            if defaults:
                for key, value in defaults.items():
                    if key not in data or data[key] is None:
                        data[key] = value

            # Only keep columns that exist in the SQLAlchemy model
            filtered_data = {k: v for k, v in data.items() if k in valid_columns}

            # Create a new instance and add it to the session
            # Using model_class constructor is safer than merge for initial migrations
            obj = model_class(**filtered_data)
            session.add(obj)

    @staticmethod
    def run_auto_migration():
        """
        The main orchestration. Renames the old DB and builds a fresh one.
        """
        if not MigrationService.needs_migration():
            db_manager.create_tables()
            return

        logger.info("Legacy database detected. Starting automated migration...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        legacy_path = f"{DB_PATH}.legacy_{timestamp}"

        # Pre-initialize variables for the finally/except blocks
        legacy_conn: Optional[sqlite3.Connection] = None
        session: Optional[Session] = None

        try:
            os.rename(DB_PATH, legacy_path)
            logger.info(f"Original DB moved to {legacy_path}")

            # Ensure fresh tables exist
            db_manager.create_tables()

            # Connect to legacy with Row factory
            legacy_conn = sqlite3.connect(legacy_path)
            legacy_conn.row_factory = sqlite3.Row
            legacy_cursor = legacy_conn.cursor()

            session = db_manager.get_session()

            # Migration Order (Dependencies first!)
            MigrationService._migrate_table(legacy_cursor, session, "venues", Venue)
            # Flush to ensure IDs are available for FKs if needed,
            # though we are migrating explicit IDs.
            session.flush()

            MigrationService._migrate_table(
                legacy_cursor, session, "evaluation_criteria", EvaluationCriteria
            )
            session.flush()

            MigrationService._migrate_table(legacy_cursor, session, "interns", Intern)
            session.flush()

            MigrationService._migrate_table(
                legacy_cursor, session, "documents", Document
            )
            MigrationService._migrate_table(
                legacy_cursor, session, "observations", Observation
            )
            MigrationService._migrate_table(legacy_cursor, session, "visits", Visit)
            MigrationService._migrate_table(legacy_cursor, session, "grades", Grade)

            MigrationService._migrate_table(
                legacy_cursor,
                session,
                "meetings",
                Meeting,
                defaults={"meeting_topic": "General Follow-up"},
            )

            session.commit()
            logger.info("Migration successful!")

        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"FATAL: Migration failed. Reason: {e}")

            raise e
        finally:
            if legacy_conn:
                legacy_conn.close()
            if session:
                session.close()
