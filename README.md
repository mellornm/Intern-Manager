# Intern Manager

A desktop application for managing academic internships.

[![Status](https://img.shields.io/badge/Status-In_Development-blue?style=for-the-badge)](https://github.com/mellorn/intern-manager)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt_for_Python-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.qt.io/qt-for-python)
[![uv](https://img.shields.io/badge/Manager-uv-purple?style=for-the-badge)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE.md)

---

## About the Project

**Intern Manager** is a desktop application designed to streamline the administration of internship programs. It manages student information, practice locations (such as hospitals and clinics), supervisors, and automates document generation and grade calculation based on weighted criteria.

The application is built using the **Repository Pattern** with **Dependency Injection**, which creates a decoupled, testable, and maintainable codebase.

---

## Core Features

*   **Intern Management:** Full CRUD operations with data validation, including **visual indicators** for contract expiration and **time elapsed progress bars**.
*   **Communication Shortcuts:** Integrated actions for quick contact via **WhatsApp and E-mail**.
*   **Venue Management:** Manage internship locations and their supervisors.
*   **Supervision & Meetings:**
    *   **Supervision Calendar:** Monthly view for tracking meetings and on-site visits.
    *   **Visit Evidence:** Secure photo storage with automatic ISO sanitization.
*   **Evaluation System:**
    *   Customizable, weighted grading criteria.
    *   Automatic calculation of averages and final status (Pass/Fail).
*   **Productivity Tools:**
    *   **Batch Export:** Simultaneous generation of multiple PDF reports.
    *   **Collective Approval:** Bulk processing of mandatory documents.
    *   **Interactive Dashboard:** KPI cards with drill-down filtering.
*   **Document Generation:** Automatically create essential documents like contracts and attendance sheets.
*   **Batch Import:** Process `.csv` files to add or update multiple records at once using an "upsert" logic.
*   **Data Persistence:** Uses a local SQLite database for simplicity and portability.

---

## Technologies and Prerequisites

To run this project, you will need the following software installed:

*   **Python 3.13+**
*   **uv:** A fast Python package installer and resolver.
    *   *Installation instructions can be found at [uv.astral.sh](https://uv.astral.sh/).*
*   **Git**

---

## How to Run the Project

Follow the steps below to set up and run the application locally.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mellorn/intern-manager.git
    cd intern-manager
    ```

2.  **Create a virtual environment:**
    This command will create a `.venv` directory in the project folder.
    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**
    -   On Windows (PowerShell):
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    -   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    This command installs the project dependencies from the `uv.lock` file.
    ```bash
    uv sync
    ```

5.  **Run the application:**
    ```bash
    uv run python src/main.py
    ```

---

## Project Architecture

The project is organized into a modular structure to promote maintainability and scalability, following the **Repository Pattern** and **Service Layer** principles.

```
src/
├── core/
│   └── models/          # Domain entities (SQLAlchemy Models)
├── data/
│   └── database.py      # Database connector and session management
├── repository/          # Data Access Layer (Abstraction over SQLAlchemy)
├── services/            # Business Logic (Batch Ops, Reports, Communications)
├── ui/                  # Presentation Layer (PySide6 / Qt)
│   ├── components/      # Reusable UI widgets (Metric cards, Stat cards)
│   ├── dialogs/         # Form dialogs and configuration windows
│   ├── views/           # Specialized views (Dashboard, Calendar, Venues)
│   └── main_window.py   # Application shell and navigation logic
├── utils/               # Helpers (Validators, Text processors, Seeders)
└── main.py              # Entry point and Dependency Injection container
```

### Layer Responsibilities

-   **`core`**: Defines the fundamental data structures and business rules.
-   **`data`**: Handles low-level database operations and migrations (Alembic).
-   **`repository`**: Provides a clean interface for data retrieval and persistence, decoupling the domain from the DB engine.
-   **`services`**: Orchestrates complex operations, such as batch report generation and automated communication protocols.
-   **`ui`**: Manages the user interface, utilizing custom delegates for advanced table rendering (progress bars, status icons).
-   **`utils`**: Contains cross-cutting concerns like data validation and URL formatting for external integrations.

---

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for more details.

---

## Developed by

Rodrigo Mello
mellornm@gmail.com
