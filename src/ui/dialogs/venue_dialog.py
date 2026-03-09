from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.models.venue import Venue
from ui.styles import COLORS


class VenueDialog(QDialog):
    def __init__(self, parent=None, venue: Optional[Venue] = None):
        super().__init__(parent)
        self.venue = venue
        self.setWindowTitle("Gerenciar Local")
        self.setMinimumWidth(500)

        # Estilo CSS Limpo
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["white"]}; }}
            
            QLabel {{ 
                color: {COLORS["medium"]}; 
                font-size: 12px; 
                font-weight: bold; 
                margin-top: 5px;
            }}
            
            QLineEdit {{
                background-color: {COLORS["light"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: {COLORS["dark"]};
            }}
            QLineEdit:focus {{ 
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["primary"]}; 
            }}
        """)

        self._setup_ui()
        if self.venue:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- 1. Cabeçalho ---
        header = QHBoxLayout()

        # Ícone Grande
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.hospital-alt", color=COLORS["primary"]).pixmap(QSize(32, 32))
        )
        header.addWidget(icon_lbl)

        # Textos
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Dados do Local")
        lbl_title.setStyleSheet(f"font-size: 18px; color: {COLORS['dark']}; margin: 0;")
        lbl_sub = QLabel("Cadastre hospitais, clínicas ou laboratórios parceiros.")
        lbl_sub.setStyleSheet(
            f"font-size: 12px; color: {COLORS['secondary']}; font-weight: normal; margin: 0;"
        )

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header.addLayout(title_box)
        header.addStretch()

        layout.addLayout(header)

        # Linha Divisória
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']};")
        layout.addWidget(line)

        # --- 2. Campos (Grid Layout para organização) ---
        # Usaremos um Container Widget para os campos
        fields_widget = QWidget()
        glayout = QGridLayout(fields_widget)
        glayout.setSpacing(15)
        glayout.setContentsMargins(0, 0, 0, 0)

        # -- Nome do Local (Largura Total) --
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Ex: Hospital Santa Casa")
        glayout.addWidget(
            QLabel("Nome do Local *"), 0, 0, 1, 2
        )  # Linha 0, Col 0, Ocupa 1 linha, 2 colunas
        glayout.addWidget(self.txt_name, 1, 0, 1, 2)

        # -- Endereço (Largura Total) --
        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText("Rua, Número, Bairro...")
        glayout.addWidget(QLabel("Endereço Completo"), 2, 0, 1, 2)
        glayout.addWidget(self.txt_address, 3, 0, 1, 2)

        # -- Supervisor --
        self.txt_supervisor = QLineEdit()
        glayout.addWidget(QLabel("Nome do Supervisor"), 4, 0, 1, 2)
        glayout.addWidget(self.txt_supervisor, 5, 0, 1, 2)

        # -- Email (Coluna 1) e Telefone (Coluna 2) --
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("email@exemplo.com")

        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("(00) 00000-0000")

        glayout.addWidget(QLabel("E-mail de Contato"), 6, 0)
        glayout.addWidget(self.txt_email, 7, 0)

        glayout.addWidget(QLabel("Telefone"), 6, 1)
        glayout.addWidget(self.txt_phone, 7, 1)

        layout.addWidget(fields_widget)
        layout.addStretch()  # Empurra tudo para cima

        # --- 3. Botões ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["light"]};
                color: {COLORS["medium"]};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #E1DFDD; color: {COLORS["dark"]}; }}
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Salvar Local")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setIcon(qta.icon("fa5s.check", color="white"))
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_save.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def _load_data(self):
        if not self.venue:
            return
        self.txt_name.setText(self.venue.venue_name)
        self.txt_address.setText(self.venue.address or "")
        self.txt_supervisor.setText(self.venue.supervisor_name or "")
        self.txt_email.setText(self.venue.supervisor_email or "")
        self.txt_phone.setText(self.venue.supervisor_phone or "")

    def validate_and_accept(self):
        from PySide6.QtWidgets import QMessageBox
        from utils.validations import validate_email_format

        name = self.txt_name.text().strip()
        email = self.txt_email.text().strip()

        if not name:
            QMessageBox.warning(
                self, "Campo Obrigatório", "Por favor, informe o Nome do Local."
            )
            self.txt_name.setFocus()
            return

        if email:
            try:
                validate_email_format(email)
            except ValueError as e:
                QMessageBox.warning(self, "E-mail Inválido", str(e))
                self.txt_email.setFocus()
                return

        self.accept()

    def get_data(self) -> Venue:
        v_id = self.venue.venue_id if self.venue else None
        return Venue(
            venue_id=v_id,
            venue_name=self.txt_name.text().strip(),
            address=self.txt_address.text().strip() or None,
            supervisor_name=self.txt_supervisor.text().strip() or None,
            supervisor_email=self.txt_email.text().strip() or None,
            supervisor_phone=self.txt_phone.text().strip() or None,
        )
