from datetime import datetime

import qtawesome as qta
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.models.intern import Intern
from core.models.observation import Observation
from services.observation_service import ObservationService
from ui.styles import COLORS


class ObservationDialog(QDialog):
    def __init__(self, parent, intern: Intern, service: ObservationService):
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Observações: {self.intern.name}")
        self.resize(550, 650)

        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 10px;
                color: {COLORS["dark"]};
            }}
            QListWidget::item:selected {{
                border: 1px solid {COLORS["primary"]};
                background-color: #E3F2FD; /* Azul bem clarinho */
                color: {COLORS["dark"]};
            }}
            
            QTextEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }}
            QTextEdit:focus {{ border: 1px solid {COLORS["primary"]}; }}
        """)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # --- Header ---
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            qta.icon("fa5s.sticky-note", color=COLORS["warning"]).pixmap(QSize(28, 28))
        )
        lbl = QLabel("Caderno de Observações")
        lbl.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {COLORS['dark']};"
        )
        header.addWidget(icon)
        header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)

        # --- Lista (Feed) ---
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        # Padding interno nos itens
        self.list_widget.setSpacing(5)
        layout.addWidget(self.list_widget)

        # Botão de apagar (pequeno, alinhado à direita do feed)
        h_del = QHBoxLayout()
        h_del.addStretch()
        self.btn_del = QPushButton(" Apagar Selecionada")
        self.btn_del.setIcon(qta.icon("fa5s.trash", color=COLORS["danger"]))
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setStyleSheet(
            f"color: {COLORS['danger']}; background: transparent; border: none; font-weight: 600;"
        )
        self.btn_del.clicked.connect(self.delete_selected)
        h_del.addWidget(self.btn_del)
        layout.addLayout(h_del)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']}")
        layout.addWidget(line)

        # --- Nova Nota ---
        layout.addWidget(QLabel("<b>Nova Anotação:</b>"))
        self.txt_new = QTextEdit()
        self.txt_new.setPlaceholderText(
            "Escreva aqui detalhes sobre o desempenho, comportamento ou incidentes..."
        )
        self.txt_new.setMaximumHeight(100)
        layout.addWidget(self.txt_new)

        # Botão Salvar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Fechar")
        btn_cancel.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none;"
        )
        btn_cancel.clicked.connect(self.accept)

        self.btn_add = QPushButton(" Adicionar Nota")
        self.btn_add.setIcon(qta.icon("fa5s.paper-plane", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 8px 20px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.add_observation)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_add)
        layout.addLayout(btn_layout)

    def load_data(self):
        if not self.intern.intern_id:
            return

        obs_list = self.service.get_by_intern_id(self.intern.intern_id)
        self.list_widget.clear()

        self.list_widget.setIconSize(QSize(20, 20))

        for obs in obs_list:
            data_display = "Data desconhecida"
            if obs.last_update:
                try:
                    dt_obj = datetime.strptime(
                        str(obs.last_update), "%Y-%m-%d %H:%M:%S"
                    )
                    data_display = dt_obj.strftime("%d/%m/%Y às %H:%M")
                except ValueError:
                    data_display = str(obs.last_update)

            texto_item = f"{data_display}\n{obs.observation}"

            item = QListWidgetItem(texto_item)

            item.setIcon(qta.icon("fa5s.calendar-alt", color=COLORS["secondary"]))

            item.setData(Qt.ItemDataRole.UserRole, obs)
            self.list_widget.addItem(item)

        self.list_widget.scrollToTop()

    def add_observation(self):
        if not self.intern.intern_id:
            QMessageBox.warning(self, "Erro", "Salve o aluno primeiro.")
            return

        content = self.txt_new.toPlainText().strip()
        if not content:
            return

        new_obs = Observation(intern_id=self.intern.intern_id, observation=content)

        try:
            self.service.add_new_observation(new_obs)
            self.txt_new.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        obs_obj = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(obs_obj, Observation):
            return

        if (
            QMessageBox.question(
                self,
                "Confirmar",
                "Apagar essa anotação?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            try:
                self.service.delete_observation(obs_obj)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro: {e}")
