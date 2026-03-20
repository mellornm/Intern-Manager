from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QPushButton,
    QFrame,
    QDateEdit,
    QComboBox,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta

from core.models.intern import Intern
from services.venue_service import VenueService
from ui.dialogs.venue_dialog import VenueDialog
from utils.validations import validate_date_range
from ui.styles import COLORS


class InternDialog(QDialog):
    def __init__(
        self, parent, venue_service: VenueService, intern: Optional[Intern] = None
    ):
        super().__init__(parent)
        self.intern = intern
        self.venue_service = venue_service

        self.setWindowTitle("Ficha do Estagiário")
        self.setMinimumWidth(550)

        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            QLabel {{ color: {COLORS["dark"]}; font-size: 13px; }}
            
            /* --- Campos Normais (Texto e Combo) --- */
            QLineEdit, QComboBox {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
                font-size: 13px;
                color: {COLORS["dark"]};
            }}

            /* --- CORREÇÃO DATA: Padding LARGO --- */
            QDateEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                /* Top/Bottom 3px para não cortar altura */
                /* Right 35px: Muita folga para a seta não encostar no ano */
                padding: 3px 35px 3px 8px; 
                min-height: 20px;
                min-width: 150px; /* Garante largura mínima via CSS também */
                font-size: 13px;
                color: {COLORS["dark"]};
            }}
            
            /* Botão Drop-down Estilizado */
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: {COLORS["border"]};
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: {COLORS["light"]};
            }}
            
            /* Seta Desenhada com CSS */
            QDateEdit::down-arrow {{
                image: none;
                width: 0; 
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS["dark"]};
                margin-right: 2px;
            }}
            
            /* --- Popup do Calendário --- */
            QCalendarWidget QWidget {{
                background-color: {COLORS["white"]};
                color: {COLORS["dark"]};
                alternate-background-color: #FAFAFA;
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS["dark"]};
                background-color: transparent;
                icon-size: 24px;
            }}
            QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
            QCalendarWidget QSpinBox {{
                background-color: {COLORS["white"]};
                color: {COLORS["dark"]};
                selection-background-color: {COLORS["primary"]};
                selection-color: white;
            }}

            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{ 
                border: 1px solid {COLORS["primary"]}; 
            }}
        """)

        self._setup_ui()
        self.load_venues()

        if self.intern:
            self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header_title = "Editar Aluno" if self.intern else "Novo Aluno"
        lbl_head = QLabel(header_title)
        lbl_head.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {COLORS['primary']}; margin-bottom: 10px;"
        )
        layout.addWidget(lbl_head)

        # Form Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(
            f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};"
        )
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Personal
        self.txt_name = QLineEdit()
        self.txt_ra = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Ex: 11999998888")

        # Venue
        self.combo_venue = QComboBox()
        self.btn_add_venue = QPushButton()
        self.btn_add_venue.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add_venue.setFixedSize(36, 36)
        self.btn_add_venue.setToolTip("Cadastrar novo local")
        self.btn_add_venue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_venue.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["success"]}; border-radius: 4px; border: none; }}
            QPushButton:hover {{ background-color: #0E6A0E; }}
        """)
        self.btn_add_venue.clicked.connect(self.quick_add_venue)

        venue_layout = QHBoxLayout()
        venue_layout.addWidget(self.combo_venue)
        venue_layout.addWidget(self.btn_add_venue)

        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate())
        self.date_start.setFixedWidth(160)

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate().addMonths(6))
        self.date_end.setFixedWidth(160)

        # Semestre
        self.combo_term = QComboBox()
        terms = [f"{y}/{s}" for y in range(2025, 2030) for s in [1, 2]]
        self.combo_term.addItems(terms)

        # Jornada e Horário
        self.txt_hours = QLineEdit()
        self.txt_hours.setPlaceholderText("Ex: 9h - 15h")

        self.txt_days = QLineEdit()
        self.txt_days.setPlaceholderText("Ex: Seg a Sex")

        hours_layout = QHBoxLayout()
        hours_layout.addWidget(self.txt_hours)
        hours_layout.addWidget(QLabel("   Dias:"))
        hours_layout.addWidget(self.txt_days)

        # Helper Labels
        def lbl(t):
            lbl_style = QLabel(t)
            lbl_style.setStyleSheet("font-weight: bold;")
            return lbl_style

        form_layout.addRow(lbl("Nome Completo *:"), self.txt_name)
        form_layout.addRow(lbl("RA (Matrícula) *:"), self.txt_ra)
        form_layout.addRow(lbl("E-mail:"), self.txt_email)
        form_layout.addRow(lbl("WhatsApp/Telefone:"), self.txt_phone)
        form_layout.addRow(lbl("Local de Estágio:"), venue_layout)
        form_layout.addRow(lbl("Semestre:"), self.combo_term)
        form_layout.addRow(lbl("Horários:"), hours_layout)

        date_layout = QHBoxLayout()
        date_layout.addWidget(lbl("Início:"))
        date_layout.addWidget(self.date_start)
        date_layout.addSpacing(20)
        date_layout.addWidget(lbl("Término:"))
        date_layout.addWidget(self.date_end)

        form_layout.addRow(lbl("Vigência:"), date_layout)

        layout.addWidget(form_frame)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: 1px solid {COLORS["secondary"]}; color: {COLORS["secondary"]}; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Salvar Aluno")
        self.btn_save.setIcon(qta.icon("fa5s.check", color="white"))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 25px; border-radius: 6px; font-weight: bold; font-size: 14px; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_save.clicked.connect(self.save_data)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_venues(self):
        current_data = self.combo_venue.currentData()
        self.combo_venue.clear()
        self.combo_venue.addItem("--- Selecione ---", None)
        venues = self.venue_service.get_all()
        for v in venues:
            self.combo_venue.addItem(v.venue_name, v.venue_id)
        if current_data:
            idx = self.combo_venue.findData(current_data)
            if idx >= 0:
                self.combo_venue.setCurrentIndex(idx)

    def quick_add_venue(self):
        dialog = VenueDialog(self)
        if dialog.exec():
            try:
                new_data = dialog.get_data()
                new_id = self.venue_service.add_new_venue(new_data)
                self.load_venues()
                idx = self.combo_venue.findData(new_id)
                if idx >= 0:
                    self.combo_venue.setCurrentIndex(idx)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar local: {e}")

    def load_data(self):
        if not self.intern:
            return
        self.txt_name.setText(str(self.intern.name or ""))
        self.txt_ra.setText(str(self.intern.registration_number or ""))
        self.txt_email.setText(self.intern.email or "")
        self.txt_phone.setText(self.intern.phone or "")
        self.combo_term.setCurrentText(self.intern.term)

        # Carregamento correto dos novos campos
        self.txt_hours.setText(self.intern.working_hours or "")
        self.txt_days.setText(self.intern.working_days or "")

        if self.intern.venue_id:
            idx = self.combo_venue.findData(self.intern.venue_id)
            if idx >= 0:
                self.combo_venue.setCurrentIndex(idx)

        # Converter YYYY-MM-DD para QDate
        # Importante: Se o dado no banco ainda estiver sujo (ex: "Segunda a Sexta"),
        # o QDate.fromString vai retornar inválido, e o setDate não fará nada (data ficará a atual).
        if self.intern.start_date:
            d = QDate.fromString(self.intern.start_date, "yyyy-MM-dd")
            if d.isValid():
                self.date_start.setDate(d)

        if self.intern.end_date:
            d = QDate.fromString(self.intern.end_date, "yyyy-MM-dd")
            if d.isValid():
                self.date_end.setDate(d)

    def save_data(self):
        from utils.validations import validate_email_format

        name = self.txt_name.text().strip()
        ra = self.txt_ra.text().strip()
        email = self.txt_email.text().strip()

        if not name:
            QMessageBox.warning(self, "Erro", "Nome é obrigatório.")
            self.txt_name.setFocus()
            return
        if not ra:
            QMessageBox.warning(self, "Erro", "RA é obrigatório.")
            self.txt_ra.setFocus()
            return

        if email:
            try:
                validate_email_format(email)
            except ValueError as e:
                QMessageBox.warning(self, "E-mail Inválido", str(e))
                self.txt_email.setFocus()
                return

        s_str = self.date_start.date().toString("dd/MM/yyyy")
        e_str = self.date_end.date().toString("dd/MM/yyyy")

        try:
            validate_date_range(s_str, e_str)
        except ValueError as e:
            QMessageBox.warning(self, "Data Inválida", str(e))
            return

        self.accept()

    def get_data(self) -> Intern:
        cid = self.intern.intern_id if self.intern else None
        return Intern(
            intern_id=cid,
            name=self.txt_name.text().strip(),
            registration_number=self.txt_ra.text().strip(),
            email=self.txt_email.text().strip(),
            phone=self.txt_phone.text().strip() or None,
            venue_id=self.combo_venue.currentData(),
            term=self.combo_term.currentText(),
            start_date=self.date_start.date().toString("yyyy-MM-dd"),
            end_date=self.date_end.date().toString("yyyy-MM-dd"),
            # Campos novos
            working_hours=self.txt_hours.text().strip() or None,
            working_days=self.txt_days.text().strip() or None,
        )
