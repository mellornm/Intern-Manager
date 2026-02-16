from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QLabel,
)
from PySide6.QtCore import Qt, QSettings, QSize
import qtawesome as qta
from ui.styles import COLORS


class SettingsDialog(QDialog):
    """
    Dialog for managing application settings, including report personalization and data export.

    This dialog allows users to configure details like institution name, supervisor,
    city/state, and a logo path for reports. It also provides functionality to
    export the application's database to an Excel file.

    Attributes:
        export_service (ExportService, optional): An service for exporting data.
            If None, the export functionality will be disabled.
        settings (QSettings): QSettings object for persistent storage of user settings.
    """

    def __init__(
        self, parent=None, export_service=None, visit_service=None, intern_service=None
    ):
        super().__init__(parent)
        self.export_service = export_service
        self.visit_service = visit_service
        self.intern_service = intern_service

        self.setWindowTitle("Configurações do Sistema")
        self.resize(550, 500)

        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            QGroupBox {{ 
                font-weight: bold; 
                border: 1px solid {COLORS["border"]}; 
                border-radius: 6px; 
                margin-top: 10px; 
                padding-top: 15px;
                color: {COLORS["dark"]};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QLineEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 8px;
                color: {COLORS["dark"]};
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS["primary"]}; }}
        """)

        self.settings = QSettings("Rodrigo Noronha de Mello", "InternManager2026")

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            qta.icon("fa5s.cog", color=COLORS["medium"]).pixmap(QSize(32, 32))
        )
        lbl_title = QLabel("Parâmetros Gerais")
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['dark']};"
        )
        header.addWidget(icon)
        header.addWidget(lbl_title)
        header.addStretch()
        layout.addLayout(header)

        group_rep = QGroupBox("Personalização dos Relatórios (PDF)")
        form = QFormLayout()
        form.setSpacing(15)

        self.txt_institution = QLineEdit()
        self.txt_institution.setPlaceholderText(
            "Ex: UNISINOS - Curso de Biomedicina..."
        )
        self.txt_supervisor = QLineEdit()
        self.txt_supervisor.setPlaceholderText("Ex: Prof. Dr. João da Silva")
        self.txt_city = QLineEdit()
        self.txt_city.setPlaceholderText("Ex: São Leopoldo - RS")

        self.txt_logo_path = QLineEdit()
        self.txt_logo_path.setReadOnly(True)
        self.txt_logo_path.setPlaceholderText("Caminho da imagem do logo...")

        btn_logo = QPushButton(" Buscar")
        btn_logo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logo.clicked.connect(self.select_logo)

        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.txt_logo_path)
        logo_layout.addWidget(btn_logo)

        def lbl(t):
            lbl_style = QLabel(t)
            lbl_style.setStyleSheet("font-weight: bold;")
            return lbl_style

        form.addRow(lbl("Instituição:"), self.txt_institution)
        form.addRow(lbl("Supervisor:"), self.txt_supervisor)
        form.addRow(lbl("Cidade/UF:"), self.txt_city)
        form.addRow(lbl("Logotipo:"), logo_layout)

        group_rep.setLayout(form)
        layout.addWidget(group_rep)

        group_data = QGroupBox("Dados e Backup")
        data_layout = QVBoxLayout()

        lbl_bkp = QLabel(
            "Exporte todos os dados do sistema para uma planilha Excel (.xlsx)."
        )
        lbl_bkp.setStyleSheet(f"color: {COLORS['secondary']}; font-weight: normal;")
        data_layout.addWidget(lbl_bkp)

        self.btn_export = QPushButton(" Exportar Banco de Dados (Excel)")
        self.btn_export.setIcon(qta.icon("fa5s.file-excel", color="white"))
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["success"]}; color: white; border: none; 
                padding: 10px; border-radius: 6px; font-weight: bold; text-align: left; padding-left: 15px;
            }}
            QPushButton:hover {{ background-color: #0E6A0E; }}
        """)
        self.btn_export.clicked.connect(self.export_data)

        if not self.export_service:
            self.btn_export.setEnabled(False)
            self.btn_export.setText("Exportar (Serviço indisponível)")

        data_layout.addWidget(self.btn_export)
        self.btn_export_photos = QPushButton(" Backup de TODAS as Fotos")
        self.btn_export_photos.setIcon(qta.icon("fa5s.images", color="white"))
        self.btn_export_photos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_photos.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 10px; border-radius: 6px; font-weight: bold; text-align: left; padding-left: 15px;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_export_photos.clicked.connect(self.backup_all_photos)

        data_layout.addWidget(self.btn_export_photos)
        group_data.setLayout(data_layout)
        layout.addWidget(group_data)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none;"
        )
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Salvar Configurações")
        self.btn_save.setIcon(qta.icon("fa5s.save", color="white"))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 10px 20px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_save.clicked.connect(self.save_settings)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def select_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Logomarca", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if path:
            self.txt_logo_path.setText(path)

    def _load_data(self):
        self.txt_institution.setText(
            str(self.settings.value("institution_name", "") or "")
        )
        self.txt_supervisor.setText(
            str(self.settings.value("coordinator_name", "") or "")
        )
        self.txt_city.setText(str(self.settings.value("city_state", "") or ""))
        self.txt_logo_path.setText(str(self.settings.value("logo_path", "") or ""))

    def save_settings(self):
        self.settings.setValue("institution_name", self.txt_institution.text().strip())
        self.settings.setValue("coordinator_name", self.txt_supervisor.text().strip())
        self.settings.setValue("city_state", self.txt_city.text().strip())
        self.settings.setValue("logo_path", self.txt_logo_path.text().strip())

        QMessageBox.information(self, "Salvo", "Configurações atualizadas com sucesso!")
        self.accept()

    def export_data(self):
        if not self.export_service:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar para Excel", "backup_estagio.xlsx", "Excel Files (*.xlsx)"
        )
        if path:
            try:
                self.export_service.export_to_excel(path)
                QMessageBox.information(
                    self, "Sucesso", f"Dados exportados para:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha na exportação:\n{e}")

    def backup_all_photos(self):
        if not self.visit_service or not self.intern_service:
            QMessageBox.critical(self, "Erro", "Serviços não disponíveis.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Pasta para Backup das Fotos")
        if not folder:
            return

        all_interns = self.intern_service.get_all_interns()

        targets = [(i.intern_id, i.name) for i in all_interns if i.intern_id]

        if not targets:
            QMessageBox.information(self, "Aviso", "Nenhum aluno encontrado.")
            return

        try:
            success, errors = self.visit_service.export_batch_photos(targets, folder)
            QMessageBox.information(
                self,
                "Backup Concluído",
                f"Fotos exportadas: {success}\nErros/Ignorados: {errors}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
