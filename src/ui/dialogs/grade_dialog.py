from typing import Dict
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QDoubleSpinBox,
    QMessageBox,
    QWidget,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, QSize, QTimer
import qtawesome as qta

from core.models.intern import Intern
from core.models.grade import Grade
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService
from ui.styles import COLORS


class SmartGradeInput(QDoubleSpinBox):
    """Input inteligente e bonito para notas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {COLORS["light"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
                color: {COLORS["primary"]};
                font-weight: bold;
            }}
            QDoubleSpinBox:focus {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["primary"]};
            }}
        """)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class GradeDialog(QDialog):
    def __init__(
        self,
        parent,
        intern: Intern,
        criteria_service: EvaluationCriteriaService,
        grade_service: GradeService,
    ):
        super().__init__(parent)
        self.intern = intern
        self.criteria_service = criteria_service
        self.grade_service = grade_service
        self.inputs: Dict[int, SmartGradeInput] = {}

        self.setWindowTitle(f"Notas: {intern.name}")
        self.resize(500, 600)
        self.setStyleSheet(f"background-color: {COLORS['white']};")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            qta.icon("fa5s.star", color=COLORS["warning"]).pixmap(QSize(32, 32))
        )

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_name = QLabel(self.intern.name)
        lbl_name.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {COLORS['dark']};"
        )
        lbl_term = QLabel(f"Lançamento de Avaliações - {self.intern.term}")
        lbl_term.setStyleSheet(f"font-size: 12px; color: {COLORS['secondary']};")

        title_box.addWidget(lbl_name)
        title_box.addWidget(lbl_term)
        header.addWidget(icon)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']}")
        layout.addWidget(line)

        # Scroll Area para os critérios
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setSpacing(15)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.form_widget)
        layout.addWidget(scroll)

        # Card de Total
        self.total_frame = QFrame()
        self.total_frame.setStyleSheet(
            f"background-color: {COLORS['light']}; border-radius: 8px; border: 1px solid {COLORS['border']};"
        )
        tf_layout = QHBoxLayout(self.total_frame)

        lbl_t = QLabel("MÉDIA FINAL:")
        lbl_t.setStyleSheet(
            f"font-weight: bold; color: {COLORS['medium']}; font-size: 14px;"
        )

        self.lbl_total = QLabel("0.00")
        self.lbl_total.setStyleSheet(
            f"font-weight: 900; color: {COLORS['dark']}; font-size: 28px;"
        )

        tf_layout.addWidget(lbl_t)
        tf_layout.addStretch()
        tf_layout.addWidget(self.lbl_total)

        layout.addWidget(self.total_frame)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none; font-weight: 600;"
        )
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton(" Salvar Notas")
        btn_save.setIcon(qta.icon("fa5s.save", color="white"))
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 25px; border-radius: 6px; font-weight: bold; font-size: 14px; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        btn_save.clicked.connect(self.save_grades)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def load_data(self):
        if not self.intern.intern_id:
            return

        criteria_list = self.criteria_service.list_active_criteria()
        existing_grades = self.grade_service.get_by_intern_id(self.intern.intern_id)
        grade_map = {g.criteria_id: g.value for g in existing_grades}

        # Limpar layout anterior se houver
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

        self.inputs.clear()

        for c in criteria_list:
            spin = SmartGradeInput()
            spin.setRange(0.0, c.weight)  # Limita ao peso máximo do critério
            spin.setSingleStep(0.1)

            # Valor existente ou 0
            val = grade_map.get(c.criteria_id, 0.0)
            spin.setValue(val)
            spin.valueChanged.connect(self.update_total)

            self.inputs[c.criteria_id] = spin

            # Label bonito com Peso
            lbl_text = f"{c.name} <span style='color:{COLORS['secondary']}; font-size:11px;'>(Máx: {c.weight})</span>"
            lbl = QLabel(lbl_text)
            lbl.setTextFormat(Qt.TextFormat.RichText)

            self.form_layout.addRow(lbl, spin)

        self.update_total()

    def update_total(self):
        total = sum(spin.value() for spin in self.inputs.values())
        self.lbl_total.setText(f"{total:.2f}")

        # Color Coding
        if total >= 6.0:
            self.lbl_total.setStyleSheet(
                f"font-weight: 900; color: {COLORS['success']}; font-size: 28px;"
            )
            self.total_frame.setStyleSheet(
                f"background-color: #D1E7DD; border: 1px solid {COLORS['success']}; border-radius: 8px;"
            )
        else:
            self.lbl_total.setStyleSheet(
                f"font-weight: 900; color: {COLORS['danger']}; font-size: 28px;"
            )
            self.total_frame.setStyleSheet(
                f"background-color: #F8D7DA; border: 1px solid {COLORS['danger']}; border-radius: 8px;"
            )

    def save_grades(self):
        # CORREÇÃO 2: Guard clause para garantir ID
        if not self.intern.intern_id:
            QMessageBox.critical(self, "Erro", "Aluno sem ID!")
            return

        grades_to_save = []
        for c_id, spin in self.inputs.items():
            grades_to_save.append(
                Grade(
                    intern_id=self.intern.intern_id,
                    criteria_id=c_id,
                    value=spin.value(),
                )
            )

        try:
            self.grade_service.save_batch_grades(grades_to_save)
            QMessageBox.information(self, "Sucesso", "Notas salvas com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")
