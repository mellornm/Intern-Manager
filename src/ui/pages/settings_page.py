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
            with ui.column().classes("gap-0.5"):
                ui.label("Configurações do Sistema").classes(
                    "text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Personalização do cabeçalho de relatórios oficiais em PDF e cópias de segurança."
                ).classes("text-xs sm:text-sm text-slate-500")

        with ui.grid(columns=1).classes("w-full lg:grid-cols-2 gap-4 sm:gap-6"):
            # 1. Report Customization Card
            with ui.card().classes(
                "p-5 sm:p-6 bg-white border border-slate-200/80 rounded-xl shadow-xs flex flex-col gap-4"
            ):
                with ui.row().classes("items-center gap-3 pb-3 border-b border-slate-100"):
                    ui.avatar("tune", color="blue-1", text_color="primary", size="md").classes(
                        "rounded-xl"
                    )
                    with ui.column().classes("gap-0"):
                        ui.label("Parâmetros dos Relatórios (PDF)").classes(
                            "text-base font-bold text-slate-900"
                        )
                        ui.label("Dados impressos no cabeçalho e rodapé de assinatura").classes(
                            "text-xs text-slate-400"
                        )

                inst_input = (
                    ui.input(
                        "Nome da Instituição de Ensino",
                        value=current_settings.get("institution_name", ""),
                        placeholder="Ex: UNISINOS - Curso de Biomedicina",
                    )
                    .classes("w-full")
                    .props("outlined dense hide-bottom-space")
                )
                with inst_input.add_slot("prepend"):
                    ui.icon("account_balance", size="xs").classes("text-slate-400")

                coord_input = (
                    ui.input(
                        "Coordenador / Supervisor Acadêmico",
                        value=current_settings.get("coordinator_name", ""),
                        placeholder="Ex: Prof. Dr. Rodrigo Noronha de Mello",
                    )
                    .classes("w-full")
                    .props("outlined dense hide-bottom-space")
                )
                with coord_input.add_slot("prepend"):
                    ui.icon("school", size="xs").classes("text-slate-400")

                city_input = (
                    ui.input(
                        "Cidade - UF (Local de Emissão)",
                        value=current_settings.get("city_state", ""),
                        placeholder="Ex: Porto Alegre - RS",
                    )
                    .classes("w-full")
                    .props("outlined dense hide-bottom-space")
                )
                with city_input.add_slot("prepend"):
                    ui.icon("place", size="xs").classes("text-slate-400")

                ui.label("Logotipo da Instituição").classes(
                    "text-xs font-bold text-slate-500 uppercase tracking-wider mt-1"
                )

                logo_preview_container = ui.row().classes("items-center gap-3")

                def update_logo_preview():
                    logo_preview_container.clear()
                    current_lp = load_settings().get("logo_path", "")
                    if current_lp and Path(current_lp).exists():
                        with logo_preview_container:
                            ui.image(Path(current_lp)).classes(
                                "h-14 w-28 object-contain rounded-lg border border-slate-200 p-1 bg-slate-50"
                            )
                            ui.badge(
                                "Logotipo Ativo", color="green-1", text_color="green-9"
                            ).classes("text-xs font-bold px-2 py-0.5 rounded")

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
                    label="Substituir Imagem do Logotipo (PNG/JPG)",
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_logo_upload,
                ).props('accept="image/*" flat bordered color=primary').classes("w-full")

                def handle_save_settings():
                    data = {
                        "institution_name": (inst_input.value or "").strip(),
                        "coordinator_name": (coord_input.value or "").strip(),
                        "city_state": (city_input.value or "").strip(),
                    }
                    save_settings(data)
                    ui.notify("Configurações salvas com sucesso!", color="positive")

                with ui.row().classes("w-full justify-end pt-3 border-t border-slate-100"):
                    ui.button(
                        "Salvar Parâmetros",
                        icon="save",
                        on_click=handle_save_settings,
                    ).props("unelevated no-caps color=primary").classes("px-4 font-semibold")

            # 2. Backups & Data Export Card
            with ui.card().classes(
                "p-5 sm:p-6 bg-white border border-slate-200/80 rounded-xl shadow-xs flex flex-col justify-between gap-4"
            ):
                with ui.column().classes("w-full gap-4"):
                    with ui.row().classes("items-center gap-3 pb-3 border-b border-slate-100"):
                        ui.avatar(
                            "storage", color="blue-1", text_color="primary", size="md"
                        ).classes("rounded-xl")
                        with ui.column().classes("gap-0"):
                            ui.label("Backup e Exportação de Dados").classes(
                                "text-base font-bold text-slate-900"
                            )
                            ui.label(
                                "Cópia integral das tabelas em Excel ou banco SQLite nativo"
                            ).classes("text-xs text-slate-400")

                    ui.label(
                        "Exporte os dados completos do sistema em formato Excel (.xlsx) ou baixe uma cópia de segurança do banco de dados SQLite (.db) para arquivamento externo."
                    ).classes("text-xs sm:text-sm text-slate-600")

                    def handle_excel_backup():
                        temp_xlsx = TEMP_DIR / "backup_completo_intern_manager.xlsx"
                        try:
                            container.export_service.export_to_excel(str(temp_xlsx))
                            ui.notify(
                                "Planilha completa gerada! Iniciando download...",
                                color="positive",
                            )
                            ui.download(
                                str(temp_xlsx), filename="backup_intern_manager.xlsx"
                            )
                        except Exception as e:
                            ui.notify(f"Erro ao exportar banco: {e}", color="negative")

                    with ui.card().classes(
                        "w-full p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 shadow-none flex-col sm:flex-row justify-between items-start sm:items-center gap-3"
                    ):
                        with ui.column().classes("gap-0.5"):
                            ui.label("Planilha Consolidada (Excel)").classes(
                                "font-bold text-sm text-slate-800"
                            )
                            ui.label(
                                "Exporta alunos, notas, documentos e locais em abas separadas."
                            ).classes("text-xs text-slate-500")
                        ui.button(
                            "Exportar (.xlsx)",
                            icon="download",
                            on_click=handle_excel_backup,
                        ).props("outline no-caps color=green-8").classes("w-full sm:w-auto")

                    def handle_sqlite_download():
                        if DB_PATH.exists():
                            ui.notify(
                                "Baixando arquivo do banco de dados...", color="positive"
                            )
                            ui.download(str(DB_PATH), filename=DB_PATH.name)
                        else:
                            ui.notify(
                                "Arquivo do banco de dados não encontrado.",
                                color="warning",
                            )

                    with ui.card().classes(
                        "w-full p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 shadow-none flex-col sm:flex-row justify-between items-start sm:items-center gap-3"
                    ):
                        with ui.column().classes("gap-0.5"):
                            ui.label("Cópia do Banco de Dados (.db)").classes(
                                "font-bold text-sm text-slate-800"
                            )
                            ui.label(
                                "Arquivo SQLite bruto para restauração direta."
                            ).classes("text-xs text-slate-500")
                        ui.button(
                            "Baixar Banco (.db)",
                            icon="cloud_download",
                            on_click=handle_sqlite_download,
                        ).props("outline no-caps color=blue-8").classes("w-full sm:w-auto")

                with ui.column().classes(
                    "w-full pt-3 border-t border-slate-100 text-[11px] text-slate-400 gap-0.5"
                ):
                    ui.label(f"Banco de Dados: {DB_PATH}").classes("truncate w-full")
                    ui.label(
                        "Concorrência: SQLite WAL (Write-Ahead Logging) • Interface Responsiva"
                    )
