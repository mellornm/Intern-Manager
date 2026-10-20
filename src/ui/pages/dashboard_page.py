"""
Dashboard Page for InternManager Pro Web.
Interactive KPIs and ECharts visualizations for venue distribution and document status.
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
        with ui.row().classes("w-full justify-between items-center"):
            with ui.column().classes("gap-0"):
                ui.label("Monitoramento de Estágio").classes("text-2xl sm:text-3xl font-extrabold text-slate-900")
                ui.label("Status de alocação de locais e conformidade documental.").classes("text-sm text-slate-500")

            refresh_btn = ui.button("Atualizar Dados", icon="refresh").props("color=primary size=sm")

        # KPI Metrics Grid Container
        kpi_container = ui.grid(columns=1).classes("w-full sm:grid-cols-2 lg:grid-cols-4 gap-4")

        # Charts Area Container
        charts_container = ui.grid(columns=1).classes("w-full lg:grid-cols-2 gap-6")

        # Session state for doc filter
        state = {"filter_doc": "Todos"}

        def refresh_all():
            total_interns = container.intern_service.repo.count_total()
            no_venue_count = container.intern_service.repo.count_without_venue()
            active_interns = [i for i in container.intern_service.get_all_interns() if i.is_active]

            # Pending documents count
            if state["filter_doc"] == "Todos":
                total_pending = container.document_service.count_total_pending()
            else:
                pending_ids = container.document_service.repo.get_intern_ids_with_pending_docs(state["filter_doc"])
                total_pending = len(pending_ids)

            meetings_month = container.meeting_service.repo.count_this_month()

            # Render KPIs
            kpi_container.clear()
            with kpi_container:
                create_kpi_card(
                    title="Total Alunos",
                    value=total_interns,
                    icon="school",
                    color_class="text-blue-600",
                    bg_color_class="bg-blue-100",
                    on_click=lambda: ui.navigate.to("/interns"),
                )

                create_kpi_card(
                    title="Sem Local",
                    value=no_venue_count,
                    icon="location_off",
                    color_class="text-red-600",
                    bg_color_class="bg-red-100",
                    on_click=lambda: ui.navigate.to("/interns?filter=no_venue"),
                )

                pending_title = "Todos Pendentes" if state["filter_doc"] == "Todos" else f"Pendentes: {state['filter_doc']}"
                create_kpi_card(
                    title=pending_title,
                    value=total_pending,
                    icon="assignment_late",
                    color_class="text-amber-600",
                    bg_color_class="bg-amber-100",
                    on_click=lambda: ui.navigate.to("/interns?filter=pending_docs"),
                )

                create_kpi_card(
                    title="Reuniões (Mês)",
                    value=meetings_month,
                    icon="event",
                    color_class="text-green-600",
                    bg_color_class="bg-green-100",
                    on_click=lambda: ui.navigate.to("/calendar"),
                )

            # Render Charts
            charts_container.clear()
            with charts_container:
                # Chart 1: Venue Distribution (Donut Chart)
                with ui.card().classes("p-5 card-shadow flex flex-col gap-2"):
                    ui.label("Distribuição de Locais").classes("text-base font-bold text-slate-800")
                    allocated = max(total_interns - no_venue_count, 0)

                    donut_options = {
                        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
                        "legend": {"bottom": "0%", "left": "center"},
                        "color": ["#107C10", "#D13438"],
                        "series": [
                            {
                                "name": "Alocação",
                                "type": "pie",
                                "radius": ["45%", "70%"],
                                "avoidLabelOverlap": False,
                                "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
                                "label": {"show": True, "formatter": "{b}\n{d}%", "fontWeight": "bold"},
                                "data": [
                                    {"value": allocated, "name": "Alocados"},
                                    {"value": no_venue_count, "name": "Sem Local"},
                                ],
                            }
                        ],
                    }
                    ui.echart(donut_options).classes("w-full h-72")

                # Chart 2: Document Status (Bar Chart with filter)
                with ui.card().classes("p-5 card-shadow flex flex-col gap-2"):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Status Documental").classes("text-base font-bold text-slate-800")
                        doc_select = ui.select(
                            options=DOC_TYPES,
                            value=state["filter_doc"],
                        ).classes("w-48").props("dense outlined")

                        def on_doc_change(e):
                            state["filter_doc"] = e.value
                            refresh_all()

                        doc_select.on_value_change(on_doc_change)

                    # Calculate ok vs pending
                    filter_name = state["filter_doc"]
                    ok_count = 0
                    pending_count = 0

                    if filter_name == "Todos":
                        for i in active_interns:
                            docs = container.document_service.get_by_intern_id(i.intern_id)
                            if not docs or any((d.status or "").lower() != "aprovado" for d in docs):
                                pending_count += 1
                            else:
                                ok_count += 1
                    else:
                        for i in active_interns:
                            docs = container.document_service.get_by_intern_id(i.intern_id)
                            target_docs = [d for d in docs if filter_name.lower() in (d.document_name or "").lower()]
                            if not target_docs or not any((d.status or "").lower() == "aprovado" for d in target_docs):
                                pending_count += 1
                            else:
                                ok_count += 1

                    bar_options = {
                        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                        "xAxis": {"type": "value"},
                        "yAxis": {"type": "category", "data": ["Reprovado / Pendente", "Aprovado"]},
                        "series": [
                            {
                                "type": "bar",
                                "data": [
                                    {"value": pending_count, "itemStyle": {"color": "#FFC107"}},
                                    {"value": ok_count, "itemStyle": {"color": "#107C10"}},
                                ],
                                "label": {"show": True, "position": "right", "fontWeight": "bold"},
                            }
                        ],
                    }
                    ui.echart(bar_options).classes("w-full h-72")

        refresh_btn.on("click", refresh_all)
        refresh_all()
