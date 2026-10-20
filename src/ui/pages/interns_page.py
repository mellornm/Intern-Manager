"""
Interns Management Page for NiceGUI.
Search, multi-dimensional filters, batch actions, CSV import, Excel export, and row-level workflows.
"""

from typing import List, Optional
from nicegui import ui

from config import TEMP_DIR
from core.models.intern import Intern
from ui.components.status_badge import create_progress_pill, create_status_badge
from ui.context import ServiceContainer
from ui.dialogs.batch_dialogs import open_batch_document_dialog, open_batch_meeting_dialog
from ui.dialogs.document_dialog import open_document_dialog
from ui.dialogs.grade_dialog import open_grade_dialog
from ui.dialogs.intern_dialog import open_intern_dialog
from ui.dialogs.meeting_dialog import open_meeting_dialog
from ui.dialogs.observation_dialog import open_observation_dialog
from ui.dialogs.report_dialog import export_batch_reports_zip, open_report_dialog
from ui.dialogs.visit_dialog import open_visit_dialog
from ui.layout import page_layout
from utils.validations import format_date_to_br


def render_interns_page(container: ServiceContainer, initial_filter: Optional[str] = None):
    """Renders the comprehensive Interns list and action workflows."""
    with page_layout(title="Estagiários", active_path="/interns"):
        # Initial filter mapping from dashboard links
        init_status = "Ativos"
        init_doc_filter = "Todos"
        init_venue_id = 0

        if initial_filter == "no_venue":
            init_venue_id = -1  # Special code for 'Sem Local'
        elif initial_filter == "pending_docs":
            init_doc_filter = "Com Pendência"

        # Session state for filters
        state = {
            "search": "",
            "status": init_status,
            "doc_filter": init_doc_filter,
            "venue_id": init_venue_id,
            "selected_ids": set(),
        }

        venues = container.venue_service.get_all()
        venue_options = {0: "Todos os Locais", -1: "⚠️ Sem Local (Não alocados)"}
        venue_options.update({v.venue_id: v.venue_name for v in venues if v.venue_id is not None})

        # Header Title and Top Actions
        with ui.row().classes("w-full justify-between items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0"):
                ui.label("Estagiários").classes("text-2xl sm:text-3xl font-extrabold text-slate-900")
                ui.label("Gerenciamento acadêmico, alocações e conformidade.").classes("text-sm text-slate-500")

            with ui.row().classes("gap-2 flex-wrap items-center"):
                ui.button(
                    "Novo Aluno",
                    icon="person_add",
                    on_click=lambda: open_intern_dialog(
                        intern_service=container.intern_service,
                        venue_service=container.venue_service,
                        on_success=refresh_table,
                    ),
                ).props("color=primary")

                ui.button(
                    "Aprovação em Lote",
                    icon="done_all",
                    on_click=lambda: open_batch_document_dialog(
                        selected_intern_ids=list(state["selected_ids"]),
                        document_service=container.document_service,
                        on_success=refresh_table,
                    ),
                ).props("outline color=primary")

                ui.button(
                    "Reunião em Grupo",
                    icon="groups",
                    on_click=lambda: open_batch_meeting_dialog(
                        intern_service=container.intern_service,
                        meeting_service=container.meeting_service,
                        venue_service=container.venue_service,
                        on_success=refresh_table,
                    ),
                ).props("outline color=primary")

                ui.button(
                    "Relatórios em Lote",
                    icon="picture_as_pdf",
                    on_click=lambda: handle_batch_reports(),
                ).props("outline color=negative")

                ui.button(
                    "Exportar Excel",
                    icon="file_download",
                    on_click=lambda: handle_export_excel(),
                ).props("outline color=green-8")

                # CSV Import Upload
                async def handle_csv_upload(e):
                    content = e.content.read()
                    temp_csv = TEMP_DIR / e.name
                    with open(temp_csv, "wb") as f:
                        f.write(content)
                    try:
                        container.import_service.read_file(temp_csv)
                        ui.notify(f"Arquivo CSV '{e.name}' importado com sucesso!", color="positive")
                        refresh_table()
                    except Exception as err:
                        ui.notify(f"Erro ao importar CSV: {err}", color="negative")
                    finally:
                        temp_csv.unlink(missing_ok=True)

                ui.upload(
                    label="Importar CSV",
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_csv_upload,
                ).props('accept=".csv" flat size=sm color=primary').classes("max-w-xs")

        # Filters Card
        with ui.card().classes("w-full p-4 card-shadow"):
            with ui.row().classes("w-full items-center gap-4 flex-wrap"):
                search_input = ui.input(
                    placeholder="Buscar por nome ou RA...",
                    value=state["search"],
                ).classes("flex-1 min-w-48").props("outlined dense")
                with search_input.add_slot("prepend"):
                    ui.icon("search")

                status_select = ui.select(
                    label="Status do Aluno",
                    options=["Todos", "Ativos", "Inativos"],
                    value=state["status"],
                ).classes("w-36").props("outlined dense")

                doc_filter_select = ui.select(
                    label="Situação Documental",
                    options=["Todos", "Com Pendência", "100% Conforme"],
                    value=state["doc_filter"],
                ).classes("w-44").props("outlined dense")

                venue_select = ui.select(
                    label="Local de Estágio",
                    options=venue_options,
                    value=state["venue_id"],
                ).classes("w-56").props("outlined dense")

                clear_btn = ui.button("Limpar Filtros", icon="filter_alt_off").props("flat color=grey size=sm")

        # Table Container
        table_container = ui.column().classes("w-full gap-2")

        def handle_export_excel():
            temp_xlsx = TEMP_DIR / "interns_database_export.xlsx"
            try:
                container.export_service.export_to_excel(str(temp_xlsx))
                ui.notify("Planilha Excel gerada! Baixando arquivo...", color="positive")
                ui.download(str(temp_xlsx), filename="interns_export.xlsx")
            except Exception as e:
                ui.notify(f"Erro ao exportar Excel: {e}", color="negative")

        def handle_batch_reports():
            target_ids = list(state["selected_ids"])
            if not target_ids:
                # If none selected, offer to export all currently filtered
                all_filtered_ids = [
                    i.intern_id for i in get_filtered_interns() if i.intern_id is not None
                ]
                if not all_filtered_ids:
                    ui.notify("Nenhum aluno encontrado para gerar relatórios.", color="warning")
                    return
                target_ids = all_filtered_ids

            export_batch_reports_zip(target_ids, container)

        def get_filtered_interns() -> List[Intern]:
            all_interns = container.intern_service.get_all_interns()
            query = state["search"].lower().strip()
            status_f = state["status"]
            doc_f = state["doc_filter"]
            v_id = state["venue_id"]

            filtered = []
            for intern in all_interns:
                # Text search (Name or RA)
                if query:
                    name_match = query in (intern.name or "").lower()
                    ra_match = query in (intern.registration_number or "").lower()
                    if not (name_match or ra_match):
                        continue

                # Status filter
                if status_f == "Ativos" and not intern.is_active:
                    continue
                if status_f == "Inativos" and intern.is_active:
                    continue

                # Venue filter
                if v_id == -1:  # Without venue
                    if intern.venue_id is not None:
                        continue
                elif v_id > 0:
                    if intern.venue_id != v_id:
                        continue

                # Document status filter
                if doc_f != "Todos" and intern.intern_id:
                    docs = container.document_service.get_by_intern_id(intern.intern_id)
                    has_pending = not docs or any((d.status or "").lower() != "aprovado" for d in docs)
                    if doc_f == "Com Pendência" and not has_pending:
                        continue
                    if doc_f == "100% Conforme" and has_pending:
                        continue

                filtered.append(intern)

            return filtered

        def refresh_table():
            table_container.clear()
            interns_list = get_filtered_interns()

            with table_container:
                # Counter banner
                with ui.row().classes("w-full justify-between items-center px-1 text-xs text-slate-500"):
                    ui.label(f"Exibindo {len(interns_list)} estagiário(s)")
                    selected_label = ui.label(
                        f"✓ {len(state['selected_ids'])} aluno(s) selecionado(s) para ações em lote"
                        if state["selected_ids"]
                        else ""
                    ).classes("font-bold text-blue-700")

                if not interns_list:
                    with ui.card().classes("w-full p-8 card-shadow items-center justify-center gap-2"):
                        ui.icon("person_off", size="xl").classes("text-slate-300")
                        ui.label("Nenhum estagiário encontrado com os filtros atuais.").classes("text-slate-500 font-medium")
                    return

                # Table of interns
                venue_cache = {v.venue_id: v.venue_name for v in container.venue_service.get_all() if v.venue_id}

                for intern in interns_list:
                    i_id = intern.intern_id
                    v_name = venue_cache.get(intern.venue_id, "⚠️ Sem Local") if intern.venue_id else "⚠️ Sem Local"
                    docs = container.document_service.get_by_intern_id(i_id) if i_id else []
                    approved_count = sum(1 for d in docs if (d.status or "").lower() == "aprovado")
                    total_docs = len(docs)

                    with ui.card().classes("w-full p-4 card-shadow flex-col sm:flex-row items-start sm:items-center justify-between gap-3"):
                        # Selection Checkbox + Identity
                        with ui.row().classes("items-center gap-3"):
                            chk = ui.checkbox(value=(i_id in state["selected_ids"]))

                            def on_check(e, current_id=i_id):
                                if e.value:
                                    state["selected_ids"].add(current_id)
                                else:
                                    state["selected_ids"].discard(current_id)
                                selected_label.text = (
                                    f"✓ {len(state['selected_ids'])} aluno(s) selecionado(s) para ações em lote"
                                    if state["selected_ids"]
                                    else ""
                                )

                            chk.on_value_change(on_check)

                            with ui.column().classes("gap-0"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label(intern.name).classes("font-bold text-base text-slate-900")
                                    create_status_badge("Ativo" if intern.is_active else "Inativo")

                                with ui.row().classes("items-center gap-2 text-xs text-slate-500"):
                                    ui.label(f"RA: {intern.registration_number or 'S/N'}")
                                    ui.label(f"• Semestre: {intern.term or 'N/I'}")
                                    ui.label(f"• Local: {v_name}").classes("font-semibold text-slate-700")

                        # Progress & Period
                        with ui.row().classes("items-center gap-6"):
                            with ui.column().classes("gap-1 items-start sm:items-center"):
                                ui.label("DOCUMENTOS").classes("text-xs font-bold text-slate-400")
                                create_progress_pill(approved_count, total_docs)

                            if intern.start_date and intern.end_date:
                                with ui.column().classes("gap-0 text-xs text-slate-500"):
                                    ui.label("VIGÊNCIA").classes("font-bold text-slate-400 text-xs")
                                    ui.label(f"{format_date_to_br(str(intern.start_date))} até {format_date_to_br(str(intern.end_date))}")

                            # Actions Menu
                            with ui.row().classes("items-center gap-1"):
                                ui.button(
                                    icon="edit",
                                    on_click=lambda i=intern: open_intern_dialog(
                                        intern_service=container.intern_service,
                                        venue_service=container.venue_service,
                                        intern=i,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=primary").tooltip("Editar Dados")

                                ui.button(
                                    icon="description",
                                    on_click=lambda i=intern: open_document_dialog(
                                        intern=i,
                                        service=container.document_service,
                                        on_close=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=primary").tooltip("Documentos & Auditoria")

                                ui.button(
                                    icon="grade",
                                    on_click=lambda i=intern: open_grade_dialog(
                                        intern=i,
                                        criteria_service=container.criteria_service,
                                        grade_service=container.grade_service,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=amber-8").tooltip("Notas e Avaliação")

                                # Dropdown with more actions
                                with ui.button(icon="more_vert").props("flat round dense size=sm color=grey"):
                                    with ui.menu():
                                        ui.menu_item(
                                            "Observações Pedagógicas",
                                            on_click=lambda i=intern: open_observation_dialog(
                                                intern=i,
                                                service=container.observation_service,
                                            ),
                                        )
                                        ui.menu_item(
                                            "Reuniões de Supervisão",
                                            on_click=lambda i=intern: open_meeting_dialog(
                                                intern=i,
                                                service=container.meeting_service,
                                            ),
                                        )
                                        ui.menu_item(
                                            "Visitas Técnicas in loco",
                                            on_click=lambda i=intern: open_visit_dialog(
                                                intern=i,
                                                service=container.visit_service,
                                                venue_service=container.venue_service,
                                            ),
                                        )
                                        ui.separator()
                                        ui.menu_item(
                                            "Gerar Relatório Individual (PDF)",
                                            on_click=lambda i=intern: open_report_dialog(
                                                intern=i,
                                                container=container,
                                            ),
                                        )
                                        ui.separator()
                                        ui.menu_item(
                                            "Inativar Aluno" if intern.is_active else "Ativar Aluno",
                                            on_click=lambda i=intern: toggle_intern_active(i),
                                        )
                                        ui.menu_item(
                                            "Excluir Aluno",
                                            on_click=lambda i=intern: confirm_delete_intern(i),
                                        ).classes("text-red-600")

        def toggle_intern_active(intern: Intern):
            intern.is_active = not intern.is_active
            container.intern_service.update_intern(intern)
            ui.notify(f"Aluno {'ativado' if intern.is_active else 'inativado'} com sucesso!", color="info")
            refresh_table()

        def confirm_delete_intern(intern: Intern):
            with ui.dialog() as del_dialog, ui.card().classes("p-6 dialog-card"):
                ui.label("Confirmar Exclusão").classes("text-lg font-bold text-slate-800")
                ui.label(f"Deseja realmente excluir permanentemente o aluno '{intern.name}'?").classes("text-sm text-slate-600")
                with ui.row().classes("w-full justify-end gap-2 pt-4"):
                    ui.button("Cancelar", on_click=del_dialog.close).props("flat color=grey")

                    def do_delete():
                        if intern.intern_id:
                            container.intern_service.delete_intern(intern.intern_id)
                            ui.notify("Aluno excluído.", color="info")
                            del_dialog.close()
                            refresh_table()

                    ui.button("Excluir", icon="delete", on_click=do_delete).props("color=negative")
            del_dialog.open()

        # Connect filter handlers
        search_input.on_value_change(lambda e: (state.update({"search": e.value or ""}), refresh_table()))
        status_select.on_value_change(lambda e: (state.update({"status": e.value or "Todos"}), refresh_table()))
        doc_filter_select.on_value_change(lambda e: (state.update({"doc_filter": e.value or "Todos"}), refresh_table()))
        venue_select.on_value_change(lambda e: (state.update({"venue_id": int(e.value if e.value is not None else 0)}), refresh_table()))

        def clear_filters():
            state["search"] = ""
            state["status"] = "Todos"
            state["doc_filter"] = "Todos"
            state["venue_id"] = 0
            search_input.value = ""
            status_select.value = "Todos"
            doc_filter_select.value = "Todos"
            venue_select.value = 0
            refresh_table()

        clear_btn.on("click", clear_filters)

        refresh_table()
