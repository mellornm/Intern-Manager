"""
Intern Add/Edit Dialog using NiceGUI.
"""

from datetime import date, datetime
from typing import Callable, Optional
from nicegui import ui

from core.models.intern import Intern
from services.intern_service import InternService
from services.venue_service import VenueService
from utils.validations import validate_date_range


def open_intern_dialog(
    intern_service: InternService,
    venue_service: VenueService,
    intern: Optional[Intern] = None,
    on_success: Optional[Callable] = None,
):
    """Opens dialog to create or edit an intern."""
    is_edit = intern is not None
    dialog_title = "Editar Aluno" if is_edit else "Novo Aluno"

    venues = venue_service.get_all()
    venue_options = {v.venue_id: v.venue_name for v in venues if v.venue_id is not None}
    venue_options[0] = "Nenhum (Sem Local)"

    terms = [f"{y}/{s}" for y in range(2025, 2031) for s in (1, 2)]

    # Initial values
    init_name = intern.name if is_edit else ""
    init_ra = intern.registration_number if is_edit else ""
    init_email = intern.email if is_edit else ""
    init_phone = intern.phone if is_edit else ""
    init_venue_id = intern.venue_id if (is_edit and intern.venue_id) else 0
    init_term = intern.term if (is_edit and intern.term in terms) else terms[0]
    init_hours = intern.working_hours if is_edit else ""
    init_days = intern.working_days if is_edit else ""
    init_active = intern.is_active if is_edit else True

    init_start = str(intern.start_date) if (is_edit and intern.start_date) else date.today().isoformat()
    init_end = str(intern.end_date) if (is_edit and intern.end_date) else date.today().replace(month=min(date.today().month + 6, 12)).isoformat()

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("school", color="primary", size="md")
                ui.label(dialog_title).classes("text-xl font-bold text-slate-800")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        with ui.column().classes("w-full gap-4 pt-2"):
            with ui.grid(columns=2).classes("w-full gap-4"):
                name_input = ui.input("Nome Completo *", value=init_name).classes("w-full")
                ra_input = ui.input("RA (Matrícula) *", value=init_ra).classes("w-full")

                email_input = ui.input("E-mail", value=init_email).classes("w-full")
                phone_input = ui.input("WhatsApp / Telefone", value=init_phone, placeholder="Ex: 11999998888").classes("w-full")

            with ui.grid(columns=2).classes("w-full gap-4"):
                venue_select = ui.select(
                    label="Local de Estágio",
                    options=venue_options,
                    value=init_venue_id,
                ).classes("w-full")

                term_select = ui.select(
                    label="Semestre",
                    options=terms,
                    value=init_term,
                ).classes("w-full")

            with ui.grid(columns=2).classes("w-full gap-4"):
                hours_input = ui.input("Horário de Estágio", value=init_hours, placeholder="Ex: 08:00 - 14:00").classes("w-full")
                days_input = ui.input("Dias da Semana", value=init_days, placeholder="Ex: Seg a Sex").classes("w-full")

            with ui.grid(columns=2).classes("w-full gap-4"):
                start_input = ui.input("Data de Início", value=init_start).classes("w-full")
                with start_input.add_slot("append"):
                    ui.icon("event").classes("cursor-pointer")
                    with ui.menu():
                        ui.date().bind_value(start_input)

                end_input = ui.input("Data de Término", value=init_end).classes("w-full")
                with end_input.add_slot("append"):
                    ui.icon("event").classes("cursor-pointer")
                    with ui.menu():
                        ui.date().bind_value(end_input)

            active_switch = ui.switch("Estágio Ativo", value=init_active).classes("mt-1")

        def handle_save():
            name = (name_input.value or "").strip()
            ra = (ra_input.value or "").strip()

            if not name:
                ui.notify("O nome completo é obrigatório.", color="negative")
                return
            if not ra:
                ui.notify("O RA (matrícula) é obrigatório.", color="negative")
                return

            try:
                dt_start = datetime.strptime(start_input.value, "%Y-%m-%d").date() if start_input.value else None
                dt_end = datetime.strptime(end_input.value, "%Y-%m-%d").date() if end_input.value else None
            except Exception:
                ui.notify("Formato de data inválido. Use AAAA-MM-DD.", color="negative")
                return

            if dt_start and dt_end:
                try:
                    validate_date_range(dt_start.isoformat(), dt_end.isoformat())
                except ValueError as e:
                    ui.notify(str(e), color="negative")
                    return

            chosen_venue_id = venue_select.value if venue_select.value != 0 else None

            if is_edit and intern:
                intern.name = name
                intern.registration_number = ra
                intern.email = email_input.value or ""
                intern.phone = phone_input.value or ""
                intern.venue_id = chosen_venue_id
                intern.term = term_select.value or ""
                intern.working_hours = hours_input.value or ""
                intern.working_days = days_input.value or ""
                intern.start_date = dt_start.isoformat() if dt_start else None
                intern.end_date = dt_end.isoformat() if dt_end else None
                intern.is_active = active_switch.value

                try:
                    success = intern_service.update_intern(intern)
                    if success:
                        ui.notify("Aluno atualizado com sucesso!", color="positive")
                        dialog.close()
                        if on_success:
                            on_success()
                    else:
                        ui.notify("Falha ao atualizar aluno.", color="negative")
                except Exception as e:
                    ui.notify(f"Erro ao atualizar: {e}", color="negative")
            else:
                new_intern = Intern(
                    name=name,
                    registration_number=ra,
                    email=email_input.value or "",
                    phone=phone_input.value or "",
                    venue_id=chosen_venue_id,
                    term=term_select.value or "",
                    working_hours=hours_input.value or "",
                    working_days=days_input.value or "",
                    start_date=dt_start.isoformat() if dt_start else None,
                    end_date=dt_end.isoformat() if dt_end else None,
                    is_active=active_switch.value,
                )
                try:
                    intern_service.add_new_intern(new_intern)
                    ui.notify(f"Aluno {name} cadastrado com sucesso!", color="positive")
                    dialog.close()
                    if on_success:
                        on_success()
                except Exception as e:
                    ui.notify(f"Erro ao salvar: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-3 pt-4 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Salvar Aluno", icon="check", on_click=handle_save).props("color=primary")

    dialog.open()
