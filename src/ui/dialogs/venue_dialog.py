"""
Venue Add/Edit Dialog for NiceGUI.
Refactored with sectioned fields, Quasar outlined/dense inputs, prepend icons, and phone mask.
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
    dialog_subtitle = (
        f"Atualizando dados de {venue.venue_name}"
        if is_edit and venue
        else "Cadastre a instituição concedente e o preceptor responsável."
    )

    init_name = venue.venue_name if is_edit and venue else ""
    init_address = venue.address if is_edit and venue else ""
    init_supervisor = venue.supervisor_name if is_edit and venue else ""
    init_phone = venue.supervisor_phone if is_edit and venue else ""
    init_email = venue.supervisor_email if is_edit and venue else ""

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-lg p-0 rounded-2xl overflow-hidden shadow-2xl border border-slate-200"
    ):
        # Modal Header
        with ui.row().classes(
            "w-full px-6 py-4 bg-slate-50 border-b border-slate-200 items-center justify-between"
        ):
            with ui.row().classes("items-center gap-3"):
                ui.avatar(
                    "domain",
                    color="blue-1",
                    text_color="primary",
                    size="md",
                )
                with ui.column().classes("gap-0"):
                    ui.label(dialog_title).classes("text-lg font-bold text-slate-900")
                    ui.label(dialog_subtitle).classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props(
                "flat round dense size=sm color=grey-7"
            )

        # Modal Body
        with ui.column().classes("w-full px-6 py-5 gap-4 max-h-[75vh] overflow-y-auto"):
            with ui.row().classes(
                "items-center gap-1.5 text-xs font-bold text-blue-800 uppercase tracking-wider"
            ):
                ui.icon("business", size="16px")
                ui.label("1. Dados da Instituição")

            name_input = (
                ui.input(
                    "Nome da Instituição / Clínica *",
                    value=init_name,
                    placeholder="Ex: Hospital São Lucas",
                )
                .classes("w-full")
                .props("outlined dense hide-bottom-space")
            )
            with name_input.add_slot("prepend"):
                ui.icon("domain", size="xs").classes("text-slate-400")

            address_input = (
                ui.input(
                    "Endereço Completo",
                    value=init_address,
                    placeholder="Rua, Número, Bairro, Cidade - UF",
                )
                .classes("w-full")
                .props("outlined dense hide-bottom-space")
            )
            with address_input.add_slot("prepend"):
                ui.icon("place", size="xs").classes("text-slate-400")

            ui.separator().classes("bg-slate-100 my-1")

            with ui.row().classes(
                "items-center gap-1.5 text-xs font-bold text-blue-800 uppercase tracking-wider"
            ):
                ui.icon("supervisor_account", size="16px")
                ui.label("2. Preceptor / Supervisor de Campo")

            supervisor_input = (
                ui.input(
                    "Nome do Supervisor Local *",
                    value=init_supervisor,
                    placeholder="Ex: Dr. Marcos Oliveira",
                )
                .classes("w-full")
                .props("outlined dense hide-bottom-space")
            )
            with supervisor_input.add_slot("prepend"):
                ui.icon("person", size="xs").classes("text-slate-400")

            with ui.grid(columns=1).classes("w-full sm:grid-cols-2 gap-3"):
                phone_input = (
                    ui.input(
                        "WhatsApp / Telefone",
                        value=init_phone,
                        placeholder="(11) 99999-8888",
                    )
                    .classes("w-full")
                    .props('outlined dense hide-bottom-space mask="(##) #####-####" unmasked-value')
                )
                with phone_input.add_slot("prepend"):
                    ui.icon("phone", size="xs").classes("text-slate-400")

                email_input = (
                    ui.input(
                        "E-mail do Supervisor",
                        value=init_email,
                        placeholder="supervisor@instituicao.com.br",
                    )
                    .classes("w-full")
                    .props("outlined dense hide-bottom-space type=email")
                )
                with email_input.add_slot("prepend"):
                    ui.icon("mail_outline", size="xs").classes("text-slate-400")

        def handle_save():
            name = (name_input.value or "").strip()
            supervisor = (supervisor_input.value or "").strip()

            if not name:
                name_input.props("error error-message='Informe o nome do local'")
                ui.notify("O nome do local é obrigatório.", color="negative")
                return
            name_input.props(remove="error")

            if not supervisor:
                supervisor_input.props("error error-message='Informe o supervisor'")
                ui.notify("O nome do supervisor é obrigatório.", color="negative")
                return
            supervisor_input.props(remove="error")

            if is_edit and venue:
                venue.venue_name = name
                venue.address = address_input.value or ""
                venue.supervisor_name = supervisor
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
                    supervisor_name=supervisor,
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

        # Modal Footer
        with ui.row().classes(
            "w-full px-6 py-3.5 bg-slate-50 border-t border-slate-200 justify-end items-center gap-2"
        ):
            ui.button("Cancelar", on_click=dialog.close).props("flat no-caps color=grey-7")
            ui.button("Salvar Local", icon="check", on_click=handle_save).props(
                "unelevated no-caps color=primary"
            ).classes("px-5 font-semibold")

    dialog.open()
