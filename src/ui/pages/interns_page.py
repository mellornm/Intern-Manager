"""
Interns Management Page for NiceGUI.
Refactored with a 12-column tabular card grid on desktop and touch-friendly
responsive layout for tablet and mobile viewports.
"""

from typing import List, Optional
from nicegui import ui

from config import TEMP_DIR
from core.models.intern import Intern
from ui.components.status_badge import create_status_badge
from ui.context import ServiceContainer
from ui.dialogs.batch_dialogs import open_batch_document_dialog, open_batch_meeting_dialog
from ui.dialogs.document_dialog import open_document_dialog
from ui.dialogs.grade_dialog import open_grade_dialog
from ui.dialogs.intern_dialog import open_intern_dialog
from ui.dialogs.meeting_dialog import open_meeting_dialog
from ui.dialogs.observation_dialog import open_observation_dialog
from ui.dialogs.quick_view_dialogs import open_intern_quick_view
from ui.dialogs.report_dialog import export_batch_reports_zip, open_report_dialog
from ui.dialogs.visit_dialog import open_visit_dialog
from ui.layout import page_layout


def _get_initials(name: str) -> str:
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return "AL"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


def render_interns_page(container: ServiceContainer, initial_filter: Optional[str] = None):
    """Renders the comprehensive Interns list and action workflows."""
    with page_layout(title="Estagiários", active_path="/interns"):
        init_status = "Ativos"
        init_doc_filter = "Todos"
        init_venue_id = 0

        if initial_filter == "no_venue":
            init_venue_id = -1
        elif initial_filter == "pending_docs":
            init_doc_filter = "Com Pendência"

        state = {
            "search": "",
            "status": init_status,
            "doc_filter": init_doc_filter,
            "venue_id": init_venue_id,
            "selected_ids": set(),
        }

        venues = container.venue_service.get_all()
        venue_options = {0: "Todos os Locais", -1: "Sem Local (Não alocados)"}
        venue_options.update({v.venue_id: v.venue_name for v in venues if v.venue_id is not None})

        # Hidden CSV uploader modal to avoid visual pollution in the header
        async def handle_csv_upload(e):
            content = e.content.read()
            temp_csv = TEMP_DIR / e.name
            with open(temp_csv, "wb") as f:
                f.write(content)
            try:
                container.import_service.read_file(temp_csv)
                ui.notify(f"Arquivo CSV '{e.name}' importado com sucesso!", color="positive")
                csv_dialog.close()
                refresh_table()
            except Exception as err:
                ui.notify(f"Erro ao importar CSV: {err}", color="negative")
            finally:
                temp_csv.unlink(missing_ok=True)
                csv_uploader.reset()

        with ui.dialog() as csv_dialog, ui.card().classes("w-full max-w-md p-5 sm:p-6 rounded-2xl shadow-xl"):
            with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("upload_file", color="primary", size="sm")
                    ui.label("Importar Estagiários via CSV").classes("text-base font-bold text-slate-800")
                ui.button(icon="close", on_click=csv_dialog.close).props("flat round dense size=sm color=grey-7")
            ui.label(
                "Selecione um arquivo .csv padronizado para importar alunos em lote."
            ).classes("text-xs text-slate-500 py-2")
            csv_uploader = (
                ui.upload(
                    label="Arraste ou selecione o arquivo .CSV",
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_csv_upload,
                )
                .props('accept=".csv" flat bordered color=primary')
                .classes("w-full")
            )

        # 1. Clean Top Header: Title + Primary Actions + Secondary Dropdown
        with ui.row().classes("w-full justify-between items-start sm:items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0.5"):
                ui.label("Gestão de Estagiários").classes(
                    "text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Acompanhamento de vigência contratual, alocação em campo e conformidade documental."
                ).classes("text-xs sm:text-sm text-slate-500")

            with ui.row().classes("items-center gap-2 flex-wrap w-full sm:w-auto justify-end"):
                ui.button(
                    "Reunião Coletiva",
                    icon="groups",
                    on_click=lambda: open_batch_meeting_dialog(
                        intern_service=container.intern_service,
                        meeting_service=container.meeting_service,
                        venue_service=container.venue_service,
                        on_success=refresh_table,
                    ),
                ).props("outline no-caps color=primary").classes("px-3 flex-1 sm:flex-none")

                with ui.button("Dados & Relatórios", icon="import_export").props(
                    "outline no-caps color=slate-700 icon-right=arrow_drop_down"
                ).classes("px-3 text-slate-700 bg-white flex-1 sm:flex-none"):
                    with ui.menu().props("auto-close"):
                        with ui.menu_item(on_click=csv_dialog.open):
                            with ui.item_section().props("avatar"):
                                ui.icon("upload_file", color="primary", size="xs")
                            with ui.item_section():
                                ui.label("Importar CSV")
                        with ui.menu_item(on_click=lambda: handle_export_excel()):
                            with ui.item_section().props("avatar"):
                                ui.icon("table_view", color="green-7", size="xs")
                            with ui.item_section():
                                ui.label("Exportar Base (Excel)")
                        ui.separator()
                        with ui.menu_item(on_click=lambda: handle_batch_reports()):
                            with ui.item_section().props("avatar"):
                                ui.icon("picture_as_pdf", color="red-7", size="xs")
                            with ui.item_section():
                                ui.label("Exportar Relatórios (ZIP)")

                ui.button(
                    "Novo Estagiário",
                    icon="person_add",
                    on_click=lambda: open_intern_dialog(
                        intern_service=container.intern_service,
                        venue_service=container.venue_service,
                        on_success=refresh_table,
                    ),
                ).props("unelevated no-caps color=primary").classes(
                    "px-4 font-semibold shadow-xs w-full sm:w-auto"
                )

        # 2. Unified Filter & Search Toolbar (Responsive Grid on Mobile/Tablet -> Flex on Desktop)
        with ui.card().classes("w-full p-3 sm:p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-xs"):
            with ui.element("div").classes(
                "w-full grid grid-cols-1 sm:grid-cols-2 lg:flex items-center gap-2.5 sm:gap-3"
            ):
                search_input = (
                    ui.input(
                        placeholder="Buscar por nome ou matrícula (RA)...",
                        value=state["search"],
                    )
                    .classes("sm:col-span-2 lg:flex-1 w-full")
                    .props("outlined dense clearable debounce=250 hide-bottom-space")
                )
                with search_input.add_slot("prepend"):
                    ui.icon("search", size="xs").classes("text-slate-400")

                status_select = (
                    ui.select(
                        label="Status",
                        options=["Todos", "Ativos", "Inativos"],
                        value=state["status"],
                    )
                    .classes("w-full lg:w-36")
                    .props("outlined dense options-dense hide-bottom-space")
                )

                doc_filter_select = (
                    ui.select(
                        label="Documentação",
                        options=["Todos", "Com Pendência", "100% Conforme"],
                        value=state["doc_filter"],
                    )
                    .classes("w-full lg:w-44")
                    .props("outlined dense options-dense hide-bottom-space")
                )

                with ui.row().classes("sm:col-span-2 lg:w-auto items-center gap-2 no-wrap w-full"):
                    venue_select = (
                        ui.select(
                            label="Local de Estágio",
                            options=venue_options,
                            value=state["venue_id"],
                        )
                        .classes("flex-1 lg:w-56")
                        .props("outlined dense options-dense hide-bottom-space")
                    )

                    clear_btn = (
                        ui.button(icon="filter_alt_off")
                        .props("flat dense round color=grey-7")
                        .tooltip("Limpar todos os filtros")
                    )

        # 3. Contextual Batch Action Bar (Only visible when items are selected)
        batch_bar = ui.row().classes(
            "w-full px-3.5 py-2.5 bg-blue-900 text-white rounded-xl items-center justify-between gap-2 flex-wrap shadow-md transition-all"
        )
        batch_bar.set_visibility(False)

        with batch_bar:
            with ui.row().classes("items-center gap-2"):
                ui.icon("check_box", size="sm").classes("text-blue-200")
                batch_count_label = ui.label("0 selecionados").classes("text-xs sm:text-sm font-semibold")

            with ui.row().classes("items-center gap-1.5 sm:gap-2 flex-wrap"):
                ui.button(
                    "Aprovar Documento",
                    icon="done_all",
                    on_click=lambda: open_batch_document_dialog(
                        selected_intern_ids=list(state["selected_ids"]),
                        document_service=container.document_service,
                        on_success=refresh_table,
                    ),
                ).props("unelevated dense no-caps color=blue-7 text-color=white").classes("px-2.5 text-xs")

                ui.button(
                    "Relatórios (ZIP)",
                    icon="picture_as_pdf",
                    on_click=lambda: handle_batch_reports(),
                ).props("unelevated dense no-caps color=blue-7 text-color=white").classes("px-2.5 text-xs")

                ui.button(
                    "Limpar",
                    icon="close",
                    on_click=lambda: clear_selection(),
                ).props("flat dense no-caps color=white").classes("px-2 text-xs")

        # 4. List Container
        table_container = ui.column().classes("w-full gap-2.5")

        def update_batch_bar():
            count = len(state["selected_ids"])
            batch_bar.set_visibility(count > 0)
            batch_count_label.set_text(f"{count} estagiário(s) selecionado(s)")

        def clear_selection():
            state["selected_ids"].clear()
            update_batch_bar()
            refresh_table()

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
                if query:
                    name_match = query in (intern.name or "").lower()
                    ra_match = query in (intern.registration_number or "").lower()
                    if not (name_match or ra_match):
                        continue

                if status_f == "Ativos" and not intern.is_active:
                    continue
                if status_f == "Inativos" and intern.is_active:
                    continue

                if v_id == -1:
                    if intern.venue_id is not None:
                        continue
                elif v_id > 0:
                    if intern.venue_id != v_id:
                        continue

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
            filtered_ids = {i.intern_id for i in interns_list if i.intern_id is not None}
            all_selected = bool(filtered_ids) and filtered_ids.issubset(state["selected_ids"])
            update_batch_bar()

            with table_container:
                # Table Header Row + Select All
                with ui.row().classes(
                    "w-full px-3.5 py-2 bg-slate-100/80 border border-slate-200/70 rounded-lg items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider"
                ):
                    with ui.row().classes("items-center gap-2.5"):
                        select_all_chk = ui.checkbox(value=all_selected).props("dense")

                        def toggle_select_all(e):
                            if e.value:
                                state["selected_ids"].update(filtered_ids)
                            else:
                                state["selected_ids"].difference_update(filtered_ids)
                            refresh_table()

                        select_all_chk.on_value_change(toggle_select_all)
                        ui.label(f"Estagiários ({len(interns_list)})")

                    with ui.row().classes("hidden lg:flex items-center gap-16 pr-8"):
                        ui.label("Vigência do Contrato").classes("w-44")
                        ui.label("Conformidade Doc.").classes("w-36")
                        ui.label("Ações").classes("w-28 text-right")

                if not interns_list:
                    with ui.card().classes(
                        "w-full py-12 bg-white border border-slate-200/80 rounded-xl items-center justify-center gap-2 shadow-none"
                    ):
                        ui.icon("person_search", size="xl").classes("text-slate-300")
                        ui.label("Nenhum estagiário encontrado para os filtros aplicados.").classes(
                            "text-slate-600 font-semibold text-sm text-center px-4"
                        )
                        ui.label("Tente ajustar os termos de busca ou limpar os filtros.").classes(
                            "text-xs text-slate-400 text-center px-4"
                        )
                    return

                venue_cache = {
                    v.venue_id: v.venue_name
                    for v in container.venue_service.get_all()
                    if v.venue_id
                }

                for intern in interns_list:
                    i_id = intern.intern_id
                    has_venue = bool(intern.venue_id and intern.venue_id in venue_cache)
                    v_name = venue_cache.get(intern.venue_id, "Não alocado") if has_venue else "Sem local vinculado"

                    docs = container.document_service.get_by_intern_id(i_id) if i_id else []
                    approved_count = sum(1 for d in docs if (d.status or "").lower() == "aprovado")
                    total_docs = len(docs)
                    doc_pct = int((approved_count / total_docs) * 100) if total_docs > 0 else 0
                    doc_color = "green-7" if doc_pct == 100 else ("amber-8" if doc_pct >= 50 else "red-6")

                    meetings = container.meeting_service.get_by_intern_id(i_id) if i_id else []
                    present_meetings = sum(1 for m in meetings if m.is_intern_present)
                    obs_list = container.observation_service.get_by_intern_id(i_id) if i_id else []
                    incident_count = sum(1 for o in obs_list if getattr(o, "is_incident", False))

                    time_pct = intern.time_progress_percent
                    days_rem = intern.days_remaining
                    time_color = "amber-8" if intern.is_near_deadline else ("blue-7" if intern.is_active else "grey-6")

                    is_row_selected = i_id in state["selected_ids"]
                    row_border = (
                        "border-blue-500 bg-blue-50/20"
                        if is_row_selected
                        else "border-slate-200/80 bg-white hover:border-slate-300"
                    )

                    with ui.card().classes(
                        f"w-full px-3.5 sm:px-4 py-3 rounded-xl border {row_border} shadow-xs hover:shadow-sm transition-all"
                    ):
                        with ui.element("div").classes(
                            "w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 items-center gap-3 lg:gap-4"
                        ):
                            # COL 1-5: Checkbox + Avatar + Identity + Allocation Metadata
                            with ui.row().classes(
                                "sm:col-span-2 lg:col-span-5 items-start sm:items-center gap-3 no-wrap min-w-0"
                            ):
                                chk = ui.checkbox(value=is_row_selected).props("dense")

                                def on_check(e, current_id=i_id):
                                    if e.value:
                                        state["selected_ids"].add(current_id)
                                    else:
                                        state["selected_ids"].discard(current_id)
                                    update_batch_bar()

                                chk.on_value_change(on_check)

                                avatar_bg = "blue-1" if intern.is_active else "grey-3"
                                avatar_txt = "blue-9" if intern.is_active else "grey-7"
                                ui.avatar(
                                    _get_initials(intern.name),
                                    color=avatar_bg,
                                    text_color=avatar_txt,
                                    size="md",
                                ).classes("font-bold text-xs shrink-0 cursor-pointer").on(
                                    "click",
                                    lambda i=intern: open_intern_quick_view(
                                        i, container, on_change=refresh_table
                                    ),
                                )

                                with ui.column().classes("gap-1 min-w-0 flex-1"):
                                    with ui.row().classes("items-center gap-2 flex-wrap"):
                                        ui.label(intern.name).classes(
                                            "font-bold text-sm text-slate-900 hover:text-blue-700 cursor-pointer truncate transition-colors"
                                        ).on(
                                            "click",
                                            lambda i=intern: open_intern_quick_view(
                                                i, container, on_change=refresh_table
                                            ),
                                        ).tooltip("Clique para abrir o Dossiê 360° do aluno")
                                        create_status_badge(intern.status)
                                        if incident_count > 0:
                                            ui.badge(
                                                f"⚠️ {incident_count} ocorrência(s)",
                                                color="red-1",
                                                text_color="red-9",
                                            ).classes(
                                                "text-[10px] font-bold px-1.5 py-0.5 rounded border border-red-200 cursor-pointer"
                                            ).on(
                                                "click",
                                                lambda i=intern: open_observation_dialog(
                                                    intern=i,
                                                    service=container.observation_service,
                                                    on_close=refresh_table,
                                                ),
                                            )
                                        if intern.is_near_deadline and days_rem is not None:
                                            ui.badge(
                                                f"Expira em {days_rem}d", color="amber-9"
                                            ).props("outline").classes("text-[10px] font-bold px-1.5 py-0.5")

                                    with ui.row().classes(
                                        "items-center gap-x-3 gap-y-1 text-xs text-slate-500 flex-wrap"
                                    ):
                                        with ui.row().classes("items-center gap-1"):
                                            ui.icon("badge", size="14px").classes("text-slate-400")
                                            ui.label(f"RA: {intern.registration_number or 'S/N'}").classes("font-mono")

                                        with ui.row().classes("items-center gap-1"):
                                            ui.icon("calendar_today", size="13px").classes("text-slate-400")
                                            ui.label(intern.term or "N/I")

                                        with ui.row().classes("items-center gap-1"):
                                            ui.icon("event_available", size="14px").classes("text-slate-400")
                                            ui.label(f"{present_meetings}/{len(meetings)} reun.")

                                        with ui.row().classes("items-center gap-1 min-w-0"):
                                            ui.icon(
                                                "location_on" if has_venue else "warning_amber",
                                                size="14px",
                                            ).classes("text-blue-600 shrink-0" if has_venue else "text-amber-600 shrink-0")
                                            ui.label(v_name).classes(
                                                "font-medium text-slate-700 truncate max-w-44"
                                                if has_venue
                                                else "font-medium text-amber-700"
                                            )

                            # COL 6-8: Contract Validity & Time Progress
                            with ui.column().classes("sm:col-span-1 lg:col-span-3 gap-1 w-full"):
                                ui.label("VIGÊNCIA").classes(
                                    "lg:hidden text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                with ui.row().classes("w-full justify-between items-center text-xs"):
                                    ui.label(
                                        f"{intern.formatted_start_date} → {intern.formatted_end_date}"
                                    ).classes("font-medium text-slate-600")
                                    if days_rem is not None and intern.is_active:
                                        rem_label = f"{days_rem}d rest." if days_rem >= 0 else "Encerrado"
                                        ui.label(rem_label).classes(
                                            "text-[11px] font-semibold "
                                            + ("text-amber-700" if intern.is_near_deadline else "text-slate-400")
                                        )
                                ui.linear_progress(
                                    value=time_pct / 100.0,
                                    show_value=False,
                                    color=time_color,
                                ).props("rounded size=6px track-color=grey-3").classes("w-full")
                                if intern.working_days or intern.working_hours:
                                    ui.label(
                                        f"{intern.working_days or ''} • {intern.working_hours or ''}".strip(" •")
                                    ).classes("text-[11px] text-slate-400 truncate")

                            # COL 9-10: Document Compliance Progress (Clickable)
                            with ui.column().classes(
                                "sm:col-span-1 lg:col-span-2 gap-1 w-full cursor-pointer group"
                            ).on(
                                "click",
                                lambda i=intern: open_document_dialog(
                                    intern=i,
                                    service=container.document_service,
                                    on_close=refresh_table,
                                ),
                            ):
                                ui.label("DOCUMENTOS").classes(
                                    "lg:hidden text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                with ui.row().classes("w-full justify-between items-center text-xs"):
                                    ui.label(f"{approved_count}/{total_docs} aprovados").classes(
                                        "font-semibold text-slate-700 group-hover:text-blue-700 transition-colors"
                                    )
                                    ui.label(f"{doc_pct}%").classes("text-[11px] font-bold text-slate-500")
                                ui.linear_progress(
                                    value=(approved_count / total_docs) if total_docs > 0 else 0.0,
                                    show_value=False,
                                    color=doc_color,
                                ).props("rounded size=6px track-color=grey-3").classes("w-full")

                            # COL 11-12: Quick Actions & Structured Context Menu
                            with ui.row().classes(
                                "sm:col-span-2 lg:col-span-2 items-center justify-end gap-1 pt-2 lg:pt-0 border-t border-slate-100 lg:border-0 w-full"
                            ):
                                ui.button(
                                    icon="visibility",
                                    on_click=lambda i=intern: open_intern_quick_view(
                                        i,
                                        container=container,
                                        on_change=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=blue-8").tooltip(
                                    "Dossiê 360° (Visualização Rápida)"
                                )

                                ui.button(
                                    icon="folder_open",
                                    on_click=lambda i=intern: open_document_dialog(
                                        intern=i,
                                        service=container.document_service,
                                        on_close=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=primary").tooltip(
                                    "Auditoria de Documentos"
                                )

                                ui.button(
                                    icon="grade",
                                    on_click=lambda i=intern: open_grade_dialog(
                                        intern=i,
                                        criteria_service=container.criteria_service,
                                        grade_service=container.grade_service,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=amber-8").tooltip(
                                    "Notas e Avaliação"
                                )

                                with ui.button(icon="more_vert").props(
                                    "flat round dense size=sm color=slate-600"
                                ):
                                    with ui.menu().props("auto-close"):
                                        with ui.menu_item(
                                            on_click=lambda i=intern: open_intern_dialog(
                                                intern_service=container.intern_service,
                                                venue_service=container.venue_service,
                                                intern=i,
                                                on_success=refresh_table,
                                            )
                                        ):
                                            with ui.item_section().props("avatar"):
                                                ui.icon("edit", color="slate-700", size="xs")
                                            with ui.item_section():
                                                ui.label("Editar Cadastro")

                                        with ui.menu_item(
                                            on_click=lambda i=intern: open_observation_dialog(
                                                intern=i,
                                                service=container.observation_service,
                                                on_close=refresh_table,
                                            )
                                        ):
                                            with ui.item_section().props("avatar"):
                                                ui.icon("assignment_late", color="red-7", size="xs")
                                            with ui.item_section():
                                                ui.label("Observações e Ocorrências (Anexos)")

                                        with ui.menu_item(
                                            on_click=lambda i=intern: open_meeting_dialog(
                                                intern=i,
                                                service=container.meeting_service,
                                                on_close=refresh_table,
                                            )
                                        ):
                                            with ui.item_section().props("avatar"):
                                                ui.icon("event_available", color="primary", size="xs")
                                            with ui.item_section():
                                                ui.label("Reuniões de Supervisão")

                                        with ui.menu_item(
                                            on_click=lambda i=intern: open_visit_dialog(
                                                intern=i,
                                                service=container.visit_service,
                                                venue_service=container.venue_service,
                                                on_close=refresh_table,
                                            )
                                        ):
                                            with ui.item_section().props("avatar"):
                                                ui.icon("pin_drop", color="green-7", size="xs")
                                            with ui.item_section():
                                                ui.label("Visitas Técnicas in loco")

                                        ui.separator()

                                        with ui.menu_item(
                                            on_click=lambda i=intern: open_report_dialog(
                                                intern=i,
                                                container=container,
                                            )
                                        ):
                                            with ui.item_section().props("avatar"):
                                                ui.icon("picture_as_pdf", color="red-7", size="xs")
                                            with ui.item_section():
                                                ui.label("Relatório Individual (PDF)")

                                        ui.separator()

                                        with ui.menu_item(
                                            on_click=lambda i=intern: toggle_intern_active(i)
                                        ):
                                            with ui.item_section().props("avatar"):
                                                ui.icon(
                                                    "person_off" if intern.is_active else "person_check",
                                                    color="amber-8",
                                                    size="xs",
                                                )
                                            with ui.item_section():
                                                ui.label(
                                                    "Marcar como Concluído/Inativo"
                                                    if intern.is_active
                                                    else "Reativar Estagiário"
                                                )

                                        with ui.menu_item(
                                            on_click=lambda i=intern: confirm_delete_intern(i)
                                        ).classes("text-red-600"):
                                            with ui.item_section().props("avatar"):
                                                ui.icon("delete_outline", color="red-6", size="xs")
                                            with ui.item_section():
                                                ui.label("Excluir Estagiário")

        def toggle_intern_active(intern: Intern):
            intern.is_active = not intern.is_active
            container.intern_service.update_intern(intern)
            ui.notify(
                f"Aluno {'reativado' if intern.is_active else 'marcado como concluído'} com sucesso!",
                color="info",
            )
            refresh_table()

        def confirm_delete_intern(intern: Intern):
            with ui.dialog() as del_dialog, ui.card().classes("p-5 sm:p-6 rounded-2xl max-w-md w-full"):
                with ui.row().classes("items-center gap-3 pb-2"):
                    ui.avatar("warning_amber", color="red-1", text_color="red-7", size="md")
                    with ui.column().classes("gap-0"):
                        ui.label("Confirmar Exclusão").classes("text-base font-bold text-slate-900")
                        ui.label("Esta ação removerá todo o histórico do aluno.").classes(
                            "text-xs text-slate-500"
                        )

                ui.label(
                    f"Deseja realmente excluir permanentemente o estagiário '{intern.name}' (RA: {intern.registration_number})?"
                ).classes("text-sm text-slate-700 py-2")

                with ui.row().classes("w-full justify-end gap-2 pt-3 border-t border-slate-100"):
                    ui.button("Cancelar", on_click=del_dialog.close).props("flat no-caps color=grey-7")

                    def do_delete():
                        if intern.intern_id:
                            container.intern_service.delete_intern(intern.intern_id)
                            state["selected_ids"].discard(intern.intern_id)
                            ui.notify("Estagiário excluído.", color="info")
                            del_dialog.close()
                            refresh_table()

                    ui.button("Excluir Permanentemente", icon="delete", on_click=do_delete).props(
                        "unelevated no-caps color=negative"
                    )
            del_dialog.open()

        # Connect filter handlers
        search_input.on_value_change(lambda e: (state.update({"search": e.value or ""}), refresh_table()))
        status_select.on_value_change(lambda e: (state.update({"status": e.value or "Todos"}), refresh_table()))
        doc_filter_select.on_value_change(lambda e: (state.update({"doc_filter": e.value or "Todos"}), refresh_table()))
        venue_select.on_value_change(
            lambda e: (state.update({"venue_id": int(e.value if e.value is not None else 0)}), refresh_table())
        )

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
