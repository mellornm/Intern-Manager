from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
    QLabel,
    QComboBox,
    QTextEdit,
    QFrame,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette
import qtawesome as qta

from core.models.intern import Intern
from core.models.document import Document
from services.document_service import DocumentService
from ui.styles import COLORS
from ui.delegates import StatusDelegate

# --- Dicionário de Broncas Padrão ---
STANDARD_FEEDBACKS = {
    "--- Selecione um motivo ---": "",
    "Assinatura Faltando": "Documento recusado. Motivo: Falta a assinatura do supervisor de campo ou do estagiário.",
    "Data Inválida": "Documento recusado. Motivo: As datas informadas não correspondem ao período do estágio cadastrado.",
    "Carimbo Ausente": "Documento recusado. Motivo: É obrigatório o carimbo e assinatura da instituição concedente.",
    "Documento Errado": "Documento recusado. Motivo: O arquivo enviado não corresponde ao modelo oficial da universidade.",
    "Rasuras": "Documento recusado. Motivo: O documento apresenta rasuras ou está ilegível.",
}


class AuditDialog(QDialog):
    """Janela Popup para Auditar (Aprovar/Reprovar) um documento."""

    def __init__(self, parent, document: Document):
        super().__init__(parent)
        self.document = document
        self.setWindowTitle("Auditoria de Documento")
        self.resize(500, 450)

        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["white"]}; }}
            QLabel {{ color: {COLORS["dark"]}; font-weight: bold; margin-top: 10px; }}
            QComboBox, QTextEdit {{
                background-color: {COLORS["light"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS["dark"]};
            }}
            QComboBox:focus, QTextEdit:focus {{ border: 1px solid {COLORS["primary"]}; background-color: {COLORS["white"]}; }}
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            qta.icon("fa5s.stamp", color=COLORS["primary"]).pixmap(QSize(32, 32))
        )

        title_box = QVBoxLayout()
        lbl_doc = QLabel(self.document.document_name)
        lbl_doc.setStyleSheet(
            f"font-size: 18px; color: {COLORS['primary']}; margin: 0;"
        )
        lbl_sub = QLabel("Avaliação de conformidade")
        lbl_sub.setStyleSheet(
            f"font-size: 12px; color: {COLORS['secondary']}; font-weight: normal; margin: 0;"
        )

        title_box.addWidget(lbl_doc)
        title_box.addWidget(lbl_sub)
        header.addWidget(icon)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']}")
        layout.addWidget(line)

        # Status Combo
        layout.addWidget(QLabel("Decisão:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Pendente", "Aprovado", "Reprovado"])
        self.combo_status.setCurrentText(self.document.status or "Pendente")
        self.combo_status.currentIndexChanged.connect(self.on_status_change)
        layout.addWidget(self.combo_status)

        # Motivos Prontos (Só aparece se Reprovado)
        self.lbl_reasons = QLabel("Motivo da Recusa (Rápido):")
        layout.addWidget(self.lbl_reasons)

        self.combo_reasons = QComboBox()
        self.combo_reasons.addItems(list(STANDARD_FEEDBACKS.keys()))
        self.combo_reasons.currentTextChanged.connect(self.fill_feedback)
        layout.addWidget(self.combo_reasons)

        # Feedback Texto
        layout.addWidget(QLabel("Parecer / Feedback:"))
        self.txt_feedback = QTextEdit()
        self.txt_feedback.setPlaceholderText("Descreva o problema ou observações...")
        self.txt_feedback.setText(self.document.feedback or "")
        layout.addWidget(self.txt_feedback)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none; font-weight: bold;"
        )
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Confirmar Decisão")
        self.btn_save.setIcon(qta.icon("fa5s.check-double", color="white"))
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border-radius: 6px; padding: 10px 20px; font-weight: bold; border: none; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_save.clicked.connect(self.accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        # Estado inicial
        self.on_status_change()

    def on_status_change(self):
        status = self.combo_status.currentText()
        is_rejected = status == "Reprovado"

        self.lbl_reasons.setVisible(is_rejected)
        self.combo_reasons.setVisible(is_rejected)

        if status == "Aprovado":
            self.btn_save.setStyleSheet(
                f"background-color: {COLORS['success']}; color: white; border-radius: 6px; padding: 10px 20px; font-weight: bold; border: none;"
            )
        elif status == "Reprovado":
            self.btn_save.setStyleSheet(
                f"background-color: {COLORS['danger']}; color: white; border-radius: 6px; padding: 10px 20px; font-weight: bold; border: none;"
            )
        else:
            self.btn_save.setStyleSheet(
                f"background-color: {COLORS['primary']}; color: white; border-radius: 6px; padding: 10px 20px; font-weight: bold; border: none;"
            )

    def fill_feedback(self, reason_key):
        text = STANDARD_FEEDBACKS.get(reason_key, "")
        if text:
            self.txt_feedback.setText(text)

    def get_data(self):
        return {
            "status": self.combo_status.currentText(),
            "feedback": self.txt_feedback.toPlainText(),
        }


class DocumentDialog(QDialog):
    """Gerenciador de Documentos do Aluno."""

    def __init__(self, parent, intern: Intern, service: DocumentService):
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Documentos: {intern.name}")
        self.resize(800, 500)

        # Define apenas a cor de fundo do Dialog
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['light']}; }}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            qta.icon("fa5s.folder-open", color=COLORS["dark"]).pixmap(QSize(28, 28))
        )
        lbl = QLabel(f"Documentos de {self.intern.name}")
        lbl.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['dark']};"
        )
        header.addWidget(icon)
        header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()

        btn_add = QPushButton("Adicionar Avulso")
        btn_add.setIcon(qta.icon("fa5s.plus", color=COLORS["dark"]))
        btn_add.clicked.connect(self.add_document)

        btn_gen = QPushButton("Gerar Kit Padrão")
        btn_gen.setIcon(qta.icon("fa5s.magic", color="white"))
        btn_gen.setStyleSheet(
            f"background-color: {COLORS['primary']}; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold;"
        )
        btn_gen.clicked.connect(self.generate_defaults)

        btn_audit = QPushButton("Auditar / Parecer")
        btn_audit.setIcon(qta.icon("fa5s.stamp", color=COLORS["dark"]))
        btn_audit.clicked.connect(self.audit_document)

        btn_del = QPushButton("Excluir")
        btn_del.setIcon(qta.icon("fa5s.trash", color=COLORS["danger"]))
        btn_del.setStyleSheet(f"color: {COLORS['danger']};")
        btn_del.clicked.connect(self.delete_document)

        for b in [btn_add, btn_audit, btn_del]:
            if not b.styleSheet():
                b.setStyleSheet(
                    f"background-color: {COLORS['white']}; border: 1px solid {COLORS['border']}; padding: 8px 15px; border-radius: 4px; font-weight: 600; color: {COLORS['dark']};"
                )

        toolbar.addWidget(btn_gen)
        toolbar.addWidget(btn_add)
        toolbar.addStretch()
        toolbar.addWidget(btn_audit)
        toolbar.addWidget(btn_del)
        layout.addLayout(toolbar)

        # --- TABELA ---
        self.table = QTableWidget()

        # --- AJUSTE DE CONTRASTE ---
        # 1. Definimos um Azul mais forte (#BBDEFB) na Paleta para destacar bem,
        #    mesmo se a linha de trás for cinza.
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#BBDEFB"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["dark"]))
        self.table.setPalette(palette)

        # 2. CSS Ajustado:
        #    - Define explicitamente a cor alternada (zebra) como #FAFAFA (quase branco)
        #    - Define o Hover como #E0E0E0 (cinza médio) para ser visível sobre a zebra
        self.table.setStyleSheet(f"""
            QTableWidget {{ 
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]}; 
                background-color: {COLORS["white"]};
                alternate-background-color: #FAFAFA; /* Zebra bem clarinha */
                gridline-color: transparent;
                outline: none;
            }}
            QHeaderView::section {{ 
                background-color: {COLORS["white"]}; 
                color: {COLORS["medium"]}; 
                border: none; 
                border-bottom: 2px solid {COLORS["light"]}; 
                font-weight: bold; 
                padding: 8px; 
            }}
            /* O Hover tem que ser mais escuro que a linha alternada */
            QTableWidget::item:hover {{
                background-color: #E0E0E0; 
                color: {COLORS["dark"]};
            }}
            /* Reforço da seleção para garantir */
            QTableWidget::item:selected {{
                background-color: #BBDEFB;
                color: {COLORS["dark"]};
                border: none;
            }}
        """)

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Documento", "Status", "Parecer"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)

        # Pílulas na coluna Status (índice 2)
        self.table.setItemDelegateForColumn(2, StatusDelegate(self.table))
        self.table.doubleClicked.connect(self.audit_document)

        layout.addWidget(self.table)

        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none;"
        )
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def load_data(self):
        if not self.intern.intern_id:
            return

        docs = self.service.get_by_intern_id(self.intern.intern_id)

        self.table.setRowCount(0)
        for row, d in enumerate(docs):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 45)

            self.table.setItem(row, 0, QTableWidgetItem(str(d.document_id)))

            item_name = QTableWidgetItem(d.document_name)
            item_name.setFont(self.font())
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, item_name)

            self.table.setItem(row, 2, QTableWidgetItem(d.status))
            self.table.setItem(row, 3, QTableWidgetItem(d.feedback or ""))

    def audit_document(self):
        row = self.table.currentRow()
        if row < 0:
            return

        item_id = self.table.item(row, 0)
        if not item_id:
            return
        doc_id = int(item_id.text())

        doc = self.service.get_document_by_id(doc_id)
        if doc:
            audit = AuditDialog(self, doc)
            if audit.exec():
                data = audit.get_data()
                doc.status = data["status"]
                doc.feedback = data["feedback"]
                self.service.update_document(doc)
                self.load_data()

    def add_document(self):
        if self.intern.intern_id is None:
            QMessageBox.warning(
                self, "Erro", "Salve o aluno antes de adicionar documentos."
            )
            return
        name, ok = QInputDialog.getText(self, "Novo", "Nome do documento:")
        if ok and name:
            new_doc = Document(
                intern_id=self.intern.intern_id, document_name=name, status="Pendente"
            )
            self.service.add_new_document(new_doc)
            self.load_data()

    def generate_defaults(self):
        if self.intern.intern_id:
            self.service.create_initial_documents_batch(self.intern.intern_id)
            self.load_data()

    def delete_document(self):
        row = self.table.currentRow()
        if row < 0:
            return

        item_id = self.table.item(row, 0)
        if not item_id:
            return
        doc_id = int(item_id.text())

        if (
            QMessageBox.question(
                self,
                "Excluir",
                "Apagar documento?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            doc = self.service.get_document_by_id(doc_id)
            if doc:
                self.service.delete_document(doc)
                self.load_data()
