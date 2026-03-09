from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QDateEdit,
    QMessageBox,
    QComboBox,
    QLineEdit,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from ui.styles import COLORS
from core.models.meeting import Meeting


class BatchMeetingDialog(QDialog):
    """
    Dialog for creating supervisory meetings for multiple interns simultaneously.

    This dialog allows the user to filter interns by venue, select participants
    from a list, and record a collective meeting with a specific date and topic.
    """

    def __init__(self, parent, intern_service, meeting_service, venue_service):
        """
        Initializes the batch meeting dialog.

        Args:
            parent: The parent widget.
            intern_service: Service for intern data operations.
            meeting_service: Service for meeting data operations.
            venue_service: Service for venue data operations.
        """
        super().__init__(parent)
        self.intern_service = intern_service
        self.meeting_service = meeting_service
        self.venue_service = venue_service
        self.all_interns_data = []

        self.setWindowTitle("Agendar Reunião em Grupo")
        self.setMinimumSize(550, 650)
        self.setStyleSheet(f"background-color: {COLORS['light']};")

        self._setup_ui()
        self._load_interns()

    def _setup_ui(self):
        """Builds the dialog's layout and widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        # Title
        lbl = QLabel("Nova Reunião Coletiva")
        lbl.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {COLORS['primary']};"
        )
        layout.addWidget(lbl)

        # Venue Filter
        filter_layout = QHBoxLayout()
        self.combo_venue = QComboBox()
        self.combo_venue.setStyleSheet(f"""
            QComboBox {{ 
                background-color: {COLORS["white"]}; 
                border: 1px solid {COLORS["border"]}; 
                border-radius: 6px; 
                padding: 8px; 
            }}
        """)
        self.combo_venue.addItem("Todos os Locais", None)
        for v in self.venue_service.get_all():
            self.combo_venue.addItem(v.venue_name, v.venue_id)
        self.combo_venue.currentIndexChanged.connect(self._filter_list)

        lbl_filter = QLabel("Filtrar por Local:")
        lbl_filter.setStyleSheet("font-weight: 600;")
        filter_layout.addWidget(lbl_filter)
        filter_layout.addWidget(self.combo_venue)
        layout.addLayout(filter_layout)

        # Participant Selection List
        lbl_sel = QLabel("Selecione os participantes:")
        lbl_sel.setStyleSheet("font-weight: 600; margin-top: 5px;")
        layout.addWidget(lbl_sel)

        self.list_interns = QListWidget()
        self.list_interns.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 8px;
                outline: none;
            }}
            QListWidget::item {{
                color: {COLORS["dark"]};
                padding: 10px;
                border-bottom: 1px solid {COLORS["light"]};
            }}
            QListWidget::item:hover {{
                background-color: #F8F9FA;
            }}
            
            QListWidget::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {COLORS["medium"]};
                border-radius: 5px;
                background-color: {COLORS["white"]};
                margin-right: 12px;
            }}
            
            QListWidget::indicator:checked {{
                background-color: {COLORS["primary"]};
                border-color: {COLORS["primary"]};
            }}
        """)
        layout.addWidget(self.list_interns)

        # "Select All" Checkbox
        self.chk_all = QCheckBox("Selecionar Todos os Alunos Listados")
        self.chk_all.setStyleSheet("font-weight: 500; font-size: 13px;")
        self.chk_all.stateChanged.connect(self._toggle_all)
        layout.addWidget(self.chk_all)

        # Form Divider
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {COLORS['border']}; margin: 5px 0;")
        layout.addWidget(line)

        # Meeting Details (Date & Topic)
        details_layout = QVBoxLayout()
        details_layout.setSpacing(12)

        # Date Row
        date_row = QHBoxLayout()
        lbl_date = QLabel("Data da Reunião:")
        lbl_date.setFixedWidth(120)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setStyleSheet(f"""
            QDateEdit {{ 
                padding: 8px; 
                background-color: {COLORS["white"]}; 
                border: 1px solid {COLORS["border"]}; 
                border-radius: 6px; 
            }}
        """)
        date_row.addWidget(lbl_date)
        date_row.addWidget(self.date_edit)
        date_row.addStretch()
        details_layout.addLayout(date_row)

        # Topic Row
        topic_row = QHBoxLayout()
        lbl_topic = QLabel("Assunto / Pauta:")
        lbl_topic.setFixedWidth(120)
        self.txt_topic = QLineEdit()
        self.txt_topic.setPlaceholderText(
            "Ex: Reunião Coletiva de Orientação, Feedback de Grupo..."
        )
        self.txt_topic.setStyleSheet(f"""
            QLineEdit {{ 
                padding: 8px; 
                background-color: {COLORS["white"]}; 
                border: 1px solid {COLORS["border"]}; 
                border-radius: 6px; 
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS["primary"]}; }}
        """)
        topic_row.addWidget(lbl_topic)
        topic_row.addWidget(self.txt_topic)
        details_layout.addLayout(topic_row)

        layout.addLayout(details_layout)

        # Action Buttons
        btns_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ 
                background-color: transparent; color: {COLORS["secondary"]}; 
                padding: 10px 20px; border-radius: 6px; font-weight: 600; 
            }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Confirmar Agendamento")
        self.btn_save.setIcon(qta.icon("fa5s.check-double", color="white"))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {COLORS["success"]}; color: white; 
                padding: 12px 25px; border-radius: 8px; font-weight: bold; border: none; 
            }}
            QPushButton:hover {{ background-color: #0E6A0E; }}
        """)
        self.btn_save.clicked.connect(self._save_batch)

        btns_layout.addWidget(btn_cancel)
        btns_layout.addStretch()
        btns_layout.addWidget(self.btn_save)
        layout.addLayout(btns_layout)

    def _load_interns(self):
        """Initial load of all interns from the service."""
        self.all_interns_data = self.intern_service.get_all_interns()
        self._filter_list()

    def _filter_list(self):
        """Filters the participant list based on the selected venue."""
        venue_id = self.combo_venue.currentData()
        self.list_interns.clear()

        for intern in self.all_interns_data:
            if venue_id is None or intern.venue_id == venue_id:
                item = QListWidgetItem(
                    f"{intern.name} (RA: {intern.registration_number or 'S/RA'})"
                )

                # Store ID and configure as checkable
                item.setData(Qt.ItemDataRole.UserRole, intern.intern_id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)

                self.list_interns.addItem(item)

        # Uncheck "Select All" when list is refreshed
        self.chk_all.setCheckState(Qt.CheckState.Unchecked)

    def _toggle_all(self, state):
        """Toggles all visible items in the list."""
        is_checked = state == Qt.CheckState.Checked.value or state == 2
        for i in range(self.list_interns.count()):
            item = self.list_interns.item(i)
            item.setCheckState(
                Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked
            )

    def _save_batch(self):
        """Saves a meeting record for each selected intern."""
        selected_ids = []
        for i in range(self.list_interns.count()):
            item = self.list_interns.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_ids.append(item.data(Qt.ItemDataRole.UserRole))

        if not selected_ids:
            QMessageBox.warning(
                self, "Atenção", "Selecione ao menos um aluno para a reunião!"
            )
            return

        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        topic = self.txt_topic.text().strip() or "General Follow-up"

        count = 0
        try:
            for iid in selected_ids:
                meeting = Meeting(
                    intern_id=iid,
                    meeting_date=date_str,
                    is_intern_present=True,
                    meeting_topic=topic,
                )
                self.meeting_service.add_new_meeting(meeting)
                count += 1

            QMessageBox.information(
                self,
                "Sucesso",
                f"Registro concluído! {count} reuniões criadas com sucesso.",
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao processar reuniões: {e}")
