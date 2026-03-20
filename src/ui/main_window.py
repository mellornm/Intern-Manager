"""
Main window and user interface for the Intern Manager application.
"""

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QProgressDialog,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from typing import Optional

# Config
from config import RESOURCES_DIR

# Models & Services
from services.document_service import DocumentService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService
from services.import_service import ImportService
from services.intern_service import InternService
from services.meeting_service import MeetingService
from services.observation_service import ObservationService
from services.report_service import ReportService
from services.venue_service import VenueService
from services.visit_service import VisitService
from services.communication_service import CommunicationService

# Styles and Components
from ui.criteria_view import CriteriaView
from ui.dashboard_view import DashboardView
from ui.delegates import StatusDelegate, ProgressBarDelegate

# Dialogs
from ui.dialogs.batch_document_dialog import BatchDocumentDialog
from ui.dialogs.batch_meeting_dialog import BatchMeetingDialog
from ui.dialogs.document_dialog import DocumentDialog
from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.intern_dialog import InternDialog
from ui.dialogs.meeting_dialog import MeetingDialog
from ui.dialogs.observation_dialog import ObservationDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.visit_dialog import VisitDialog
from ui.styles import COLORS
from ui.venue_view import VenueView
from services.batch_report_worker import BatchReportWorker


class MainWindow(QMainWindow):
    """Main application window, orchestrating all UI components and views."""

    def __init__(
        self,
        intern_service: InternService,
        criteria_service: EvaluationCriteriaService,
        grade_service: GradeService,
        observation_service: ObservationService,
        venue_service: VenueService,
        visit_service: VisitService,
        document_service: DocumentService,
        meeting_service: MeetingService,
        report_service: ReportService,
        import_service: ImportService,
        export_service=None,
        communication_service: Optional[CommunicationService] = None,
    ):
        """Initializes services, window properties, and the main UI."""
        super().__init__()
        self.service = intern_service
        self.criteria_service = criteria_service
        self.grade_service = grade_service
        self.obs_service = observation_service
        self.venue_service = venue_service
        self.doc_service = document_service
        self.meeting_service = meeting_service
        self.report_service = report_service
        self.import_service = import_service
        self.export_service = export_service
        self.visit_service = visit_service
        self.comm_service = communication_service

        self.current_filter_mode = "all"
        self.current_doc_type = "Todos"

        self.setWindowTitle("InternManager Pro 2026")
        self.setMinimumSize(1280, 800)
        icon_path = RESOURCES_DIR / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            self.setWindowIcon(qta.icon("fa5s.notes-medical", color=COLORS["primary"]))

        # Apply global stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS["light"]}; }}
            
            /* Styled table for a modern look */
            QTableWidget {{ 
                background-color: {COLORS["white"]}; 
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]};
                gridline-color: transparent;
                outline: none;
                alternate-background-color: #FAFAFA;
            }}
            
            QHeaderView::section {{
                background-color: {COLORS["white"]};
                color: {COLORS["medium"]};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS["light"]};
                font-weight: bold;
                text-transform: uppercase;
                font-size: 12px;
            }}
            
            QTableWidget::item:hover {{
                background-color: #E0E0E0;
                color: {COLORS["dark"]};
            }}
            
            QTableWidget::item:selected {{
                background-color: #BBDEFB;
                color: {COLORS["dark"]};
                border: none;
            }}
        """)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        """Builds the main UI layout with a sidebar and content area."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar for navigation
        self._setup_sidebar(main_layout)

        # 2. Main content area that switches between pages
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # --- Pages ---
        # Page 0: Dashboard
        self.page_dashboard = DashboardView(
            self.service, self.doc_service, self.meeting_service, self.venue_service
        )
        self.page_dashboard.filter_requested.connect(self.handle_dashboard_filter)
        self.content_stack.addWidget(self.page_dashboard)

        # Page 1: Interns List
        self.page_list = QWidget()
        self._setup_list_page()
        self.content_stack.addWidget(self.page_list)

        # Page 2: Venues
        self.page_venues = VenueView(self.venue_service, self.comm_service)
        self.content_stack.addWidget(self.page_venues)

        # Page 3: Criteria
        self.page_criteria = CriteriaView(self.criteria_service)
        self.content_stack.addWidget(self.page_criteria)

        # Connect sidebar navigation to page switching
        self.sidebar_list.currentRowChanged.connect(self.on_sidebar_changed)
        self.sidebar_list.setCurrentRow(0)

    def _setup_sidebar(self, parent_layout):
        """Creates the left-hand navigation sidebar."""
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(260)
        sidebar_frame.setStyleSheet(f"""
            QFrame {{ background-color: {COLORS["sidebar_bg"]}; border: none; }}
            QLabel {{ color: {COLORS["sidebar_text"]}; }}
        """)

        slayout = QVBoxLayout(sidebar_frame)
        slayout.setContentsMargins(0, 0, 0, 20)
        slayout.setSpacing(10)

        # App Title
        app_title = QLabel("InternManager")
        app_title.setStyleSheet(
            "font-size: 20px; font-weight: 900; padding: 30px 20px 5px 20px; letter-spacing: 1px;"
        )
        app_subtitle = QLabel("versão 2.0.0")
        app_subtitle.setStyleSheet(
            f"font-size: 12px; font-weight: normal; color: {COLORS['secondary']}; padding: 0 20px 30px 20px;"
        )
        slayout.addWidget(app_title)
        slayout.addWidget(app_subtitle)

        # Navigation List
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar_list.setStyleSheet(f"""
            QListWidget {{ background-color: transparent; outline: none; }}
            QListWidget::item {{
                color: #A0A0A0;
                padding: 15px 25px;
                border-left: 4px solid transparent;
                font-weight: 500;
                font-size: 14px;
            }}
            QListWidget::item:selected {{
                background-color: #2D2C2B;
                border-left: 4px solid {COLORS["primary"]};
                color: {COLORS["white"]};
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background-color: #2D2C2B;
                color: {COLORS["white"]};
            }}
        """)

        # Add navigation items with icons
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.chart-pie", color="white"), "  Dashboard")
        )
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.user-graduate", color="white"), "  Alunos")
        )
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.hospital", color="white"), "  Locais")
        )
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.tasks", color="white"), "  Critérios")
        )

        slayout.addWidget(self.sidebar_list)
        slayout.addStretch()

        # Sidebar footer for settings
        btn_settings = QPushButton(" Configurações")
        btn_settings.setIcon(qta.icon("fa5s.cog", color=COLORS["secondary"]))
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setStyleSheet(f"""
            QPushButton {{ text-align: left; padding: 15px 25px; background: transparent; color: {COLORS["secondary"]}; border: none; font-weight: 600; }}
            QPushButton:hover {{ color: white; }}
        """)
        btn_settings.clicked.connect(self.open_settings)
        slayout.addWidget(btn_settings)

        parent_layout.addWidget(sidebar_frame)

    def _setup_list_page(self):
        """Creates the 'Interns' page with a table and action buttons."""
        layout = QVBoxLayout(self.page_list)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # --- HEADER (Título + Botões) ---
        header = QHBoxLayout()

        # 1. Título
        lbl = QLabel("Gerenciar Alunos")
        lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {COLORS['dark']};"
        )
        header.addWidget(lbl)

        # Empurra os botões para a direita
        header.addStretch()

        # 2. Botão Novo Aluno
        self.btn_add = QPushButton(" Novo Aluno")
        self.btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.open_add_dialog)  # Conectado apenas UMA vez
        header.addWidget(self.btn_add)

        # 3. Botão Reunião em Grupo
        self.btn_batch = QPushButton(" Reunião em Grupo")
        self.btn_batch.setIcon(qta.icon("fa5s.users", color="white"))
        self.btn_batch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batch.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["secondary"]}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; margin-left: 10px; }}
            QPushButton:hover {{ background-color: #5a6268; }}
        """)
        self.btn_batch.clicked.connect(self.open_batch_meeting)
        header.addWidget(self.btn_batch)

        # Adiciona o layout do cabeçalho ao layout principal APENAS UMA VEZ
        layout.addLayout(header)

        # --- TOOLBAR (Busca + Importar) ---
        actions = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍  Buscar por nome, RA ou local...")
        self.txt_search.setFixedWidth(400)
        self.txt_search.setStyleSheet(f"""
            QLineEdit {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; border-radius: 6px; padding: 10px; color: {COLORS["dark"]}; }}
            QLineEdit:focus {{ border: 1px solid {COLORS["primary"]}; }}
        """)
        self.txt_search.textChanged.connect(self.filter_table)
        actions.addWidget(self.txt_search)

        # 1.1 Filter Status Label and Clear Button
        self.lbl_filter_status = QLabel("")
        self.lbl_filter_status.setStyleSheet(
            f"color: {COLORS['primary']}; font-weight: bold; margin-left: 10px;"
        )
        self.lbl_filter_status.setVisible(False)
        actions.addWidget(self.lbl_filter_status)

        self.btn_clear_filters = QPushButton(" Limpar Filtros")
        self.btn_clear_filters.setIcon(
            qta.icon("fa5s.times-circle", color=COLORS["danger"])
        )
        self.btn_clear_filters.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_filters.setStyleSheet(f"""
            QPushButton {{ background-color: #F8D7DA; color: {COLORS["danger"]}; border: 1px solid #F5C6CB; padding: 8px 15px; border-radius: 6px; font-weight: 600; margin-left: 5px; }}
            QPushButton:hover {{ background-color: #f1b0b7; }}
        """)
        self.btn_clear_filters.clicked.connect(self.reset_filters)
        self.btn_clear_filters.setVisible(False)
        actions.addWidget(self.btn_clear_filters)

        actions.addStretch()

        btn_import = QPushButton(" Importar Planilha")
        btn_import.setIcon(qta.icon("fa5s.file-import", color=COLORS["dark"]))
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; padding: 8px 15px; border-radius: 6px; color: {COLORS["dark"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        btn_import.clicked.connect(self.import_csv_dialog)
        actions.addWidget(btn_import)
        layout.addLayout(actions)

        # --- TABELA ---
        self.table = QTableWidget()

        # Fix palette to ensure selection highlight is the correct color
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#BBDEFB"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["dark"]))
        self.table.setPalette(palette)

        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome Completo", "Local de Estágio", "RA", "Status", "Progresso"]
        )
        self.table.setColumnHidden(0, True)  # Hide internal ID

        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Interactive
        )
        self.table.setColumnWidth(5, 150)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Right-click menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)

        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        # Use custom delegates
        self.table.setItemDelegateForColumn(4, StatusDelegate(self.table))
        self.table.setItemDelegateForColumn(5, ProgressBarDelegate(self.table))
        self.table.doubleClicked.connect(self.open_edit_dialog)

        layout.addWidget(self.table)

        # Action panel below the table
        self._setup_action_panel(layout)

    def _setup_action_panel(self, parent_layout):
        """Creates the bottom panel with actions for the selected intern."""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{ background-color: {COLORS["white"]}; border-radius: 8px; border: 1px solid {COLORS["border"]}; }}
            QMenu {{ background-color: white; border: 1px solid {COLORS["border"]}; padding: 5px; }}
            QMenu::item {{ padding: 8px 25px; border-radius: 4px; color: {COLORS["dark"]}; }}
            QMenu::item:selected {{ background-color: {COLORS["light"]}; color: {COLORS["primary"]}; }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Helper to create styled action buttons
        def make_btn(text, icon, func, primary=False):
            b = QPushButton(text)
            b.setIcon(
                qta.icon(icon, color=COLORS["white"] if primary else COLORS["dark"])
            )
            b.setCursor(Qt.CursorShape.PointingHandCursor)

            if primary:
                style = f"""
                    QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
                    QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
                """
            else:
                style = f"""
                    QPushButton {{ background-color: transparent; border: 1px solid {COLORS["border"]}; padding: 10px 15px; border-radius: 6px; color: {COLORS["dark"]}; font-weight: 600; }}
                    QPushButton:hover {{ background-color: {COLORS["light"]}; border-color: {COLORS["medium"]}; }}
                """
            b.setStyleSheet(style)
            b.clicked.connect(func)
            return b

        # 1. Primary Actions (Icon + Text)
        layout.addWidget(make_btn("Editar", "fa5s.pen", self.open_edit_dialog))
        layout.addWidget(make_btn("Relatório", "fa5s.file-pdf", self.open_report))

        # 2. Communication Group (Icon Only)
        comm_group = QHBoxLayout()
        comm_group.setSpacing(5)

        btn_wa = QPushButton()
        btn_wa.setIcon(qta.icon("fa5b.whatsapp", color="#25D366"))
        btn_wa.setFixedSize(40, 40)
        btn_wa.setToolTip("Enviar WhatsApp")
        btn_wa.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_wa.setStyleSheet(
            f"QPushButton {{ border: 1px solid {COLORS['border']}; border-radius: 6px; background: white; }} QPushButton:hover {{ background: {COLORS['light']}; }}"
        )
        btn_wa.clicked.connect(self.send_whatsapp)

        btn_mail = QPushButton()
        btn_mail.setIcon(qta.icon("fa5s.envelope", color="#EA4335"))
        btn_mail.setFixedSize(40, 40)
        btn_mail.setToolTip("Enviar E-mail")
        btn_mail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_mail.setStyleSheet(
            f"QPushButton {{ border: 1px solid {COLORS['border']}; border-radius: 6px; background: white; }} QPushButton:hover {{ background: {COLORS['light']}; }}"
        )
        btn_mail.clicked.connect(self.send_email)

        comm_group.addWidget(btn_wa)
        comm_group.addWidget(btn_mail)
        layout.addLayout(comm_group)

        # 3. Dropdown Menu (Registrar...)
        self.btn_registrar = QPushButton(" Registrar...")
        self.btn_registrar.setIcon(qta.icon("fa5s.plus", color=COLORS["dark"]))
        self.btn_registrar.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; padding: 10px 20px; border-radius: 6px; color: {COLORS["dark"]}; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
            QPushButton::menu-indicator {{ image: none; }} /* Hides the small arrow if desired, or let it show default */
        """)
        self.btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)

        # Create Menu for the button
        self.action_menu = QMenu(self)
        self.action_menu.addAction(
            qta.icon("fa5s.star", color="#F5A623"),
            "Lançar Notas",
            self.open_grades_dialog,
        )
        self.action_menu.addAction(
            qta.icon("fa5s.folder-open", color="#4A90E2"),
            "Documentos",
            self.open_documents,
        )
        self.action_menu.addAction(
            qta.icon("fa5s.calendar-alt", color="#50E3C2"),
            "Supervisão (Reunião)",
            self.open_meetings,
        )
        self.action_menu.addAction(
            qta.icon("fa5s.map-marked-alt", color="#E91E63"),
            "Visita Técnica",
            self.open_visits,
        )
        self.action_menu.addAction(
            qta.icon("fa5s.eye", color="#9013FE"), "Observação", self.open_observations
        )

        self.btn_registrar.setMenu(self.action_menu)
        layout.addWidget(self.btn_registrar)

        layout.addStretch()

        # 4. Delete Action (Icon Only, isolated at the right)
        btn_del = QPushButton()
        btn_del.setIcon(
            qta.icon("fa5s.trash-alt", color=COLORS["danger"], scale_factor=0.8)
        )
        btn_del.setToolTip("Excluir Aluno")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton {{ 
                background-color: transparent; 
                border: 1px solid #F5C6CB; 
                border-radius: 6px; 
                padding: 8px;
                min-width: 40px;
                min-height: 40px;
            }}
            QPushButton:hover {{ 
                background-color: #F8D7DA; 
                border-color: #F1B0B7; 
            }}
        """)
        btn_del.clicked.connect(self.delete_intern)
        layout.addWidget(btn_del)

        parent_layout.addWidget(container)

    # --- DATA LOGIC ---
    def load_data(self):
        """Fetches all interns and populates the main table with filter metadata."""
        interns = self.service.get_all_interns()
        all_venues = self.venue_service.get_all()
        venue_map = {v.venue_id: v.venue_name for v in all_venues}

        # Pre-fetch IDs for efficient filtering
        pending_ids = self.doc_service.repo.get_intern_ids_with_pending_docs(
            self.current_doc_type
            if self.current_filter_mode == "pending_docs"
            else None
        )
        meeting_ids = (
            self.meeting_service.repo.get_intern_ids_with_meetings_this_month()
        )

        self.table.setRowCount(0)
        for row, intern in enumerate(interns):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)

            id_item = QTableWidgetItem(str(intern.intern_id))
            self.table.setItem(row, 0, id_item)

            name_item = QTableWidgetItem(intern.name)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)

            # Store metadata for filtering without re-querying
            name_item.setData(
                Qt.ItemDataRole.UserRole + 1, intern.intern_id in pending_ids
            )
            name_item.setData(
                Qt.ItemDataRole.UserRole + 2, intern.intern_id in meeting_ids
            )
            name_item.setData(Qt.ItemDataRole.UserRole + 3, intern.venue_id is None)

            self.table.setItem(row, 1, name_item)

            self.table.setItem(
                row, 2, QTableWidgetItem(venue_map.get(intern.venue_id, "-"))
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(str(intern.registration_number or "-"))
            )
            status_item = QTableWidgetItem(intern.status)
            status_item.setData(Qt.ItemDataRole.UserRole, intern.is_near_deadline)
            self.table.setItem(row, 4, status_item)

            # Column 5: Time Progress Bar
            progress_item = QTableWidgetItem(str(intern.time_progress_percent))
            self.table.setItem(row, 5, progress_item)

        # Re-apply filters
        self.apply_filters()

    def filter_table(self, text):
        """Hides or shows table rows based on the current search and filter state."""
        self.apply_filters()

    def apply_filters(self):
        """
        Centralized logic to filter the table based on search text and
        the active dashboard category.
        """
        search = self.txt_search.text().lower().strip()

        # Update UI feedback for active filters
        is_filtered = self.current_filter_mode != "all"
        self.btn_clear_filters.setVisible(is_filtered)
        self.lbl_filter_status.setVisible(is_filtered)

        if is_filtered:
            labels = {
                "no_venue": "Filtrando: Sem Local de Estágio",
                "pending_docs": f"Filtrando: Documento Pendente ({self.current_doc_type})",
                "meetings": "Filtrando: Reuniões no Mês",
            }
            self.lbl_filter_status.setText(labels.get(self.current_filter_mode, ""))

        for row in range(self.table.rowCount()):
            show_row = True

            # 1. Apply Category Filter (from Dashboard)
            name_item = self.table.item(row, 1)
            if not name_item:
                continue

            if self.current_filter_mode == "no_venue":
                if not name_item.data(Qt.ItemDataRole.UserRole + 3):
                    show_row = False
            elif self.current_filter_mode == "pending_docs":
                if not name_item.data(Qt.ItemDataRole.UserRole + 1):
                    show_row = False
            elif self.current_filter_mode == "meetings":
                if not name_item.data(Qt.ItemDataRole.UserRole + 2):
                    show_row = False

            # 2. Apply Text Search (if row still visible)
            if show_row and search:
                match = False
                for col in [1, 2, 3]:
                    item = self.table.item(row, col)
                    if item and search in item.text().lower():
                        match = True
                        break
                show_row = match

            self.table.setRowHidden(row, not show_row)

    def reset_filters(self):
        """Clears all dashboard-initiated filters and returns to 'all' mode."""
        self.current_filter_mode = "all"
        self.current_doc_type = "Todos"
        self.txt_search.clear()
        self.load_data()

    def get_selected_intern(self):
        """
        Retrieves the Intern object for the currently selected table row.

        If no intern is selected, it displays a warning message to the user.

        Returns:
            The Intern object for the selected row, or None if no row is
            selected or the intern cannot be found.
        """
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno na tabela.")
            return None

        item_id = self.table.item(rows[0].row(), 0)
        if not item_id:
            return None
        return self.service.get_by_id(int(item_id.text()))

    # --- DIALOG WRAPPERS ---
    def open_add_dialog(self):
        """Opens a dialog to add a new intern and handles the creation process."""
        d = InternDialog(self, self.venue_service)
        if d.exec():
            try:
                new_id = self.service.add_new_intern(d.get_data())
                if new_id:
                    self.doc_service.create_initial_documents_batch(new_id)
                self.load_data()
                self.page_dashboard.refresh_data()
                QMessageBox.information(self, "Sucesso", "Aluno cadastrado!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro: {e}")

    def open_edit_dialog(self):
        """Opens a dialog to edit the selected intern."""
        i = self.get_selected_intern()
        if not i:
            return
        d = InternDialog(self, self.venue_service, intern=i)
        if d.exec():
            try:
                data = d.get_data()
                i.name = data.name
                i.venue_id = data.venue_id
                i.registration_number = data.registration_number
                i.email = data.email
                i.phone = data.phone
                i.term = data.term
                i.start_date = data.start_date
                i.end_date = data.end_date
                i.working_days = data.working_days
                i.working_hours = data.working_hours

                self.service.update_intern(i)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def send_whatsapp(self):
        """Triggers the WhatsApp communication service for the selected intern."""
        i = self.get_selected_intern()
        if not i:
            return
        if not i.phone:
            QMessageBox.warning(
                self, "Atenção", f"O aluno {i.name} não possui telefone cadastrado."
            )
            return

        if self.comm_service:
            self.comm_service.open_whatsapp(
                i.phone, f"Olá {i.name}, tudo bem? Sou seu supervisor de estágio."
            )
        else:
            QMessageBox.critical(self, "Erro", "Serviço de comunicação não disponível.")

    def send_email(self):
        """Triggers the Email communication service for the selected intern."""
        i = self.get_selected_intern()
        if not i:
            return
        if not i.email:
            QMessageBox.warning(
                self, "Atenção", f"O aluno {i.name} não possui e-mail cadastrado."
            )
            return

        if self.comm_service:
            self.comm_service.open_email(i.email, "Assunto: Acompanhamento de Estágio")
        else:
            QMessageBox.critical(self, "Erro", "Serviço de comunicação não disponível.")

    def delete_intern(self):
        """Deletes the selected intern after a confirmation dialog."""
        i = self.get_selected_intern()
        if not i:
            return
        reply = QMessageBox.question(
            self,
            "Excluir",
            f"Apagar {i.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_intern(i)
            self.load_data()
            self.page_dashboard.refresh_data()

    def open_grades_dialog(self):
        """Opens the grade management dialog for the selected intern."""
        i = self.get_selected_intern()
        if i:
            GradeDialog(self, i, self.criteria_service, self.grade_service).exec()

    def open_documents(self):
        """Opens the document management dialog for the selected intern."""
        i = self.get_selected_intern()
        if i:
            DocumentDialog(self, i, self.doc_service).exec()
            self.page_dashboard.refresh_data()

    def open_meetings(self):
        """Opens the meeting management dialog for the selected intern."""
        i = self.get_selected_intern()
        if i:
            MeetingDialog(self, i, self.meeting_service).exec()
            self.page_dashboard.refresh_data()

    def open_visits(self):
        """Abre o diálogo de gestão de Visitas Técnicas."""
        i = self.get_selected_intern()
        if i:
            VisitDialog(self, i, self.visit_service, self.venue_service).exec()
            self.page_dashboard.refresh_data()

    def open_observations(self):
        """Opens the observation management dialog for the selected intern."""
        i = self.get_selected_intern()
        if i:
            ObservationDialog(self, i, self.obs_service).exec()

    def open_settings(self):
        """Opens the application settings dialog."""
        SettingsDialog(
            self,
            export_service=self.export_service,
            visit_service=self.visit_service,
            intern_service=self.service,
        ).exec()

    def import_csv_dialog(self):
        """
        Opens a file dialog for the user to select a spreadsheet file
        (CSV, XLSX, XLS) to import interns from.
        """
        # Filter to accept both Excel and CSV formats
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Alunos",
            "",
            "Planilhas (*.xlsx *.xls *.csv);;Todos os Arquivos (*)",
        )

        if path:
            try:
                self.import_service.read_file(path)

                # Refresh the UI
                self.load_data()
                self.page_dashboard.refresh_data()

                QMessageBox.information(
                    self, "Sucesso", "Importação concluída com sucesso!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao importar arquivo:\n{str(e)}"
                )

    def open_report(self):
        """Generates and displays the report card for the selected intern."""
        i = self.get_selected_intern()
        if i:
            ReportDialog(
                self,
                i,
                self.grade_service,
                self.criteria_service,
                self.report_service,
                self.venue_service,
                self.doc_service,
                self.meeting_service,
                self.obs_service,
            ).exec()

    def open_batch_meeting(self):
        """Opens a dialog to create a single meeting for multiple interns."""
        d = BatchMeetingDialog(
            self, self.service, self.meeting_service, self.venue_service
        )
        if d.exec():
            self.page_dashboard.refresh_data()

    # --- NAVIGATION ---
    def on_sidebar_changed(self, row):
        """Switches the visible page when a sidebar item is clicked."""
        if row < self.content_stack.count():
            self.content_stack.setCurrentIndex(row)

            # Lazy-load or refresh data for the selected page
            if row == 0:  # Dashboard
                self.page_dashboard.refresh_data()
            elif row == 1:  # Interns
                self.load_data()
            elif row == 2:  # Venues
                self.page_venues.refresh_data()
            elif row == 3:  # Criteria
                self.page_criteria.refresh_data()

    def handle_dashboard_filter(self, card_id: str):
        """
        Switches to the Interns page and applies a specific filter based on
        the KPI card clicked in the dashboard.
        """
        # Switch to Interns page (Index 1)
        self.sidebar_list.setCurrentRow(1)

        # Set the filter mode
        self.current_filter_mode = card_id

        # If filtering by docs, capture the current doc type from dashboard combo
        if card_id == "pending_docs":
            self.current_doc_type = self.page_dashboard.combo_doc_filter.currentText()
        else:
            self.current_doc_type = "Todos"

        # Clear search text to avoid conflicting filters
        self.txt_search.clear()

        # Reload data to pre-calculate the specific IDs for the chosen filter
        self.load_data()

    def _open_context_menu(self, pos):
        # 1. Pega os itens selecionados
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            return

        menu = QMenu(self)
        # Estilo do menu
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; border-radius: 6px; padding: 5px; }}
            QMenu::item {{ padding: 8px 25px; border-radius: 4px; color: {COLORS["dark"]}; font-weight: 500; }}
            QMenu::item:selected {{ background-color: {COLORS["light"]}; color: {COLORS["primary"]}; }}
            QMenu::separator {{ height: 1px; background: {COLORS["border"]}; margin: 5px 10px; }}
        """)

        count = len(selection)

        # --- MULTIPLE INTERNS ---
        if count > 1:
            lbl_info = menu.addAction(f"  {count} Alunos Selecionados")
            lbl_info.setEnabled(False)
            menu.addSeparator()

            # Ação em Lote: Exportar Fotos
            act_export_photos = menu.addAction(
                qta.icon("fa5s.images", color=COLORS["primary"]),
                f"  Exportar Fotos ({count})",
            )
            act_export_photos.triggered.connect(
                lambda: self.export_batch_photos_action(selection)
            )

            # Ação em Lote: Exportar Relatórios PDF
            act_export_reports = menu.addAction(
                qta.icon("fa5s.file-pdf", color="#D0021B"),
                f"  Exportar Relatórios PDF ({count})",
            )
            act_export_reports.triggered.connect(
                lambda: self.export_batch_reports_action(selection)
            )

            menu.addSeparator()

            # Ação em Lote: Aprovação de Documentos
            act_batch_docs = menu.addAction(
                qta.icon("fa5s.check-double", color="#27AE60"),
                f"  Aprovar Documento em Lote ({count})",
            )
            act_batch_docs.triggered.connect(
                lambda: self.approve_batch_documents_action(selection)
            )

        # --- SINGLE INTERN ---
        else:
            # Garante que a linha clicada é a selecionada visualmente
            item = self.table.itemAt(pos)
            if item:
                self.table.selectRow(item.row())

            act_edit = menu.addAction(
                qta.icon("fa5s.pen", color=COLORS["dark"]), "  Editar Cadastro"
            )
            act_edit.triggered.connect(self.open_edit_dialog)

            act_wa = menu.addAction(
                qta.icon("fa5b.whatsapp", color="#25D366"), "  Enviar WhatsApp"
            )
            act_wa.triggered.connect(self.send_whatsapp)

            act_mail = menu.addAction(
                qta.icon("fa5s.envelope", color="#EA4335"), "  Enviar E-mail"
            )
            act_mail.triggered.connect(self.send_email)

            menu.addSeparator()

            act_grades = menu.addAction(
                qta.icon("fa5s.star", color="#F5A623"), "  Lançar Notas"
            )
            act_grades.triggered.connect(self.open_grades_dialog)

            act_docs = menu.addAction(
                qta.icon("fa5s.folder-open", color="#4A90E2"), "  Documentos"
            )
            act_docs.triggered.connect(self.open_documents)

            act_meet = menu.addAction(
                qta.icon("fa5s.calendar-alt", color="#50E3C2"), "  Supervisões"
            )
            act_meet.triggered.connect(self.open_meetings)

            act_visit = menu.addAction(
                qta.icon("fa5s.map-marked-alt", color="#E91E63"), "  Visitas Técnicas"
            )
            act_visit.triggered.connect(self.open_visits)

            act_obs = menu.addAction(
                qta.icon("fa5s.eye", color="#9013FE"), "  Observações"
            )
            act_obs.triggered.connect(self.open_observations)

            menu.addSeparator()

            # Opção Extra: Exportar fotos deste aluno específico
            act_exp_photo = menu.addAction(
                qta.icon("fa5s.images", color=COLORS["medium"]), "  Exportar Fotos"
            )
            act_exp_photo.triggered.connect(
                lambda: self.export_batch_photos_action(selection)
            )

            act_pdf = menu.addAction(
                qta.icon("fa5s.file-pdf", color="#D0021B"), "  Gerar Relatório Final"
            )
            act_pdf.triggered.connect(self.open_report)

            menu.addSeparator()

            act_del = menu.addAction(
                qta.icon("fa5s.trash-alt", color="#D0021B"), "  Excluir Aluno"
            )
            act_del.triggered.connect(self.delete_intern)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def export_batch_photos_action(self, selected_rows):
        """
        Lógica chamada pelo menu de contexto para exportar fotos.
        """
        # 1. Recupera IDs e Nomes dos alunos selecionados
        targets = []
        for index in selected_rows:
            row = index.row()

            item_id = self.table.item(row, 0)
            item_name = self.table.item(row, 1)

            if item_id and item_name:
                targets.append((int(item_id.text()), item_name.text()))

        if not targets:
            return

        # 2. Pergunta onde salvar
        folder = QFileDialog.getExistingDirectory(
            self, "Selecione a Pasta para Salvar as Fotos"
        )
        if not folder:
            return

        # 3. Chama o VisitService
        try:
            success, errors = self.visit_service.export_batch_photos(targets, folder)

            msg = f"Processo finalizado!\n\nFotos copiadas: {success}"
            if errors > 0:
                msg += f"\nErros/Ignorados (sem foto ou falha): {errors}"

            QMessageBox.information(self, "Exportação de Fotos", msg)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na exportação: {e}")

    def export_batch_reports_action(self, selected_rows):
        """
        Orchestrates the background generation of multiple PDF reports.
        """
        # 1. Collect IDs
        intern_ids = []
        for index in selected_rows:
            item_id = self.table.item(index.row(), 0)
            if item_id:
                intern_ids.append(int(item_id.text()))

        if not intern_ids:
            return

        # 2. Get target folder
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta para os Relatórios"
        )
        if not folder:
            return

        # 3. Setup Progress Dialog
        total = len(intern_ids)
        progress = QProgressDialog(
            "Iniciando exportação...", "Cancelar", 0, total, self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Exportação em Massa")
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # 4. Setup Worker
        services = {
            "intern": self.service,
            "venue": self.venue_service,
            "criteria": self.criteria_service,
            "grade": self.grade_service,
            "document": self.doc_service,
            "meeting": self.meeting_service,
            "observation": self.obs_service,
            "visit": self.visit_service,
            "report": self.report_service,
        }

        self.report_worker = BatchReportWorker(folder, intern_ids, services)

        # Connect signals
        self.report_worker.progress_changed.connect(
            lambda count, name: progress.setLabelText(
                f"Gerando relatório ({count}/{total}):\n{name}"
            )
        )
        self.report_worker.progress_changed.connect(
            lambda count, name: progress.setValue(count)
        )

        progress.canceled.connect(self.report_worker.stop)

        def on_finished(success, total):
            progress.close()
            QMessageBox.information(
                self,
                "Exportação Concluída",
                f"Processo finalizado com sucesso!\n\nRelatórios gerados: {success} de {total}",
            )

        def on_error(err_msg):
            progress.close()
            QMessageBox.critical(
                self, "Erro na Exportação", f"Ocorreu um erro crítico:\n{err_msg}"
            )

        self.report_worker.finished.connect(on_finished)
        self.report_worker.error_occurred.connect(on_error)

        # 5. Start
        self.report_worker.start()

    def approve_batch_documents_action(self, selected_rows):
        """
        Handles batch approval of documents for multiple selected interns.
        """
        intern_ids = []
        for index in selected_rows:
            item_id = self.table.item(index.row(), 0)
            if item_id:
                intern_ids.append(int(item_id.text()))

        if not intern_ids:
            return

        d = BatchDocumentDialog(self, len(intern_ids))
        if d.exec():
            doc_name = d.get_selected_document()
            try:
                updated = self.doc_service.approve_batch_documents(intern_ids, doc_name)

                # Update dashboard (since counts changed)
                self.page_dashboard.refresh_data()
                # Reload current table to update marks
                self.load_data()

                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Documento '{doc_name}' aprovado para {updated} alunos.",
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha na aprovação coletiva: {e}")
