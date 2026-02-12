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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
import qtawesome as qta

from ui.styles import COLORS
from ui.dialogs.venue_dialog import VenueDialog


class VenueView(QWidget):
    """
    Manages the UI for internship venues.

    This widget displays a list of venues in a table, allowing users
    to add, edit, and delete them through a dialog interface.
    """

    def __init__(self, service):
        """
        Initializes the VenueView.

        Args:
            service: The venue service instance for database operations.
        """
        super().__init__()
        self.service = service
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

        self.btn_del = QPushButton(" Excluir")
        self.btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        self.btn_del.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: 1px solid #F5C6CB; padding: 8px 15px; border-radius: 4px; color: {COLORS["danger"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: #F8D7DA; }}
        """)
        self.btn_del.clicked.connect(self.delete_venue)

        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_del)
        layout.addLayout(actions_layout)

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
                QMessageBox.critical(
                    self,
                    "Erro",
                    str(e) + "\nVerifique se existem alunos vinculados ao local",
                )
