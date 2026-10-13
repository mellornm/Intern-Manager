"""
Venue Add/Edit Dialog for NiceGUI.
"""

from typing import Callable, Optional
from nicegui import ui

from core.models.venue import Venue
from services.venue_service import VenueService


def open_venue_dialog(
    venue_service: VenueService,
    venue: Optional[Venue] = None,
    on_success: Optional[Callable] = None,
):
    """Opens modal to add or edit an internship venue."""
    is_edit = venue is not None
    dialog_title = "Editar Local de Estágio" if is_edit else "Novo Local de Estágio"

    init_name = venue.venue_name if is_edit else ""
    init_address = venue.address if is_edit else ""
    init_supervisor = venue.supervisor_name if is_edit else ""
    init_phone = venue.supervisor_phone if is_edit else ""
    init_email = venue.supervisor_email if is_edit else ""

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("location_on", color="primary", size="md")
                ui.label(dialog_title).classes("text-xl font-bold text-slate-800")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        with ui.column().classes("w-full gap-3 pt-2"):
            name_input = ui.input("Nome da Instituição / Empresa *", value=init_name).classes("w-full")
            address_input = ui.input("Endereço Completo", value=init_address).classes("w-full")

            supervisor_input = ui.input("Supervisor / Responsável", value=init_supervisor).classes("w-full")

            with ui.grid(columns=2).classes("w-full gap-3"):
                phone_input = ui.input("Telefone do Supervisor", value=init_phone, placeholder="Ex: 11999998888").classes("w-full")
                email_input = ui.input("E-mail do Supervisor", value=init_email).classes("w-full")

        def handle_save():
            name = (name_input.value or "").strip()
            if not name:
                ui.notify("O nome do local é obrigatório.", color="negative")
                return

            if is_edit and venue:
                venue.venue_name = name
                venue.address = address_input.value or ""
                venue.supervisor_name = supervisor_input.value or ""
                venue.supervisor_phone = phone_input.value or ""
                venue.supervisor_email = email_input.value or ""

                try:
                    venue_service.update_venue(venue)
                    ui.notify("Local de estágio atualizado com sucesso!", color="positive")
                    dialog.close()
                    if on_success:
                        on_success()
                except Exception as e:
                    ui.notify(f"Erro ao atualizar: {e}", color="negative")
            else:
                new_venue = Venue(
                    venue_name=name,
                    address=address_input.value or "",
                    supervisor_name=supervisor_input.value or "",
                    supervisor_phone=phone_input.value or "",
                    supervisor_email=email_input.value or "",
                )
                try:
                    venue_service.add_new_venue(new_venue)
                    ui.notify(f"Local '{name}' cadastrado com sucesso!", color="positive")
                    dialog.close()
                    if on_success:
                        on_success()
                except Exception as e:
                    ui.notify(f"Erro ao salvar local: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-2 pt-4 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Salvar Local", icon="check", on_click=handle_save).props("color=primary")

    dialog.open()
