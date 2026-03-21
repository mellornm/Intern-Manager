"""
Application Configuration and Path Management.

This module is responsible for defining and managing critical file system paths
for the application. It dynamically determines paths for resources and user data,
ensuring compatibility with both development mode and a "frozen" executable
created by PyInstaller.

Attributes:
    APP_ROOT (Path): The root directory for read-only application resources.
                     In development, this is the 'src' directory. In a frozen
                     app, it points to the temporary `_MEIPASS` folder.
    USER_DATA_ROOT (Path): The root directory for writable user data.
                           In development, this is the 'data' directory inside
                           the project. In a frozen app, it points to a
                           dedicated 'InternManager' folder in the user's
                           `APPDATA` or home directory.
    RESOURCES_DIR (Path): The location of static, read-only resources like
                          SQL scripts or images.
    SQL_PATH (Path): The full path to the database schema creation script.
    DB_DIR (Path): The directory where the SQLite database is stored.
                   This is an alias for USER_DATA_ROOT.
    DB_PATH (Path): The full path to the SQLite database file (`interns.db`).
"""

import os
import sys
from pathlib import Path


def get_app_paths() -> tuple[Path, Path]:
    """
    Determines the execution and user data paths for the application.

    This function provides compatibility for running the app in both development
    mode and as a frozen executable (e.g., via PyInstaller).

    - **Application Root (`app_root`)**: In a frozen app, this points to the
      temporary folder (`_MEIPASS`) where bundled resources are unpacked.
      In development mode, it points to the project's 'src' directory.
      This path should be considered READ-ONLY.

    - **User Data Root (`user_data_root`)**: In a frozen app, this points to a
      writable directory (e.g., `%APPDATA%\\InternManager` on Windows) to store
      user-specific data like the database. In development mode, it points
      to the `data` folder within the project structure. This path is WRITABLE.

    Returns:
        A tuple containing two Path objects: (`app_root`, `user_data_root`).
    """
    # 1. Determine the read-only path for code/resources.
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            # Standard PyInstaller one-file bundle.
            app_root = Path(sys._MEIPASS)  # type:ignore
        else:
            # Fallback for other bundling methods or one-folder bundle.
            app_root = Path(sys.executable).parent
    else:
        # Running in a normal development environment.
        app_root = Path(__file__).resolve().parent.parent

    # 2. Determine the writable path for the user database.
    if getattr(sys, "frozen", False):
        base_path = os.getenv("APPDATA") or os.path.expanduser("~")
        user_data_root = Path(base_path) / "InternManager"
    else:
        user_data_root = app_root / "data"

    return app_root, user_data_root


# --- Global Configuration ---
APP_ROOT, USER_DATA_ROOT = get_app_paths()

RESOURCES_DIR = APP_ROOT / "resources"
SQL_PATH = RESOURCES_DIR / "create_db.sql"

DB_DIR = USER_DATA_ROOT
DB_PATH = DB_DIR / "interns.db"

DB_DIR.mkdir(parents=True, exist_ok=True)

# Version
VERSION = "2.0.0"
REPO_URL = "https://api.github.com/repos/vonroderik/Intern-Manager/releases/latest"
