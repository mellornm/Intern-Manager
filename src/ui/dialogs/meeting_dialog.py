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
    Controle de Supervisão (Datas e Presença).
    """

    def __init__(self, parent, intern: Intern, service: MeetingService):
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Reuniões: {self.intern.name}")
        self.resize(600, 500)

        # Estilo Global
        self.setStyleSheet(f"""
                    QDialog {{ background-color: {COLORS["light"]}; }}
                    
                    QTableWidget {{ 
                        background-color: {COLORS["white"]}; 
                        border-radius: 8px; 
                        border: 1px solid {COLORS["border"]};
                        gridline-color: transparent;
                        outline: none;
                        
                        /* Força a propriedade do widget Qt */
                        selection-background-color: #E3F2FD;
                        selection-color: {COLORS["dark"]};
                    }}
                    
                    /* Estados específicos para garantir a cor */
                    QTableWidget::item:selected, 
                    QTableWidget::item:selected:focus,
                    QTableWidget::item:selected:active {{
                        background-color: #E3F2FD; /* Azul Bebê */
                        color: {COLORS["dark"]};   /* Texto Escuro */
                        border: none;
                    }}
                    
                    QTableWidget::item:hover {{
                        background-color: #F5F5F5;
                        color: {COLORS["dark"]};
                    }}

                    QHeaderView::section {{
                        background-color: {COLORS["white"]};
                        color: {COLORS["medium"]};
                        padding: 8px;
                        border: none;
                        border-bottom: 2px solid {COLORS["light"]};
                        font-weight: bold;
                    }}
                    
                    QDateEdit {{
                        background-color: {COLORS["white"]};
                        border: 1px solid {COLORS["border"]};
                        border-radius: 4px;
                        padding: 6px;
                        min-height: 25px;
                    }}
                    QDateEdit::drop-down {{ width: 20px; border: none; }}
                    
                    QCheckBox {{ spacing: 8px; font-size: 13px; color: {COLORS["dark"]}; }}
                """)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Header ---
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.calendar-alt", color=COLORS["primary"]).pixmap(QSize(28, 28))
        )

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Registro de Supervisão")
        lbl_title.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {COLORS['dark']};"
        )
        lbl_sub = QLabel(f"Estagiário: {self.intern.name}")
        lbl_sub.setStyleSheet(f"font-size: 12px; color: {COLORS['secondary']};")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)

        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # --- Card de Inserção ---
        input_frame = QFrame()
        input_frame.setStyleSheet(
            f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};"
        )
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)

        # Campos
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setFixedWidth(120)

        self.chk_present = QCheckBox("Aluno Presente?")
        self.chk_present.setChecked(True)

        btn_add = QPushButton(" Lançar Reunião")
        btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 8px 15px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        btn_add.clicked.connect(self.add_meeting)

        input_layout.addWidget(QLabel("Data:"))
        input_layout.addWidget(self.date_edit)
        input_layout.addSpacing(20)
        input_layout.addWidget(self.chk_present)
        input_layout.addStretch()
        input_layout.addWidget(btn_add)

        layout.addWidget(input_frame)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Data da Reunião", "Presença"])
        self.table.setColumnHidden(0, True)

        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
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
        btn_close.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none;"
        )
        btn_close.clicked.connect(self.accept)

        footer.addWidget(btn_del)
        footer.addStretch()
        footer.addWidget(btn_close)

        layout.addLayout(footer)

    def load_data(self):
        if not self.intern.intern_id:
            return

        # CORREÇÃO: O nome correto do método no repo é 'get_by_intern_id'
        meetings = self.service.repo.get_by_intern_id(self.intern.intern_id)

        # Ordenar por data
        meetings.sort(key=lambda x: x.meeting_date, reverse=True)

        self.table.setRowCount(0)
        for row, m in enumerate(meetings):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)

            self.table.setItem(row, 0, QTableWidgetItem(str(m.meeting_id)))

            # Formata data
            try:
                d_obj = QDate.fromString(m.meeting_date, "yyyy-MM-dd")
                date_str = d_obj.toString("dd/MM/yyyy")
            except Exception:
                date_str = m.meeting_date

            self.table.setItem(row, 1, QTableWidgetItem(date_str))

            # Presença com cor
            status = "Presente" if m.is_intern_present else "Ausente"
            item_status = QTableWidgetItem(status)
            if not m.is_intern_present:
                item_status.setForeground(QColor(COLORS["danger"]))
            else:
                item_status.setForeground(QColor(COLORS["success"]))

            # Centraliza e põe negrito
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = item_status.font()
            font.setBold(True)
            item_status.setFont(font)

            self.table.setItem(row, 2, item_status)

    def add_meeting(self):
        if not self.intern.intern_id:
            QMessageBox.warning(self, "Erro", "Salve o aluno antes de lançar reuniões.")
            return

        iso_date = self.date_edit.date().toString("yyyy-MM-dd")
        is_present = self.chk_present.isChecked()

        new_meeting = Meeting(
            intern_id=self.intern.intern_id,
            meeting_date=iso_date,
            is_intern_present=is_present,
        )

        try:
            self.service.add_new_meeting(new_meeting)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")

    def delete_meeting(self):
        row = self.table.currentRow()
        if row < 0:
            return

        if self.intern.intern_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Apagar",
            "Remover este registro?",
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
            QMessageBox.critical(self, "Erro", f"Erro ao excluir: {e}")
