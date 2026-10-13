"""
Settings and System Administration Page for NiceGUI.
Configures report templates, institution parameters, logo upload, and system database backups.
"""

from pathlib import Path
from nicegui import ui

from config import DB_PATH, TEMP_DIR, UPLOADS_DIR
from ui.context import ServiceContainer
from ui.layout import page_layout
from ui.settings_store import load_settings, save_settings


def render_settings_page(container: ServiceContainer):
    """Renders the settings and system administration page."""
    with page_layout(title="Configurações", active_path="/settings"):
        current_settings = load_settings()

        # Header
        with ui.row().classes("w-full justify-between items-center"):
            with ui.column().classes("gap-0"):
                ui.label("Configurações do Sistema").classes("text-2xl sm:text-3xl font-extrabold text-slate-900")
                ui.label("Personalização de relatórios em PDF e exportação de backups.").classes("text-sm text-slate-500")

        with ui.grid(columns=1).classes("w-full lg:grid-cols-2 gap-6"):
            # 1. Report Customization Card
            with ui.card().classes("p-6 card-shadow flex flex-col gap-4"):
                with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-200"):
                    ui.icon("tune", color="primary", size="md")
                    ui.label("Parâmetros dos Relatórios (PDF)").classes("text-lg font-bold text-slate-800")

                inst_input = ui.input(
                    "Nome da Instituição de Ensino",
                    value=current_settings.get("institution_name", ""),
                    placeholder="Ex: UNISINOS - Curso de Biomedicina",
                ).classes("w-full").props("outlined dense")

                coord_input = ui.input(
                    "Coordenador / Supervisor do Estágio",
                    value=current_settings.get("coordinator_name", ""),
                    placeholder="Ex: Prof. Dr. Rodrigo Noronha de Mello",
                ).classes("w-full").props("outlined dense")

                city_input = ui.input(
                    "Cidade - UF",
                    value=current_settings.get("city_state", ""),
                    placeholder="Ex: Porto Alegre - RS",
                ).classes("w-full").props("outlined dense")

                # Logo upload
                ui.label("Logotipo da Instituição").classes("text-xs font-bold text-slate-500 uppercase mt-2")

                logo_preview_container = ui.row().classes("items-center gap-3")

                def update_logo_preview():
                    logo_preview_container.clear()
                    current_lp = load_settings().get("logo_path", "")
                    if current_lp and Path(current_lp).exists():
                        with logo_preview_container:
                            ui.image(Path(current_lp)).classes("h-16 w-32 object-contain rounded border border-slate-200 p-1")
                            ui.label("Logotipo ativo").classes("text-xs text-green-700 font-semibold")

                update_logo_preview()

                async def handle_logo_upload(e):
                    content = e.content.read()
                    destination = UPLOADS_DIR / "institution_logo.png"
                    with open(destination, "wb") as f:
                        f.write(content)

                    save_settings({"logo_path": str(destination)})
                    ui.notify("Logotipo atualizado com sucesso!", color="positive")
                    update_logo_preview()

                ui.upload(
                    label="Substituir Imagem do Logotipo",
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_logo_upload,
                ).props('accept="image/*" flat size=sm color=primary').classes("w-full")

                def handle_save_settings():
                    data = {
                        "institution_name": (inst_input.value or "").strip(),
                        "coordinator_name": (coord_input.value or "").strip(),
                        "city_state": (city_input.value or "").strip(),
                    }
                    save_settings(data)
                    ui.notify("Configurações salvas com sucesso!", color="positive")

                with ui.row().classes("w-full justify-end pt-3 border-t border-slate-200"):
                    ui.button("Salvar Parâmetros", icon="save", on_click=handle_save_settings).props("color=primary")

            # 2. Backups & Data Export Card
            with ui.card().classes("p-6 card-shadow flex flex-col gap-4"):
                with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-200"):
                    ui.icon("storage", color="primary", size="md")
                    ui.label("Backup e Exportação de Dados").classes("text-lg font-bold text-slate-800")

                ui.label("Exporte os dados completos do sistema em formato Excel ou gere uma cópia de segurança do banco de dados SQLite para arquivamento.").classes("text-sm text-slate-600")

                with ui.column().classes("w-full gap-3 pt-2"):
                    # Excel Export
                    def handle_excel_backup():
                        temp_xlsx = TEMP_DIR / "backup_completo_intern_manager.xlsx"
                        try:
                            container.export_service.export_to_excel(str(temp_xlsx))
                            ui.notify("Planilha completa gerada! Iniciando download...", color="positive")
                            ui.download(str(temp_xlsx), filename="backup_intern_manager.xlsx")
                        except Exception as e:
                            ui.notify(f"Erro ao exportar banco: {e}", color="negative")

                    with ui.card().classes("w-full p-4 border border-slate-200 flex-row justify-between items-center"):
                        with ui.column().classes("gap-0"):
                            ui.label("Planilha Consolidada (Excel)").classes("font-bold text-sm text-slate-800")
                            ui.label("Exporta todas as tabelas (alunos, notas, documentos, locais) em abas separadas.").classes("text-xs text-slate-500")
                        ui.button("Exportar (.xlsx)", icon="download", on_click=handle_excel_backup).props("outline color=green-8")

                    # SQLite Database copy
                    def handle_sqlite_download():
                        if DB_PATH.exists():
                            ui.notify("Baixando arquivo do banco de dados...", color="positive")
                            ui.download(str(DB_PATH), filename=DB_PATH.name)
                        else:
                            ui.notify("Arquivo do banco de dados não encontrado.", color="warning")

                    with ui.card().classes("w-full p-4 border border-slate-200 flex-row justify-between items-center"):
                        with ui.column().classes("gap-0"):
                            ui.label("Cópia do Banco de Dados (.db)").classes("font-bold text-sm text-slate-800")
                            ui.label("Arquivo SQLite raw para backup e restauração direta.").classes("text-xs text-slate-500")
                        ui.button("Baixar Banco (.db)", icon="cloud_download", on_click=handle_sqlite_download).props("outline color=blue-8")

                # System Info
                with ui.column().classes("w-full pt-4 border-t border-slate-200 text-xs text-slate-400 gap-1"):
                    ui.label(f"Local do Banco: {DB_PATH}")
                    ui.label("Modo de Concorrência: SQLite WAL (Write-Ahead Logging)")
                    ui.label("Framework: NiceGUI (Web Concorrente)")
