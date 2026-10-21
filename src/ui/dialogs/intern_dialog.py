"""
Intern Add/Edit Dialog using NiceGUI.
Refactored with sectioned academic layout, Quasar outlined/dense inputs,
prepend icons, input masks, and inline visual feedback.
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
    dialog_title = "Editar Cadastro do Estagiário" if is_edit else "Novo Cadastro de Estagiário"
    dialog_subtitle = (
        f"Atualizando dados acadêmicos e contratuais de {intern.name}"
        if is_edit and intern
        else "Preencha os dados de identificação, alocação e vigência do estágio."
    )

    venues = venue_service.get_all()
    venue_options = {0: "Não alocado (Definir posteriormente)"}
    venue_options.update({v.venue_id: v.venue_name for v in venues if v.venue_id is not None})

    terms = [f"{y}/{s}" for y in range(2025, 2031) for s in (1, 2)]

    # Initial values
    init_name = intern.name if is_edit and intern else ""
    init_ra = intern.registration_number if is_edit and intern else ""
    init_email = intern.email if is_edit and intern else ""
    init_phone = intern.phone if is_edit and intern else ""
    init_venue_id = intern.venue_id if (is_edit and intern and intern.venue_id) else 0
    init_term = intern.term if (is_edit and intern and intern.term in terms) else terms[0]
    init_hours = intern.working_hours if is_edit and intern else ""
    init_days = intern.working_days if is_edit and intern else ""
    init_active = intern.is_active if is_edit and intern else True

    init_start = (
        str(intern.start_date)
        if (is_edit and intern and intern.start_date)
        else date.today().isoformat()
    )
    init_end = (
        str(intern.end_date)
        if (is_edit and intern and intern.end_date)
        else date.today().replace(month=min(date.today().month + 6, 12)).isoformat()
    )

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-2xl p-0 rounded-2xl overflow-hidden shadow-2xl border border-slate-200"
    ):
        # Modal Header
        with ui.row().classes(
            "w-full px-6 py-4 bg-slate-50 border-b border-slate-200 items-center justify-between"
        ):
            with ui.row().classes("items-center gap-3"):
                ui.avatar(
                    "edit_note" if is_edit else "person_add",
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

        # Modal Body (Scrollable Sections)
        with ui.column().classes("w-full px-6 py-5 gap-5 max-h-[75vh] overflow-y-auto"):
            # SECTION 1: Identificação & Contato
            with ui.column().classes("w-full gap-3"):
                with ui.row().classes("items-center gap-1.5 text-xs font-bold text-blue-800 uppercase tracking-wider"):
                    ui.icon("badge", size="16px")
                    ui.label("1. Identificação e Contato")

                with ui.grid(columns=1).classes("w-full sm:grid-cols-12 gap-3"):
                    name_input = (
                        ui.input(
                            "Nome Completo do Discente *",
                            value=init_name,
                            placeholder="Ex: Ana Carolina Souza",
                        )
                        .classes("sm:col-span-8 w-full")
                        .props("outlined dense hide-bottom-space")
                    )
                    with name_input.add_slot("prepend"):
                        ui.icon("person", size="xs").classes("text-slate-400")

                    ra_input = (
                        ui.input(
                            "RA (Matrícula) *",
                            value=init_ra,
                            placeholder="Ex: 20261045",
                        )
                        .classes("sm:col-span-4 w-full")
                        .props("outlined dense hide-bottom-space")
                    )
                    with ra_input.add_slot("prepend"):
                        ui.icon("tag", size="xs").classes("text-slate-400")

                with ui.grid(columns=1).classes("w-full sm:grid-cols-12 gap-3"):
                    email_input = (
                        ui.input(
                            "E-mail Institucional / Pessoal",
                            value=init_email,
                            placeholder="aluno@universidade.edu.br",
                        )
                        .classes("sm:col-span-7 w-full")
                        .props("outlined dense hide-bottom-space type=email")
                    )
                    with email_input.add_slot("prepend"):
                        ui.icon("mail_outline", size="xs").classes("text-slate-400")

                    phone_input = (
                        ui.input(
                            "WhatsApp / Telefone",
                            value=init_phone,
                            placeholder="(11) 99999-8888",
                        )
                        .classes("sm:col-span-5 w-full")
                        .props('outlined dense hide-bottom-space mask="(##) #####-####" unmasked-value')
                    )
                    with phone_input.add_slot("prepend"):
                        ui.icon("phone", size="xs").classes("text-slate-400")

            ui.separator().classes("bg-slate-100")

            # SECTION 2: Alocação e Vínculo Acadêmico
            with ui.column().classes("w-full gap-3"):
                with ui.row().classes("items-center gap-1.5 text-xs font-bold text-blue-800 uppercase tracking-wider"):
                    ui.icon("domain", size="16px")
                    ui.label("2. Alocação e Vínculo Acadêmico")

                with ui.grid(columns=1).classes("w-full sm:grid-cols-12 gap-3"):
                    venue_select = (
                        ui.select(
                            label="Campo / Local de Estágio",
                            options=venue_options,
                            value=init_venue_id,
                        )
                        .classes("sm:col-span-8 w-full")
                        .props("outlined dense options-dense hide-bottom-space")
                    )
                    with venue_select.add_slot("prepend"):
                        ui.icon("place", size="xs").classes("text-slate-400")

                    term_select = (
                        ui.select(
                            label="Semestre Letivo *",
                            options=terms,
                            value=init_term,
                        )
                        .classes("sm:col-span-4 w-full")
                        .props("outlined dense options-dense hide-bottom-space")
                    )
                    with term_select.add_slot("prepend"):
                        ui.icon("school", size="xs").classes("text-slate-400")

            ui.separator().classes("bg-slate-100")

            # SECTION 3: Cronograma e Carga Horária
            with ui.column().classes("w-full gap-3"):
                with ui.row().classes("items-center gap-1.5 text-xs font-bold text-blue-800 uppercase tracking-wider"):
                    ui.icon("schedule", size="16px")
                    ui.label("3. Vigência e Escala de Estágio")

                with ui.grid(columns=1).classes("w-full sm:grid-cols-2 gap-3"):
                    start_input = (
                        ui.input("Data de Início *", value=init_start)
                        .classes("w-full")
                        .props("outlined dense hide-bottom-space")
                    )
                    with start_input.add_slot("prepend"):
                        ui.icon("flight_takeoff", size="xs").classes("text-slate-400")
                    with start_input.add_slot("append"):
                        ui.icon("event", size="xs").classes("cursor-pointer text-primary")
                        with ui.menu().props(" no-parent-event"):
                            ui.date().bind_value(start_input)

                    end_input = (
                        ui.input("Data de Término *", value=init_end)
                        .classes("w-full")
                        .props("outlined dense hide-bottom-space")
                    )
                    with end_input.add_slot("prepend"):
                        ui.icon("flight_land", size="xs").classes("text-slate-400")
                    with end_input.add_slot("append"):
                        ui.icon("event", size="xs").classes("cursor-pointer text-primary")
                        with ui.menu().props(" no-parent-event"):
                            ui.date().bind_value(end_input)

                with ui.grid(columns=1).classes("w-full sm:grid-cols-2 gap-3"):
                    days_input = (
                        ui.input(
                            "Dias da Semana",
                            value=init_days,
                            placeholder="Ex: Seg, Qua e Sex",
                        )
                        .classes("w-full")
                        .props("outlined dense hide-bottom-space")
                    )
                    with days_input.add_slot("prepend"):
                        ui.icon("date_range", size="xs").classes("text-slate-400")

                    hours_input = (
                        ui.input(
                            "Horário de Expediente",
                            value=init_hours,
                            placeholder="Ex: 08:00 às 14:00",
                        )
                        .classes("w-full")
                        .props("outlined dense hide-bottom-space")
                    )
                    with hours_input.add_slot("prepend"):
                        ui.icon("access_time", size="xs").classes("text-slate-400")

                # Status Card Switch
                with ui.row().classes(
                    "w-full p-3 rounded-xl bg-slate-50 border border-slate-200/80 items-center justify-between mt-1"
                ):
                    with ui.column().classes("gap-0"):
                        ui.label("Status do Estágio em Andamento").classes(
                            "text-xs font-bold text-slate-800"
                        )
                        ui.label(
                            "Desative caso o aluno já tenha concluído ou encerrado o contrato."
                        ).classes("text-[11px] text-slate-500")
                    active_switch = ui.switch(value=init_active).props("color=primary")

        def handle_save():
            name = (name_input.value or "").strip()
            ra = (ra_input.value or "").strip()

            if not name:
                name_input.props("error error-message='Informe o nome completo'")
                ui.notify("O nome completo é obrigatório.", color="negative")
                return
            name_input.props(remove="error")

            if not ra:
                ra_input.props("error error-message='Informe o RA'")
                ui.notify("O RA (matrícula) é obrigatório.", color="negative")
                return
            ra_input.props(remove="error")

            try:
                dt_start = (
                    datetime.strptime(start_input.value, "%Y-%m-%d").date()
                    if start_input.value
                    else None
                )
                dt_end = (
                    datetime.strptime(end_input.value, "%Y-%m-%d").date()
                    if end_input.value
                    else None
                )
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
                        ui.notify("Cadastro atualizado com sucesso!", color="positive")
                        dialog.close()
                        if on_success:
                            on_success()
                    else:
                        ui.notify("Falha ao atualizar estagiário.", color="negative")
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
                    ui.notify(f"Estagiário {name} cadastrado com sucesso!", color="positive")
                    dialog.close()
                    if on_success:
                        on_success()
                except Exception as e:
                    ui.notify(f"Erro ao salvar: {e}", color="negative")

        # Modal Footer
        with ui.row().classes(
            "w-full px-6 py-3.5 bg-slate-50 border-t border-slate-200 justify-end items-center gap-2"
        ):
            ui.button("Cancelar", on_click=dialog.close).props("flat no-caps color=grey-7")
            ui.button(
                "Salvar Alterações" if is_edit else "Cadastrar Estagiário",
                icon="check",
                on_click=handle_save,
            ).props("unelevated no-caps color=primary").classes("px-5 font-semibold")

    dialog.open()
