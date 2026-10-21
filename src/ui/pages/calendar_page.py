"""
Supervision Calendar Page for NiceGUI.
Pure dependency injection for calendar visualization of meetings and technical visits.
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
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]
WEEKDAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def render_calendar_page(container: ServiceContainer):
    """Renders the interactive monthly calendar with meetings and visits."""
    with page_layout(title="Calendário de Supervisão", active_path="/calendar"):
        today = date.today()

        # Session state for month and selected day
        state = {
            "year": today.year,
            "month": today.month,
            "selected_date": today.isoformat(),
        }

        # Header with navigation
        with ui.row().classes("w-full justify-between items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0"):
                ui.label("Calendário de Supervisão").classes("text-2xl sm:text-3xl font-extrabold text-slate-900")
                ui.label("Acompanhamento cronológico de reuniões e visitas técnicas in loco.").classes("text-sm text-slate-500")

            with ui.row().classes("items-center gap-2"):
                prev_btn = ui.button(icon="chevron_left").props("flat round color=primary")
                month_label = ui.label("").classes("text-lg font-bold text-slate-800 min-w-36 text-center")
                next_btn = ui.button(icon="chevron_right").props("flat round color=primary")
                today_btn = ui.button("Mês Atual", icon="today").props("outline color=primary size=sm")

        # Main Layout: Calendar Grid (Left) + Details Card (Right)
        with ui.grid(columns=1).classes("w-full lg:grid-cols-3 gap-6"):
            # Calendar Card (Span 2 cols on lg)
            calendar_card = ui.card().classes("w-full lg:col-span-2 p-5 card-shadow flex flex-col gap-4")

            # Day Details Card (Span 1 col on lg)
            details_card = ui.card().classes("w-full p-5 card-shadow flex flex-col gap-3")

        def refresh_calendar():
            y = state["year"]
            m = state["month"]
            month_label.set_text(f"{MONTH_NAMES_PT[m]} {y}")

            # Fetch events for visible month via injected services (Pure DI)
            meetings_list: List[Meeting] = container.meeting_service.get_calendar_events(m, y)
            visits_list: List[Visit] = container.visit_service.get_calendar_events(m, y)

            # Map date string (YYYY-MM-DD) -> list of events
            events_by_date: Dict[str, Dict[str, List]] = {}

            for meeting in meetings_list:
                d_str = meeting.meeting_date
                if d_str:
                    events_by_date.setdefault(d_str, {"meetings": [], "visits": []})["meetings"].append(meeting)

            for visit in visits_list:
                d_str = visit.visit_date
                if d_str:
                    events_by_date.setdefault(d_str, {"meetings": [], "visits": []})["visits"].append(visit)

            # 1. Render Calendar Grid
            calendar_card.clear()
            with calendar_card:
                # Legend banner
                with ui.row().classes("w-full items-center justify-between text-xs pb-2 border-b border-slate-100"):
                    with ui.row().classes("items-center gap-4"):
                        with ui.row().classes("items-center gap-1.5"):
                            ui.avatar(size="xs").classes("bg-blue-600")
                            ui.label("Reunião")
                        with ui.row().classes("items-center gap-1.5"):
                            ui.avatar(size="xs").classes("bg-green-600")
                            ui.label("Visita Técnica")
                        with ui.row().classes("items-center gap-1.5"):
                            ui.avatar(size="xs").classes("bg-amber-500")
                            ui.label("Ambos no Dia")

                # Weekday Headers
                with ui.grid(columns=7).classes("w-full text-center font-bold text-xs text-slate-500"):
                    for wday in WEEKDAYS_PT:
                        ui.label(wday).classes("py-1")

                # Month Days Grid
                cal = calendar.Calendar(firstweekday=0)  # Monday first
                month_days = cal.monthdatescalendar(y, m)

                with ui.grid(columns=7).classes("w-full gap-1"):
                    for week in month_days:
                        for day_date in week:
                            day_iso = day_date.isoformat()
                            is_curr_month = day_date.month == m
                            is_selected = day_iso == state["selected_date"]
                            is_today = day_iso == today.isoformat()

                            day_events = events_by_date.get(day_iso, {"meetings": [], "visits": []})
                            has_meetings = bool(day_events["meetings"])
                            has_visits = bool(day_events["visits"])

                            # Card classes
                            base_classes = "p-2 min-h-20 rounded-lg cursor-pointer flex flex-col justify-between transition-all "
                            if is_selected:
                                card_classes = base_classes + "bg-blue-50 border-2 border-blue-600 shadow-sm"
                            elif not is_curr_month:
                                card_classes = base_classes + "bg-slate-100/60 text-slate-400 border border-transparent"
                            else:
                                card_classes = base_classes + "bg-white hover:bg-slate-50 border border-slate-200"

                            with ui.card().classes(card_classes) as day_card:
                                def select_day(d=day_iso):
                                    state["selected_date"] = d
                                    refresh_calendar()

                                day_card.on("click", select_day)

                                # Top: Day Number
                                with ui.row().classes("w-full justify-between items-center"):
                                    lbl_day = ui.label(str(day_date.day)).classes("text-xs font-bold")
                                    if is_today:
                                        lbl_day.classes("text-blue-700 bg-blue-100 rounded-full px-1.5")

                                # Bottom: Badges
                                with ui.row().classes("w-full gap-1 flex-wrap items-center mt-1"):
                                    if has_meetings and has_visits:
                                        ui.badge(f"{len(day_events['meetings']) + len(day_events['visits'])} ev.", color="amber-8").classes("text-xxs px-1")
                                    elif has_meetings:
                                        ui.badge(f"{len(day_events['meetings'])} r.", color="blue-7").classes("text-xxs px-1")
                                    elif has_visits:
                                        ui.badge(f"{len(day_events['visits'])} v.", color="green-7").classes("text-xxs px-1")

            # 2. Render Day Details
            render_day_details(events_by_date.get(state["selected_date"], {"meetings": [], "visits": []}))

        def render_day_details(day_events):
            details_card.clear()
            sel_date_str = state["selected_date"]
            try:
                dt_obj = date.fromisoformat(sel_date_str)
                formatted_date = dt_obj.strftime("%d/%m/%Y")
            except Exception:
                formatted_date = sel_date_str

            with details_card:
                with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("event_note", color="primary", size="sm")
                        ui.label(f"Eventos em {formatted_date}").classes("font-bold text-slate-800 text-sm")

                meetings = day_events.get("meetings", [])
                visits = day_events.get("visits", [])

                if not meetings and not visits:
                    with ui.column().classes("w-full items-center py-12 gap-2 text-slate-400"):
                        ui.icon("event_busy", size="lg")
                        ui.label("Nenhum evento agendado para esta data.").classes("text-xs text-center")
                    return

                with ui.column().classes("w-full gap-3 max-h-96 overflow-y-auto"):
                    # Meetings
                    if meetings:
                        ui.label("REUNIÕES DE SUPERVISÃO").classes("text-xs font-bold text-blue-700 tracking-wider mt-1")
                        for m in meetings:
                            intern = container.intern_service.get_by_id(m.intern_id)
                            intern_name = intern.name if intern else f"Aluno ID {m.intern_id}"
                            status_txt = "Presente" if m.is_intern_present else "Ausente"
                            status_col = "green-7" if m.is_intern_present else "red-7"

                            with ui.card().classes("w-full p-3 bg-blue-50/50 border border-blue-200 gap-1"):
                                with ui.row().classes("w-full justify-between items-center"):
                                    ui.label(intern_name).classes("font-bold text-xs text-slate-900")
                                    ui.badge(status_txt, color=status_col).classes("text-xxs")

                                if m.meeting_topic:
                                    ui.label(m.meeting_topic).classes("text-xs text-slate-600")

                    # Visits
                    if visits:
                        ui.label("VISITAS TÉCNICAS").classes("text-xs font-bold text-green-700 tracking-wider mt-2")
                        for v in visits:
                            intern = container.intern_service.get_by_id(v.intern_id)
                            intern_name = intern.name if intern else f"Aluno ID {v.intern_id}"
                            venue = container.venue_service.get_by_id(v.venue_id) if v.venue_id else None
                            venue_name = venue.venue_name if venue else "Local Não Informado"

                            with ui.card().classes("w-full p-3 bg-green-50/50 border border-green-200 gap-1"):
                                with ui.row().classes("w-full justify-between items-center"):
                                    ui.label(intern_name).classes("font-bold text-xs text-slate-900")
                                    ui.label(f"📍 {venue_name}").classes("text-xs text-slate-700 font-semibold")

                                if v.observation:
                                    ui.label(v.observation).classes("text-xs text-slate-600")

        # Connect month navigation buttons
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
