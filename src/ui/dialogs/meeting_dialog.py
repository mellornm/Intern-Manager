"""
Supervision Meetings dialog for NiceGUI.
"""

from datetime import date
from typing import Callable, Optional
from nicegui import ui

from core.models.intern import Intern
from core.models.meeting import Meeting
from services.meeting_service import MeetingService


def open_meeting_dialog(
    intern: Intern,
    service: MeetingService,
    on_close: Optional[Callable] = None,
):
    """Opens modal to manage supervision meetings for an intern."""
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("event_available", color="primary", size="md")
                with ui.column().classes("gap-0"):
                    ui.label(f"Reuniões de Supervisão: {intern.name}").classes("text-xl font-bold text-slate-800")
                    ui.label("Histórico de encontros e presença").classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        # Container for meetings list
        list_container = ui.column().classes("w-full max-h-72 overflow-y-auto gap-2 py-2")

        def refresh_meetings():
            list_container.clear()
            if not intern.intern_id:
                return

            meetings = service.get_by_intern_id(intern.intern_id)

            with list_container:
                if not meetings:
                    with ui.column().classes("w-full items-center py-6 gap-1"):
                        ui.icon("calendar_today", size="lg").classes("text-slate-300")
                        ui.label("Nenhuma reunião de supervisão registrada.").classes("text-xs text-slate-500")
                    return

                for m in reversed(meetings):
                    presence_color = "green-7" if m.presence else "red-7"
                    presence_text = "Presente" if m.presence else "Ausente"

                    with ui.card().classes("w-full p-3 bg-white border border-slate-200 gap-1"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.badge(m.meeting_date or "Sem data", color="blue-7").classes("text-xs font-semibold")
                                ui.badge(presence_text, color=presence_color).classes("text-xs font-semibold")

                            ui.button(
                                icon="delete",
                                on_click=lambda m_id=m.meeting_id: handle_delete_meeting(m_id),
                            ).props("flat round dense size=xs color=negative").tooltip("Excluir Reunião")

                        ui.label(m.topic or "Sem pauta informada").classes("text-sm text-slate-800 font-medium pt-1")

        def handle_delete_meeting(meeting_id):
            if meeting_id:
                service.delete(meeting_id)
                ui.notify("Reunião excluída.", color="info")
                refresh_meetings()

        # Add new meeting form
        with ui.column().classes("w-full pt-3 border-t border-slate-200 gap-2"):
            ui.label("Agendar / Registrar Reunião").classes("text-xs font-bold text-slate-700 uppercase tracking-wider")

            with ui.row().classes("w-full gap-3 items-center"):
                date_input = ui.input("Data", value=date.today().isoformat()).classes("w-40").props("dense outlined")
                with date_input.add_slot("append"):
                    ui.icon("event").classes("cursor-pointer")
                    with ui.menu():
                        ui.date().bind_value(date_input)

                presence_chk = ui.checkbox("Aluno Presente", value=True).classes("text-sm")

            topic_input = ui.input(
                label="Pauta / Conteúdo Discutido",
                placeholder="Ex: Discussão de caso clínico e alinhamento do projeto",
            ).classes("w-full").props("outlined dense")

            def handle_add_meeting():
                topic = (topic_input.value or "").strip()
                if not topic:
                    ui.notify("Informe o tópico da reunião.", color="warning")
                    return

                if not intern.intern_id:
                    return

                new_meeting = Meeting(
                    intern_id=intern.intern_id,
                    meeting_date=date_input.value,
                    topic=topic,
                    presence=presence_chk.value,
                )
                try:
                    service.add_new_meeting(new_meeting)
                    topic_input.value = ""
                    ui.notify("Reunião registrada com sucesso!", color="positive")
                    refresh_meetings()
                except Exception as e:
                    ui.notify(f"Erro ao agendar reunião: {e}", color="negative")

            with ui.row().classes("w-full justify-end"):
                ui.button("Registrar Reunião", icon="add", on_click=handle_add_meeting).props("color=primary size=sm")

        refresh_meetings()

        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-200 mt-2"):
            ui.button("Fechar", on_click=dialog.close).props("flat color=grey")

    if on_close:
        dialog.on("hide", on_close)

    dialog.open()
