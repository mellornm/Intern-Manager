"""
Supervision Calendar Page for NiceGUI.
Responsive monthly calendar and daily event details for PC, Tablet, and Mobile.
"""

import calendar
from datetime import date
from typing import Dict, List
from nicegui import ui

from core.models.meeting import Meeting
from core.models.visit import Visit
from ui.context import ServiceContainer
from ui.layout import page_layout

MONTH_NAMES_PT = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
WEEKDAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def render_calendar_page(container: ServiceContainer):
    """Renders the interactive monthly calendar with meetings and visits."""
    with page_layout(title="Calendário de Supervisão", active_path="/calendar"):
        today = date.today()

        state = {
            "year": today.year,
            "month": today.month,
            "selected_date": today.isoformat(),
        }

        # Header with navigation
        with ui.row().classes("w-full justify-between items-start sm:items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0.5"):
                ui.label("Calendário de Supervisão").classes(
                    "text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Acompanhamento cronológico de reuniões de supervisão e visitas técnicas in loco."
                ).classes("text-xs sm:text-sm text-slate-500")

            with ui.row().classes(
                "items-center gap-1.5 bg-white px-2 py-1 rounded-xl border border-slate-200/80 shadow-xs w-full sm:w-auto justify-between sm:justify-end"
            ):
                prev_btn = ui.button(icon="chevron_left").props(
                    "flat round dense color=primary size=sm"
                )
                month_label = ui.label("").classes(
                    "text-sm sm:text-base font-bold text-slate-800 min-w-36 text-center"
                )
                next_btn = ui.button(icon="chevron_right").props(
                    "flat round dense color=primary size=sm"
                )
                today_btn = (
                    ui.button("Hoje", icon="today")
                    .props("unelevated no-caps color=blue-1 text-color=blue-9 size=sm")
                    .classes("px-2.5 font-semibold")
                )

        # Main Layout: Calendar Grid (Left) + Details Card (Right)
        with ui.grid(columns=1).classes("w-full lg:grid-cols-3 gap-4 sm:gap-6"):
            calendar_card = ui.card().classes(
                "w-full lg:col-span-2 p-3 sm:p-5 bg-white border border-slate-200/80 rounded-xl shadow-xs flex flex-col gap-3"
            )
            details_card = ui.card().classes(
                "w-full p-4 sm:p-5 bg-white border border-slate-200/80 rounded-xl shadow-xs flex flex-col gap-3"
            )

        def refresh_calendar():
            y = state["year"]
            m = state["month"]
            month_label.set_text(f"{MONTH_NAMES_PT[m]} {y}")

            meetings_list: List[Meeting] = container.meeting_service.get_calendar_events(m, y)
            visits_list: List[Visit] = container.visit_service.get_calendar_events(m, y)

            events_by_date: Dict[str, Dict[str, List]] = {}

            for meeting in meetings_list:
                d_str = meeting.meeting_date
                if d_str:
                    events_by_date.setdefault(d_str, {"meetings": [], "visits": []})[
                        "meetings"
                    ].append(meeting)

            for visit in visits_list:
                d_str = visit.visit_date
                if d_str:
                    events_by_date.setdefault(d_str, {"meetings": [], "visits": []})[
                        "visits"
                    ].append(visit)

            # 1. Render Calendar Grid
            calendar_card.clear()
            with calendar_card:
                with ui.row().classes(
                    "w-full items-center justify-between text-xs pb-2 border-b border-slate-100 flex-wrap gap-2"
                ):
                    with ui.row().classes("items-center gap-3 sm:gap-4 flex-wrap"):
                        with ui.row().classes("items-center gap-1.5"):
                            ui.element("span").classes("w-2.5 h-2.5 rounded-full bg-blue-600")
                            ui.label("Reunião").classes("text-slate-600 font-medium")
                        with ui.row().classes("items-center gap-1.5"):
                            ui.element("span").classes("w-2.5 h-2.5 rounded-full bg-emerald-600")
                            ui.label("Visita Técnica").classes("text-slate-600 font-medium")
                        with ui.row().classes("items-center gap-1.5"):
                            ui.element("span").classes("w-2.5 h-2.5 rounded-full bg-amber-500")
                            ui.label("Ambos").classes("text-slate-600 font-medium")

                with ui.grid(columns=7).classes(
                    "w-full text-center font-bold text-[11px] sm:text-xs text-slate-400 uppercase"
                ):
                    for wday in WEEKDAYS_PT:
                        ui.label(wday).classes("py-1")

                cal = calendar.Calendar(firstweekday=0)
                month_days = cal.monthdatescalendar(y, m)

                with ui.grid(columns=7).classes("w-full gap-1 sm:gap-1.5"):
                    for week in month_days:
                        for day_date in week:
                            day_iso = day_date.isoformat()
                            is_curr_month = day_date.month == m
                            is_selected = day_iso == state["selected_date"]
                            is_today = day_iso == today.isoformat()

                            day_events = events_by_date.get(
                                day_iso, {"meetings": [], "visits": []}
                            )
                            has_meetings = bool(day_events["meetings"])
                            has_visits = bool(day_events["visits"])

                            base_classes = "p-1.5 sm:p-2 min-h-14 sm:min-h-20 rounded-lg cursor-pointer flex flex-col justify-between transition-all shadow-none "
                            if is_selected:
                                card_classes = (
                                    base_classes
                                    + "bg-blue-50/80 border-2 border-blue-600"
                                )
                            elif not is_curr_month:
                                card_classes = (
                                    base_classes
                                    + "bg-slate-50/60 text-slate-300 border border-transparent"
                                )
                            else:
                                card_classes = (
                                    base_classes
                                    + "bg-white hover:bg-slate-50 border border-slate-200/80"
                                )

                            with ui.card().classes(card_classes) as day_card:
                                def select_day(d=day_iso):
                                    state["selected_date"] = d
                                    refresh_calendar()

                                day_card.on("click", select_day)

                                with ui.row().classes("w-full justify-between items-center"):
                                    lbl_day = ui.label(str(day_date.day)).classes(
                                        "text-[11px] sm:text-xs font-bold"
                                    )
                                    if is_today:
                                        lbl_day.classes(
                                            "text-white bg-blue-600 rounded-full px-1.5 py-0.5"
                                        )

                                with ui.row().classes(
                                    "w-full gap-1 flex-wrap items-center justify-center sm:justify-start mt-1"
                                ):
                                    if has_meetings and has_visits:
                                        ui.badge(
                                            f"{len(day_events['meetings']) + len(day_events['visits'])}",
                                            color="amber-8",
                                        ).classes("text-[10px] px-1.5 py-0.5 font-bold")
                                    elif has_meetings:
                                        ui.badge(
                                            f"{len(day_events['meetings'])}",
                                            color="blue-7",
                                        ).classes("text-[10px] px-1.5 py-0.5 font-bold")
                                    elif has_visits:
                                        ui.badge(
                                            f"{len(day_events['visits'])}",
                                            color="green-7",
                                        ).classes("text-[10px] px-1.5 py-0.5 font-bold")

            render_day_details(
                events_by_date.get(state["selected_date"], {"meetings": [], "visits": []})
            )

        def render_day_details(day_events):
            details_card.clear()
            sel_date_str = state["selected_date"]
            try:
                dt_obj = date.fromisoformat(sel_date_str)
                formatted_date = dt_obj.strftime("%d/%m/%Y")
            except Exception:
                formatted_date = sel_date_str

            with details_card:
                with ui.row().classes(
                    "w-full justify-between items-center pb-2.5 border-b border-slate-100"
                ):
                    with ui.row().classes("items-center gap-2"):
                        ui.avatar("event_note", color="blue-1", text_color="primary", size="sm")
                        with ui.column().classes("gap-0"):
                            ui.label(f"Agenda de {formatted_date}").classes(
                                "font-bold text-slate-900 text-sm"
                            )
                            ui.label("Eventos registrados no dia").classes(
                                "text-[11px] text-slate-400"
                            )

                meetings = day_events.get("meetings", [])
                visits = day_events.get("visits", [])

                if not meetings and not visits:
                    with ui.column().classes(
                        "w-full items-center py-12 gap-2 text-slate-400"
                    ):
                        ui.icon("event_busy", size="xl").classes("text-slate-300")
                        ui.label("Nenhum evento agendado para esta data.").classes(
                            "text-xs text-center"
                        )
                    return

                with ui.column().classes("w-full gap-3 max-h-96 overflow-y-auto pr-1"):
                    if meetings:
                        ui.label("REUNIÕES DE SUPERVISÃO").classes(
                            "text-[11px] font-bold text-blue-700 tracking-wider mt-1"
                        )
                        for m in meetings:
                            intern = container.intern_service.get_by_id(m.intern_id)
                            intern_name = (
                                intern.name if intern else f"Aluno ID {m.intern_id}"
                            )
                            status_txt = "Presente" if m.is_intern_present else "Ausente"
                            status_col = "green-1" if m.is_intern_present else "red-1"
                            status_txt_col = "green-9" if m.is_intern_present else "red-9"

                            with ui.card().classes(
                                "w-full p-3 bg-blue-50/40 border border-blue-200/70 rounded-xl shadow-none gap-1"
                            ):
                                with ui.row().classes("w-full justify-between items-center"):
                                    ui.label(intern_name).classes(
                                        "font-bold text-xs text-slate-900 truncate"
                                    )
                                    ui.badge(
                                        status_txt,
                                        color=status_col,
                                        text_color=status_txt_col,
                                    ).classes("text-[10px] font-bold px-1.5 py-0.5 rounded")

                                if m.meeting_topic:
                                    ui.label(m.meeting_topic).classes(
                                        "text-xs text-slate-600"
                                    )

                    if visits:
                        ui.label("VISITAS TÉCNICAS").classes(
                            "text-[11px] font-bold text-emerald-700 tracking-wider mt-2"
                        )
                        for v in visits:
                            intern = container.intern_service.get_by_id(v.intern_id)
                            intern_name = (
                                intern.name if intern else f"Aluno ID {v.intern_id}"
                            )
                            venue = (
                                container.venue_service.get_by_id(v.venue_id)
                                if v.venue_id
                                else None
                            )
                            venue_name = (
                                venue.venue_name if venue else "Local Não Informado"
                            )

                            with ui.card().classes(
                                "w-full p-3 bg-emerald-50/40 border border-emerald-200/70 rounded-xl shadow-none gap-1"
                            ):
                                with ui.row().classes(
                                    "w-full justify-between items-center gap-2 flex-wrap"
                                ):
                                    ui.label(intern_name).classes(
                                        "font-bold text-xs text-slate-900"
                                    )
                                    with ui.row().classes(
                                        "items-center gap-1 text-xs text-emerald-800 font-semibold"
                                    ):
                                        ui.icon("place", size="13px")
                                        ui.label(venue_name).classes("truncate max-w-40")

                                if v.observation:
                                    ui.label(v.observation).classes(
                                        "text-xs text-slate-600"
                                    )

        def go_prev_month():
            if state["month"] == 1:
                state["month"] = 12
                state["year"] -= 1
            else:
                state["month"] -= 1
            state["selected_date"] = date(state["year"], state["month"], 1).isoformat()
            refresh_calendar()

        def go_next_month():
            if state["month"] == 12:
                state["month"] = 1
                state["year"] += 1
            else:
                state["month"] += 1
            state["selected_date"] = date(state["year"], state["month"], 1).isoformat()
            refresh_calendar()

        def go_today():
            state["year"] = today.year
            state["month"] = today.month
            state["selected_date"] = today.isoformat()
            refresh_calendar()

        prev_btn.on("click", go_prev_month)
        next_btn.on("click", go_next_month)
        today_btn.on("click", go_today)

        refresh_calendar()
