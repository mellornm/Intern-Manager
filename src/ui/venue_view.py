from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QLabel,
    QMenu,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QCursor
import qtawesome as qta

from ui.styles import COLORS
from ui.dialogs.venue_dialog import VenueDialog


class VenueView(QWidget):
    """
    Manages the UI for internship venues.

    This widget displays a list of venues in a table, allowing users
    to add, edit, and delete them through a dialog interface.
    """

    def __init__(self, service, comm_service=None):
        """
        Initializes the VenueView.

        Args:
            service: The venue service instance for database operations.
            comm_service: The communication service instance.
        """
        super().__init__()
        self.service = service
        self.comm_service = comm_service
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        """Initializes and configures the UI components for the view."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # --- Header ---
        header = QHBoxLayout()
        lbl = QLabel("Gerenciar Locais")
        lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {COLORS['dark']};"
        )
        header.addWidget(lbl)
        header.addStretch()

        self.btn_add = QPushButton(" Novo Local")
        self.btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.add_venue)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        # --- Table ---
        self.table = QTableWidget()

        # Set a custom color for the selection highlight
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#BBDEFB"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["dark"]))
        self.table.setPalette(palette)

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Local", "Supervisor", "Telefone"])
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
        self.table.setRowHeight(0, 50)

        # Context Menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)

        self.table.doubleClicked.connect(self.edit_venue)
        layout.addWidget(self.table)

        # --- Action Buttons ---
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.btn_edit = QPushButton(" Editar")
        self.btn_edit.setIcon(qta.icon("fa5s.pen", color=COLORS["dark"]))
        self.btn_edit.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: 1px solid {COLORS["border"]}; padding: 8px 15px; border-radius: 4px; color: {COLORS["dark"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        self.btn_edit.clicked.connect(self.edit_venue)

        self.btn_wa = QPushButton(" WhatsApp")
        self.btn_wa.setIcon(qta.icon("fa5b.whatsapp", color="#25D366"))
        self.btn_wa.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: 1px solid {COLORS["border"]}; padding: 8px 15px; border-radius: 4px; color: {COLORS["dark"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        self.btn_wa.clicked.connect(self.send_whatsapp)

        self.btn_mail = QPushButton(" E-mail")
        self.btn_mail.setIcon(qta.icon("fa5s.envelope", color="#EA4335"))
        self.btn_mail.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: 1px solid {COLORS["border"]}; padding: 8px 15px; border-radius: 4px; color: {COLORS["dark"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        self.btn_mail.clicked.connect(self.send_email)

        self.btn_del = QPushButton(" Excluir")
        self.btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        self.btn_del.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: 1px solid #F5C6CB; padding: 8px 15px; border-radius: 4px; color: {COLORS["danger"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: #F8D7DA; }}
        """)
        self.btn_del.clicked.connect(self.delete_venue)

        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_wa)
        actions_layout.addWidget(self.btn_mail)
        actions_layout.addWidget(self.btn_del)
        layout.addLayout(actions_layout)

    def _open_context_menu(self, pos):
        """Displays a context menu for the selected venue."""
        item = self.table.itemAt(pos)
        if not item:
            return

        self.table.selectRow(item.row())
        v = self.get_selected()
        if not v:
            return

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; border-radius: 6px; padding: 5px; }}
            QMenu::item {{ padding: 8px 25px; border-radius: 4px; color: {COLORS["dark"]}; font-weight: 500; }}
            QMenu::item:selected {{ background-color: {COLORS["light"]}; color: {COLORS["primary"]}; }}
            QMenu::separator {{ height: 1px; background: {COLORS["border"]}; margin: 5px 10px; }}
        """)

        act_edit = menu.addAction(qta.icon("fa5s.pen", color=COLORS["dark"]), "  Editar Local")
        act_edit.triggered.connect(self.edit_venue)

        act_wa = menu.addAction(qta.icon("fa5b.whatsapp", color="#25D366"), "  Enviar WhatsApp")
        act_wa.triggered.connect(self.send_whatsapp)

        act_mail = menu.addAction(qta.icon("fa5s.envelope", color="#EA4335"), "  Enviar E-mail")
        act_mail.triggered.connect(self.send_email)

        menu.addSeparator()

        act_del = menu.addAction(qta.icon("fa5s.trash-alt", color=COLORS["danger"]), "  Excluir Local")
        act_del.triggered.connect(self.delete_venue)

        # Use global mouse position for the context menu
        menu.exec(QCursor.pos())

    def refresh_data(self):
        """Fetches all venues from the service and repopulates the table."""
        self.venues = self.service.get_all()
        self.table.setRowCount(0)
        for row, v in enumerate(self.venues):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)
            self.table.setItem(row, 0, QTableWidgetItem(str(v.venue_id)))

            item_name = QTableWidgetItem(v.venue_name)
            font = item_name.font()
            font.setBold(True)
            item_name.setFont(font)
            self.table.setItem(row, 1, item_name)

            self.table.setItem(row, 2, QTableWidgetItem(v.supervisor_name or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(v.supervisor_phone or "-"))

    def get_selected(self):
        """
        Retrieves the full Venue object for the currently selected table row.

        Returns:
            The Venue object, or None if no row is selected.
        """
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None

        # Ensure the item exists before trying to access its text
        item = self.table.item(rows[0].row(), 0)
        if item is None:
            return None

        vid = int(item.text())
        # Find the corresponding object in our cached list
        return next((v for v in self.venues if v.venue_id == vid), None)

    def add_venue(self):
        """Opens a dialog to add a new venue and saves it if accepted."""
        d = VenueDialog(self)
        if d.exec():
            try:
                self.service.add_new_venue(d.get_data())
                self.refresh_data()
                QMessageBox.information(self, "Sucesso", "Local adicionado!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def edit_venue(self):
        """Opens a dialog to edit the selected venue and saves the changes."""
        v = self.get_selected()
        if not v:
            return

        d = VenueDialog(self, v)
        if d.exec():
            try:
                self.service.update_venue(d.get_data())
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def send_whatsapp(self):
        """Triggers the WhatsApp communication service for the selected venue's supervisor."""
        v = self.get_selected()
        if not v:
            return
        if not v.supervisor_phone:
            QMessageBox.warning(self, "Atenção", f"O local '{v.venue_name}' não possui telefone de supervisor cadastrado.")
            return
        
        self.comm_service.open_whatsapp(v.supervisor_phone, f"Olá {v.supervisor_name or ''}, sou o supervisor de estágio. Gostaria de tratar sobre os estagiários alocados no local '{v.venue_name}'.")

    def send_email(self):
        """Triggers the Email communication service for the selected venue's supervisor."""
        v = self.get_selected()
        if not v:
            return
        if not v.supervisor_email:
            QMessageBox.warning(self, "Atenção", f"O local '{v.venue_name}' não possui e-mail de supervisor cadastrado.")
            return
        
        self.comm_service.open_email(v.supervisor_email, f"Assunto: Acompanhamento de Estágio - {v.venue_name}")

    def delete_venue(self):
        """Deletes the selected venue after a confirmation dialog."""
        v = self.get_selected()
        if not v:
            return

        reply = QMessageBox.question(
            self,
            "Excluir",
            f"Excluir '{v.venue_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_venue(v)
                self.refresh_data()
            except Exception as e:
                error_msg = str(e).lower()
                if "foreign key" in error_msg or "constraint failed" in error_msg:
                    detailed_msg = (
                        f"Não é possível excluir '{v.venue_name}'.\n\n"
                        "Existem estagiários vinculados a este local. "
                        "Remova ou transfira os alunos antes de excluir o local de estágio."
                    )
                else:
                    detailed_msg = f"Ocorreu um erro inesperado: {e}"

                QMessageBox.critical(self, "Impossível Excluir", detailed_msg)
