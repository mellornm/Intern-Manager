import os

import qtawesome as qta
from PySide6.QtCore import QDate, QSize, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from config import USER_DATA_ROOT
from core.models.intern import Intern
from core.models.visit import Visit
from services.venue_service import VenueService
from services.visit_service import VisitService
from ui.styles import COLORS


class VisitDialog(QDialog):
    """

    Dialog for managing intern supervision visits.

    Provides an interface to list, register, delete, and view visit photos.
    Integrates with VisitService (persistence, photo saving) and VenueService (list of locations).

    Main responsibilities:
        - Load available locations (load_venues).
        - Load and display intern visits (load_data).
        - Select and attach a photo to a visit (select_photo).
        - Create a new visit with the option to save a photo (add_visit).
        - Delete a selected visit (delete_visit).
        - Open photo in the system viewer (view_photo).

    Attributes:

        intern (Intern): Intern related to visits.
        service (VisitService): Service responsible for visit operations.
        venue_service (VenueService): Service to obtain locations.
        selected_photo_path (Optional[str]): Temporary path of the photo selected by the user.
        table (QTableWidget): Widget that lists the visits.

    """

    def __init__(
        self,
        parent,
        intern: Intern,
        service: VisitService,
        venue_service: VenueService,
    ):
        super().__init__(parent)
        self.intern = intern
        self.service = service
        self.venue_service = venue_service
        self.selected_photo_path = None

        self.setWindowTitle(f"Visitas Técnicas: {self.intern.name}")
        self.resize(750, 600)

        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            
            QTableWidget {{ 
                background-color: {COLORS["white"]}; 
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]};
                selection-background-color: #E3F2FD;
                selection-color: {COLORS["dark"]};
            }}
            
            QHeaderView::section {{
                background-color: {COLORS["white"]};
                color: {COLORS["medium"]};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {COLORS["light"]};
                font-weight: bold;
            }}

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
            
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 6px;
                min-height: 25px;
            }}
            
            QLabel {{ color: {COLORS["dark"]}; }}
        """)

        self._setup_ui()
        self.load_venues()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.map-marked-alt", color=COLORS["primary"]).pixmap(
                QSize(32, 32)
            )
        )

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Visitas de Supervisão")
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

        input_frame = QFrame()
        input_frame.setStyleSheet(
            f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};"
        )
        form_layout = QVBoxLayout(input_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(10)

        row1 = QHBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setFixedWidth(120)

        self.combo_venue = QComboBox()
        self.combo_venue.setPlaceholderText("Selecione o Local...")

        row1.addWidget(QLabel("Data:"))
        row1.addWidget(self.date_edit)
        row1.addSpacing(20)
        row1.addWidget(QLabel("Local da Visita:"))
        row1.addWidget(self.combo_venue, stretch=1)

        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.txt_obs = QLineEdit()
        self.txt_obs.setPlaceholderText("Observações sobre a visita (opcional)...")
        row2.addWidget(QLabel("Obs:"))
        row2.addWidget(self.txt_obs)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()

        self.btn_photo = QPushButton(" Anexar Foto")
        self.btn_photo.setIcon(qta.icon("fa5s.camera", color=COLORS["medium"]))
        self.btn_photo.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["light"]}; border: 1px solid {COLORS["border"]}; color: {COLORS["dark"]}; padding: 6px 12px; border-radius: 4px; }}
            QPushButton:hover {{ background-color: #E0E0E0; }}
        """)
        self.btn_photo.clicked.connect(self.select_photo)

        self.lbl_photo_status = QLabel("Nenhuma foto selecionada")
        self.lbl_photo_status.setStyleSheet(
            f"color: {COLORS['secondary']}; font-style: italic; font-size: 11px;"
        )

        self.btn_add = QPushButton(" Registrar Visita")
        self.btn_add.setIcon(qta.icon("fa5s.check", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 8px 20px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.add_visit)

        row3.addWidget(self.btn_photo)
        row3.addWidget(self.lbl_photo_status)
        row3.addStretch()
        row3.addWidget(self.btn_add)

        form_layout.addLayout(row3)
        layout.addWidget(input_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Local", "Observação", "Foto"]
        )
        self.table.setColumnHidden(0, True)

        self.table.setShowGrid(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{ 
                background-color: {COLORS["white"]};
                gridline-color: #E0E0E0; /* Linha cinza suave */
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]};
                selection-background-color: #E3F2FD;
                selection-color: {COLORS["dark"]};
            }}
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 180)

        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 60)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        self.table.doubleClicked.connect(self.view_photo)

        layout.addWidget(self.table)

        # --- Footer ---
        footer = QHBoxLayout()
        btn_del = QPushButton(" Excluir Selecionada")
        btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(
            f"background: transparent; color: {COLORS['danger']}; border: none; font-weight: 600;"
        )
        btn_del.clicked.connect(self.delete_visit)

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

    def load_venues(self):
        """Carrega os locais no ComboBox e seleciona o do aluno."""
        self.combo_venue.clear()
        venues = self.venue_service.get_all()

        for v in venues:
            self.combo_venue.addItem(v.venue_name, int(v.venue_id))

        if self.intern.venue_id and int(self.intern.venue_id) > 0:
            target_id = int(self.intern.venue_id)

            idx = self.combo_venue.findData(target_id)

            if idx >= 0:
                self.combo_venue.setCurrentIndex(idx)
            else:
                print(f"Aviso: Local ID {target_id} não encontrado na lista.")

    def load_data(self):
        if not self.intern.intern_id:
            return

        visits = self.service.get_visits_by_intern(self.intern.intern_id)

        all_venues = self.venue_service.get_all()
        venue_map = {v.venue_id: v.venue_name for v in all_venues}

        self.table.setRowCount(0)
        for row, v in enumerate(visits):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 45)

            self.table.setItem(row, 0, QTableWidgetItem(str(v.visit_id)))

            try:
                d_obj = QDate.fromString(v.visit_date, "yyyy-MM-dd")
                date_str = d_obj.toString("dd/MM/yyyy")
            except Exception:
                date_str = v.visit_date

            item_date = QTableWidgetItem(date_str)
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_date)

            # 2: Local
            venue_name = venue_map.get(v.venue_id, "Desconhecido")
            self.table.setItem(row, 2, QTableWidgetItem(venue_name))

            # 3: Observação
            self.table.setItem(row, 3, QTableWidgetItem(v.observation or "-"))

            # 4: Ícone da Foto
            photo_item = QTableWidgetItem()
            photo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if v.photo_path:
                # Ícone de Câmera Azul se tiver foto
                icon = qta.icon("fa5s.image", color=COLORS["primary"])
                photo_item.setIcon(icon)
                photo_item.setToolTip(f"Duplo clique para abrir: {v.photo_path}")
                photo_item.setData(Qt.ItemDataRole.UserRole, v.photo_path)
            else:
                # Ícone cinza claro se não tiver
                icon = qta.icon("fa5s.ban", color="#E0E0E0")
                photo_item.setIcon(icon)
                photo_item.setToolTip("Sem foto")

            self.table.setItem(row, 4, photo_item)

    def select_photo(self):
        """Abre seletor de arquivos."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if path:
            self.selected_photo_path = path
            filename = os.path.basename(path)
            # Corta o nome se for muito grande
            display_name = (filename[:25] + "..") if len(filename) > 25 else filename
            self.lbl_photo_status.setText(display_name)
            self.lbl_photo_status.setStyleSheet(
                f"color: {COLORS['success']}; font-weight: bold;"
            )

    def add_visit(self):
        if not self.intern.intern_id:
            return

        venue_id = self.combo_venue.currentData()
        if not venue_id:
            QMessageBox.warning(self, "Atenção", "Selecione o local da visita.")
            return

        iso_date = self.date_edit.date().toString("yyyy-MM-dd")
        venue_name = self.combo_venue.currentText()
        obs = self.txt_obs.text().strip()

        final_photo_name = None
        if self.selected_photo_path:
            try:
                final_photo_name = self.service.save_photo(
                    self.selected_photo_path, self.intern.name, venue_name, iso_date
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar foto: {e}")
                return

        new_visit = Visit(
            intern_id=self.intern.intern_id,
            venue_id=venue_id,
            visit_date=iso_date,
            observation=obs,
            photo_path=final_photo_name,
        )

        try:
            self.service.add_new_visit(new_visit)

            self.txt_obs.clear()
            self.selected_photo_path = None
            self.lbl_photo_status.setText("Nenhuma foto selecionada")
            self.lbl_photo_status.setStyleSheet(
                f"color: {COLORS['secondary']}; font-style: italic;"
            )

            self.load_data()
            QMessageBox.information(self, "Sucesso", "Visita registrada!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar visita: {e}")

    def delete_visit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma visita para excluir.")
            return

        item_id = self.table.item(row, 0)
        if not item_id:
            return

        visit_id = int(item_id.text())

        confirm = QMessageBox.question(
            self,
            "Excluir",
            "Tem certeza que deseja apagar este registro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            dummy = Visit(intern_id=0, venue_id=0, visit_date="", visit_id=visit_id)
            self.service.delete_visit(dummy)
            self.load_data()

    def view_photo(self):
        """Abre a foto no visualizador padrão do sistema."""
        row = self.table.currentRow()
        if row < 0:
            return

        item = self.table.item(row, 4)
        if not item:
            return

        photo_filename = item.data(Qt.ItemDataRole.UserRole)

        if photo_filename:
            full_path = USER_DATA_ROOT / "photos" / photo_filename
            if full_path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(full_path)))
            else:
                QMessageBox.warning(
                    self, "Erro", "Arquivo da foto não encontrado no disco."
                )
