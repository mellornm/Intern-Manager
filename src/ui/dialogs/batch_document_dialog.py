from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from ui.styles import COLORS
from core.constants import DEFAULT_DOCUMENTS_LIST

class BatchDocumentDialog(QDialog):
    """
    Dialog to select a document type to approve for multiple interns.
    """
    def __init__(self, parent, count):
        super().__init__(parent)
        self.count = count
        self.setWindowTitle("Aprovação Coletiva")
        self.setFixedWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        lbl_info = QLabel(f"Você está aprovando documentos para <b>{self.count} alunos</b>.")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        layout.addWidget(QLabel("Selecione o documento para aprovar:"))
        
        self.combo_docs = QComboBox()
        self.combo_docs.addItems(DEFAULT_DOCUMENTS_LIST)
        self.combo_docs.setStyleSheet(f"""
            QComboBox {{ border: 1px solid {COLORS["border"]}; padding: 8px; border-radius: 4px; }}
        """)
        layout.addWidget(self.combo_docs)

        # Buttons
        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_ok = QPushButton("Aprovar Todos")
        btn_ok.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; padding: 10px; border-radius: 4px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        btn_ok.clicked.connect(self.accept)

        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def get_selected_document(self):
        return self.combo_docs.currentText()
