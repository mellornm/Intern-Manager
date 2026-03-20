import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.engine import Engine
from config import DB_PATH
from core.models.base import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton manager for SQLAlchemy engine and session lifecycle.

    Handles SQLite-specific pragmas for Windows performance and ensures
    thread-safe session management for the PySide UI.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        db_url = f"sqlite:///{DB_PATH}"

        self.engine = create_engine(
            db_url, connect_args={"check_same_thread": False}, echo=False
        )

        session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False, expire_on_commit=False
        )

        self.SessionLocal = scoped_session(session_factory)

        self._setup_listeners()
        self._initialized = True
        logger.info("Database engine started.")

    def _setup_listeners(self):
        """
        Inject critical SQLite pragmas on every new connection.
        """

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()

            cursor.execute("PRAGMA foreign_keys=ON")

            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    def get_session(self) -> Session:
        """Return the current session from the registry."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        Ensures session is closed and resources are freed.
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            self.SessionLocal.remove()

    def create_tables(self):
        """
        Bootstrap tables from models.
        Only use this for dev; Alembic handles migrations in prod.
        """
        Base.metadata.create_all(bind=self.engine)


db_manager = DatabaseManager()
