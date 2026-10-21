"""
Dashboard Page for InternManager Pro Web.
Interactive KPIs and ECharts visualizations optimized for PC, Tablet, and Mobile.
"""

from nicegui import ui
from ui.components.kpi_card import create_kpi_card
from ui.context import ServiceContainer
from ui.layout import page_layout


DOC_TYPES = [
    "Todos",
    "Contrato de Estágio",
    "Ficha de Frequência",
    "Diário de Campo",
    "Projeto de Intervenção",
    "Avaliação do Supervisor Local",
]


def render_dashboard_page(container: ServiceContainer):
    """Renders the dashboard page within page_layout."""
    with page_layout(title="Dashboard", active_path="/"):
        # Header banner
        with ui.row().classes("w-full justify-between items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0.5"):
                ui.label("Monitoramento de Estágio").classes(
                    "text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Visão executiva de alocação em campo, supervisões e conformidade documental."
                ).classes("text-xs sm:text-sm text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button(
                    "Ver Estagiários",
                    icon="groups",
                    on_click=lambda: ui.navigate.to("/interns"),
                ).props("outline no-caps color=primary size=sm").classes("px-3")
                refresh_btn = (
                    ui.button("Atualizar", icon="refresh")
                    .props("unelevated no-caps color=primary size=sm")
                    .classes("px-3")
                )

        # KPI Metrics Grid Container (1 col mobile, 2 cols tablet, 4 cols desktop)
        kpi_container = ui.grid(columns=1).classes(
            "w-full sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4"
        )

        # Charts Area Container
        charts_container = ui.grid(columns=1).classes("w-full lg:grid-cols-2 gap-4 sm:gap-6")

        state = {"filter_doc": "Todos"}

        def refresh_all():
            total_interns = container.intern_service.repo.count_total()
            no_venue_count = container.intern_service.repo.count_without_venue()
            active_interns = [
                i for i in container.intern_service.get_all_interns() if i.is_active
            ]
            active_count = len(active_interns)

            if state["filter_doc"] == "Todos":
                total_pending = container.document_service.count_total_pending()
            else:
                pending_ids = (
                    container.document_service.repo.get_intern_ids_with_pending_docs(
                        state["filter_doc"]
                    )
                )
                total_pending = len(pending_ids)

            meetings_month = container.meeting_service.repo.count_this_month()

            # Render KPIs
            kpi_container.clear()
            with kpi_container:
                create_kpi_card(
                    title="Total de Estagiários",
                    value=total_interns,
                    subtitle=f"{active_count} ativo(s) no semestre",
                    icon="school",
                    color_class="text-blue-600",
                    bg_color_class="bg-blue-50",
                    border_color_class="border-l-blue-600",
                    icon_border_class="border-blue-200/70",
                    on_click=lambda: ui.navigate.to("/interns"),
                )

                create_kpi_card(
                    title="Sem Local Vinculado",
                    value=no_venue_count,
                    subtitle="Aguardando alocação em campo" if no_venue_count else "100% alocados",
                    icon="location_off",
                    color_class="text-rose-600",
                    bg_color_class="bg-rose-50",
                    border_color_class="border-l-rose-600",
                    icon_border_class="border-rose-200/70",
                    on_click=lambda: ui.navigate.to("/interns?filter=no_venue"),
                )

                pending_title = (
                    "Docs Pendentes"
                    if state["filter_doc"] == "Todos"
                    else f"Pend.: {state['filter_doc']}"
                )
                create_kpi_card(
                    title=pending_title,
                    value=total_pending,
                    subtitle="Clique para auditar pendências",
                    icon="assignment_late",
                    color_class="text-amber-600",
                    bg_color_class="bg-amber-50",
                    border_color_class="border-l-amber-500",
                    icon_border_class="border-amber-200/70",
                    on_click=lambda: ui.navigate.to("/interns?filter=pending_docs"),
                )

                create_kpi_card(
                    title="Reuniões no Mês",
                    value=meetings_month,
                    subtitle="Supervisões registradas",
                    icon="event_available",
                    color_class="text-emerald-600",
                    bg_color_class="bg-emerald-50",
                    border_color_class="border-l-emerald-600",
                    icon_border_class="border-emerald-200/70",
                    on_click=lambda: ui.navigate.to("/calendar"),
                )

            # Render Charts
            charts_container.clear()
            with charts_container:
                # Chart 1: Venue Distribution (Donut Chart)
                with ui.card().classes(
                    "p-4 sm:p-5 bg-white border border-slate-200/80 rounded-xl shadow-xs flex flex-col gap-2"
                ):
                    with ui.row().classes(
                        "w-full justify-between items-center pb-2 border-b border-slate-100"
                    ):
                        with ui.column().classes("gap-0"):
                            ui.label("Taxa de Alocação em Campo").classes(
                                "text-sm sm:text-base font-bold text-slate-800"
                            )
                            ui.label("Proporção de alunos vinculados a instituições").classes(
                                "text-xs text-slate-400"
                            )
                        ui.badge(
                            f"{max(total_interns - no_venue_count, 0)}/{total_interns} alocados",
                            color="blue-1",
                            text_color="blue-9",
                        ).classes("text-xs font-semibold px-2 py-0.5 rounded")

                    allocated = max(total_interns - no_venue_count, 0)

                    donut_options = {
                        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
                        "legend": {"bottom": "0%", "left": "center"},
                        "color": ["#10b981", "#f43f5e"],
                        "series": [
                            {
                                "name": "Alocação",
                                "type": "pie",
                                "radius": ["48%", "72%"],
                                "center": ["50%", "45%"],
                                "avoidLabelOverlap": False,
                                "itemStyle": {
                                    "borderRadius": 8,
                                    "borderColor": "#fff",
                                    "borderWidth": 2,
                                },
                                "label": {
                                    "show": True,
                                    "formatter": "{b}\n{d}%",
                                    "fontWeight": "bold",
                                },
                                "data": [
                                    {"value": allocated, "name": "Alocados"},
                                    {"value": no_venue_count, "name": "Sem Local"},
                                ],
                            }
                        ],
                    }
                    ui.echart(donut_options).classes("w-full h-64 sm:h-72")

                # Chart 2: Document Status (Bar Chart with filter)
                with ui.card().classes(
                    "p-4 sm:p-5 bg-white border border-slate-200/80 rounded-xl shadow-xs flex flex-col gap-2"
                ):
                    with ui.row().classes(
                        "w-full justify-between items-center gap-2 pb-2 border-b border-slate-100 flex-wrap"
                    ):
                        with ui.column().classes("gap-0"):
                            ui.label("Conformidade Documental").classes(
                                "text-sm sm:text-base font-bold text-slate-800"
                            )
                            ui.label("Alunos ativos com documentação aprovada vs. pendente").classes(
                                "text-xs text-slate-400"
                            )
                        doc_select = (
                            ui.select(
                                label="Filtrar Documento",
                                options=DOC_TYPES,
                                value=state["filter_doc"],
                            )
                            .classes("w-full sm:w-52")
                            .props("dense outlined options-dense hide-bottom-space")
                        )

                        def on_doc_change(e):
                            state["filter_doc"] = e.value
                            refresh_all()

                        doc_select.on_value_change(on_doc_change)

                    filter_name = state["filter_doc"]
                    ok_count = 0
                    pending_count = 0

                    if filter_name == "Todos":
                        for i in active_interns:
                            docs = container.document_service.get_by_intern_id(i.intern_id)
                            if not docs or any(
                                (d.status or "").lower() != "aprovado" for d in docs
                            ):
                                pending_count += 1
                            else:
                                ok_count += 1
                    else:
                        for i in active_interns:
                            docs = container.document_service.get_by_intern_id(i.intern_id)
                            target_docs = [
                                d
                                for d in docs
                                if filter_name.lower() in (d.document_name or "").lower()
                            ]
                            if not target_docs or not any(
                                (d.status or "").lower() == "aprovado" for d in target_docs
                            ):
                                pending_count += 1
                            else:
                                ok_count += 1

                    bar_options = {
                        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                        "grid": {
                            "left": "3%",
                            "right": "8%",
                            "top": "10%",
                            "bottom": "8%",
                            "containLabel": True,
                        },
                        "xAxis": {"type": "value", "minInterval": 1},
                        "yAxis": {
                            "type": "category",
                            "data": ["Com Pendência", "Regular (Aprovado)"],
                        },
                        "series": [
                            {
                                "type": "bar",
                                "barWidth": "45%",
                                "itemStyle": {"borderRadius": [0, 6, 6, 0]},
                                "data": [
                                    {
                                        "value": pending_count,
                                        "itemStyle": {"color": "#f59e0b"},
                                    },
                                    {"value": ok_count, "itemStyle": {"color": "#10b981"}},
                                ],
                                "label": {
                                    "show": True,
                                    "position": "right",
                                    "fontWeight": "bold",
                                },
                            }
                        ],
                    }
                    ui.echart(bar_options).classes("w-full h-64 sm:h-72")

        refresh_btn.on("click", refresh_all)
        refresh_all()
