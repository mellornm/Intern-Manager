"""
Pedagogical and Supervision Observations Dialog for NiceGUI.
"""

from datetime import date
from typing import Callable, Optional
from nicegui import ui

from core.models.intern import Intern
from core.models.observation import Observation
from services.observation_service import ObservationService


def open_observation_dialog(
    intern: Intern,
    service: ObservationService,
    on_close: Optional[Callable] = None,
):
    """Opens modal to manage pedagogical observations for an intern."""
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("notes", color="primary", size="md")
                with ui.column().classes("gap-0"):
                    ui.label(f"Observações: {intern.name}").classes("text-xl font-bold text-slate-800")
                    ui.label("Anotações de acompanhamento pedagógico").classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        # Container for observation timeline
        timeline_container = ui.column().classes("w-full max-h-72 overflow-y-auto gap-2 py-2")

        def refresh_observations():
            timeline_container.clear()
            if not intern.intern_id:
                return

            obs_list = service.get_by_intern_id(intern.intern_id)

            with timeline_container:
                if not obs_list:
                    with ui.column().classes("w-full items-center py-6 gap-1"):
                        ui.icon("chat_bubble_outline", size="lg").classes("text-slate-300")
                        ui.label("Nenhuma observação registrada ainda.").classes("text-xs text-slate-500")
                    return

                for obs in reversed(obs_list):
                    date_display = obs.last_update[:10] if obs.last_update else "Data não inf."
                    with ui.card().classes("w-full p-3 bg-white border border-slate-200 gap-1"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.badge(date_display, color="blue-7").classes("text-xs font-semibold")
                            ui.button(
                                icon="delete",
                                on_click=lambda o_id=obs.observation_id: handle_delete_obs(o_id),
                            ).props("flat round dense size=xs color=negative").tooltip("Excluir Anotação")

                        ui.label(obs.observation).classes("text-sm text-slate-800 whitespace-pre-wrap pt-1")

        def handle_delete_obs(obs_id):
            if obs_id:
                service.delete_observation(obs_id)
                ui.notify("Observação excluída.", color="info")
                refresh_observations()

        # Add new observation form
        with ui.column().classes("w-full pt-3 border-t border-slate-200 gap-2"):
            ui.label("Adicionar Nova Anotação").classes("text-xs font-bold text-slate-700 uppercase tracking-wider")

            obs_input = ui.textarea(
                placeholder="Descreva o acompanhamento pedagógico, atitude, evolução ou ocorrência...",
            ).classes("w-full").props("outlined rows=2")

            def handle_add_obs():
                text = (obs_input.value or "").strip()
                if not text:
                    ui.notify("Digite o texto da observação.", color="warning")
                    return

                if not intern.intern_id:
                    return

                new_obs = Observation(
                    intern_id=intern.intern_id,
                    observation=text,
                )
                try:
                    service.add_new_observation(new_obs)
                    obs_input.value = ""
                    ui.notify("Observação registrada!", color="positive")
                    refresh_observations()
                except Exception as e:
                    ui.notify(f"Erro ao salvar: {e}", color="negative")

            with ui.row().classes("w-full justify-end"):
                ui.button("Registrar Observação", icon="send", on_click=handle_add_obs).props("color=primary size=sm")

        refresh_observations()

        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-200 mt-2"):
            ui.button("Fechar", on_click=dialog.close).props("flat color=grey")

    if on_close:
        dialog.on("hide", on_close)

    dialog.open()
