from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QDateEdit,
    QCheckBox,
    QLabel,
    QFrame,
    QLineEdit,
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QColor
import qtawesome as qta

from core.models.intern import Intern
from core.models.meeting import Meeting
from services.meeting_service import MeetingService
from ui.styles import COLORS


class MeetingDialog(QDialog):
    """
    Dialog for managing supervisory meetings (dates, topics, and presence).

    This dialog allows users to view, add, and delete meeting records for a
    specific intern. It tracks the meeting date, the topic discussed, and
    whether the intern was present.
    """

    def __init__(self, parent, intern: Intern, service: MeetingService):
        """
        Initializes the meeting management dialog.

        Args:
            parent: The parent widget.
            intern (Intern): The intern whose meetings are being managed.
            service (MeetingService): The service for meeting data operations.
        """
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Reuniões: {self.intern.name}")
        self.resize(750, 600)  # Increased size to accommodate the topic field

        # Global Stylesheet
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            
            QTableWidget {{ 
                background-color: {COLORS["white"]}; 
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]};
                gridline-color: transparent;
                outline: none;
                alternate-background-color: #FAFAFA;
            }}
            
            QTableWidget::item:selected {{
                background-color: #E3F2FD;
                color: {COLORS["dark"]};
            }}
            
            QTableWidget::item:hover {{
                background-color: #F5F5F5;
                color: {COLORS["dark"]};
            }}

            QHeaderView::section {{
                background-color: {COLORS["white"]};
                color: {COLORS["medium"]};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {COLORS["light"]};
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
            }}
            
            QDateEdit, QLineEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS["dark"]};
            }}
            
            QDateEdit:focus, QLineEdit:focus {{
                border: 1px solid {COLORS["primary"]};
            }}

            QCheckBox {{ spacing: 8px; font-size: 13px; color: {COLORS["dark"]}; }}
        """)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        """Builds the dialog's layout and widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # --- Header ---
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.calendar-alt", color=COLORS["primary"]).pixmap(QSize(32, 32))
        )

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Registro de Supervisão")
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {COLORS['dark']};"
        )
        lbl_sub = QLabel(f"Estagiário: {self.intern.name}")
        lbl_sub.setStyleSheet(f"font-size: 13px; color: {COLORS['secondary']};")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)

        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # --- Input Card (New Meeting Form) ---
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_frame.setStyleSheet(f"""
            QFrame#inputFrame {{
                background-color: {COLORS["white"]}; 
                border-radius: 10px; 
                border: 1px solid {COLORS["border"]};
            }}
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(15)

        # Row 1: Date and Presence
        row1 = QHBoxLayout()

        # Date field
        date_box = QVBoxLayout()
        date_box.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setFixedWidth(140)
        date_box.addWidget(self.date_edit)
        row1.addLayout(date_box)

        row1.addSpacing(30)

        # Presence checkbox
        presence_box = QVBoxLayout()
        presence_box.addStretch()
        self.chk_present = QCheckBox("Estudante Presente?")
        self.chk_present.setChecked(True)
        presence_box.addWidget(self.chk_present)
        row1.addLayout(presence_box)

        row1.addStretch()
        input_layout.addLayout(row1)

        # Row 2: Topic and Add Button
        row2 = QHBoxLayout()
        topic_box = QVBoxLayout()
        topic_box.addWidget(QLabel("Assunto / Pauta:"))
        self.txt_topic = QLineEdit()
        self.txt_topic.setPlaceholderText(
            "Ex: Orientação de estágio, Feedback mensal, Plano de trabalho..."
        )
        topic_box.addWidget(self.txt_topic)
        row2.addLayout(topic_box)

        btn_add = QPushButton(" Lançar")
        btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setFixedSize(120, 40)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                border-radius: 8px; font-weight: bold; margin-top: 20px;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        btn_add.clicked.connect(self.add_meeting)
        row2.addWidget(btn_add)

        input_layout.addLayout(row2)
        layout.addWidget(input_frame)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Assunto", "Presença"])
        self.table.setColumnHidden(0, True)

        # Resizing
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # --- Footer ---
        footer = QHBoxLayout()
        btn_del = QPushButton(" Excluir Selecionada")
        btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(
            f"background: transparent; color: {COLORS['danger']}; border: none; font-weight: 600;"
        )
        btn_del.clicked.connect(self.delete_meeting)

        btn_close = QPushButton("Fechar")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; 
                padding: 8px 25px; border-radius: 6px; color: {COLORS["secondary"]}; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        btn_close.clicked.connect(self.accept)

        footer.addWidget(btn_del)
        footer.addStretch()
        footer.addWidget(btn_close)

        layout.addLayout(footer)

    def load_data(self):
        """Fetches and displays meeting records for the current intern."""
        if not self.intern.intern_id:
            return

        meetings = self.service.get_by_intern_id(self.intern.intern_id)

        # Results are already ordered by the repository, but we ensure it here
        meetings.sort(key=lambda x: x.meeting_date, reverse=True)

        self.table.setRowCount(0)
        for row, m in enumerate(meetings):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 45)

            # Column 0: ID (Hidden)
            self.table.setItem(row, 0, QTableWidgetItem(str(m.meeting_id)))

            # Column 1: Date
            try:
                d_obj = QDate.fromString(m.meeting_date, "yyyy-MM-dd")
                date_str = d_obj.toString("dd/MM/yyyy")
            except Exception:
                date_str = m.meeting_date
            self.table.setItem(row, 1, QTableWidgetItem(date_str))

            # Column 2: Topic
            topic_item = QTableWidgetItem(m.meeting_topic or "General Follow-up")
            self.table.setItem(row, 2, topic_item)

            # Column 3: Presence (with color coding)
            status = "Presente" if m.is_intern_present else "Ausente"
            item_status = QTableWidgetItem(status)

            if not m.is_intern_present:
                item_status.setForeground(QColor(COLORS["danger"]))
            else:
                item_status.setForeground(QColor(COLORS["success"]))

            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = item_status.font()
            font.setBold(True)
            item_status.setFont(font)

            self.table.setItem(row, 3, item_status)

    def add_meeting(self):
        """Collects data from UI and creates a new meeting record."""
        if not self.intern.intern_id:
            QMessageBox.warning(
                self, "Atenção", "O aluno deve estar salvo antes de registrar reuniões."
            )
            return

        iso_date = self.date_edit.date().toString("yyyy-MM-dd")
        is_present = self.chk_present.isChecked()
        topic = self.txt_topic.text().strip() or "General Follow-up"

        new_meeting = Meeting(
            intern_id=self.intern.intern_id,
            meeting_date=iso_date,
            is_intern_present=is_present,
            meeting_topic=topic,
        )

        try:
            self.service.add_new_meeting(new_meeting)
            self.txt_topic.clear()  # Reset topic for next entry
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar registro: {e}")

    def delete_meeting(self):
        """Removes the currently selected meeting record."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma reunião para excluir.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente remover este registro de reunião?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.No:
            return

        item_id = self.table.item(row, 0)
        if not item_id:
            return

        meeting_id = int(item_id.text())

        try:
            self.service.delete_meeting(meeting_id)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao excluir registro: {e}")
