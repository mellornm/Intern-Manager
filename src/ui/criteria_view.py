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
    QInputDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
import qtawesome as qta

from ui.styles import COLORS
from core.models.evaluation_criteria import EvaluationCriteria


class CriteriaView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        lbl = QLabel("Critérios de Avaliação")
        lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {COLORS['dark']};"
        )
        header.addWidget(lbl)
        header.addStretch()

        self.btn_add = QPushButton(" Novo Critério")
        self.btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.add_criteria)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        # Tabela
        self.table = QTableWidget()

        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#BBDEFB"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["dark"]))
        self.table.setPalette(palette)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Critério", "Peso"])
        self.table.setColumnHidden(0, True)

        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setRowHeight(0, 50)

        self.table.doubleClicked.connect(self.edit_criteria)
        layout.addWidget(self.table)

        # Botões Inferiores
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.btn_edit = QPushButton(" Editar")
        self.btn_edit.setIcon(qta.icon("fa5s.pen", color=COLORS["dark"]))
        self.btn_edit.setStyleSheet(
            f"background: transparent; border: 1px solid {COLORS['border']}; padding: 8px 15px; border-radius: 4px; font-weight: 600;"
        )
        self.btn_edit.clicked.connect(self.edit_criteria)

        self.btn_del = QPushButton(" Excluir")
        self.btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        self.btn_del.setStyleSheet(
            f"background: transparent; border: 1px solid #F5C6CB; padding: 8px 15px; border-radius: 4px; color: {COLORS['danger']}; font-weight: 600;"
        )
        self.btn_del.clicked.connect(self.delete_criteria)

        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_del)
        layout.addLayout(actions_layout)

    def refresh_data(self):
        self.criteria_list = self.service.list_active_criteria()
        self.table.setRowCount(0)
        for row, c in enumerate(self.criteria_list):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)
            self.table.setItem(row, 0, QTableWidgetItem(str(c.criteria_id)))

            name_item = QTableWidgetItem(c.name)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row, 1, name_item)

            self.table.setItem(row, 2, QTableWidgetItem(f"{c.weight:.1f}"))

    def get_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None

        # Trava de segurança
        item = self.table.item(rows[0].row(), 0)
        if item is None:
            return None

        cid = int(item.text())
        return next((c for c in self.criteria_list if c.criteria_id == cid), None)

    def add_criteria(self):
        name, ok = QInputDialog.getText(self, "Novo Critério", "Nome do Critério:")
        if ok and name:
            weight, ok2 = QInputDialog.getDouble(
                self, "Peso", "Peso (0-10):", 1.0, 0, 10, 1
            )
            if ok2:
                new_c = EvaluationCriteria(name=name, weight=weight)
                self.service.add_criteria(new_c)
                self.refresh_data()

    def edit_criteria(self):
        c = self.get_selected()
        if not c:
            return
        name, ok = QInputDialog.getText(self, "Editar", "Nome:", text=c.name)
        if ok and name:
            weight, ok2 = QInputDialog.getDouble(
                self, "Peso", "Peso:", c.weight, 0, 10, 1
            )
            if ok2:
                c.name = name
                c.weight = weight
                self.service.update_criteria(c)
                self.refresh_data()

    def delete_criteria(self):
        c = self.get_selected()
        if not c:
            return
        if (
            QMessageBox.question(
                self,
                "Excluir",
                f"Excluir '{c.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            self.service.delete_criteria(c.criteria_id)
            self.refresh_data()
