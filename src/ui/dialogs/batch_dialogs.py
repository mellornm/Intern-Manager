"""
Batch Operations Dialogs (Collective Document Approval & Group Supervision Meetings).
"""

from datetime import date
from typing import Callable, List, Optional
from nicegui import ui

from core.constants import DEFAULT_DOCUMENTS_LIST
from core.models.document import Document
from core.models.meeting import Meeting
from services.document_service import DocumentService
from services.intern_service import InternService
from services.meeting_service import MeetingService
from services.venue_service import VenueService


def open_batch_document_dialog(
    selected_intern_ids: List[int],
    document_service: DocumentService,
    on_success: Optional[Callable] = None,
):
    """Opens dialog to bulk-approve a specific document for selected interns."""
    if not selected_intern_ids:
        ui.notify("Selecione ao menos um aluno na tabela para aprovação coletiva.", color="warning")
        return

    count = len(selected_intern_ids)

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-md p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("done_all", color="primary", size="md")
                ui.label("Aprovação em Lote").classes("text-xl font-bold text-slate-800")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        with ui.column().classes("w-full gap-3 pt-2"):
            ui.label(f"Você está aprovando documento para {count} alunos selecionados.").classes("text-sm text-slate-600 font-medium")

            doc_select = ui.select(
                label="Selecione o Documento a Aprovar",
                options=DEFAULT_DOCUMENTS_LIST,
                value=DEFAULT_DOCUMENTS_LIST[0],
            ).classes("w-full")

        def handle_bulk_approve():
            doc_name = doc_select.value
            try:
                for intern_id in selected_intern_ids:
                    docs = document_service.get_by_intern_id(intern_id)
                    matched_doc = next((d for d in docs if d.document_name == doc_name), None)

                    if matched_doc and matched_doc.document_id:
                        matched_doc.status = "Aprovado"
                        matched_doc.feedback = "Aprovado em lote via painel de coordenação."
                        document_service.update_document(matched_doc)
                    else:
                        # Create and approve
                        new_doc = Document(
                            intern_id=intern_id,
                            document_name=doc_name,
                            status="Aprovado",
                            feedback="Aprovado em lote via painel de coordenação.",
                        )
                        document_service.add_new_document(new_doc)

                ui.notify(f"Documento '{doc_name}' aprovado para {count} alunos!", color="positive")
                dialog.close()
                if on_success:
                    on_success()
            except Exception as e:
                ui.notify(f"Erro na aprovação em lote: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-2 pt-4 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Aprovar Todos", icon="check_circle", on_click=handle_bulk_approve).props("color=primary")

    dialog.open()


def open_batch_meeting_dialog(
    intern_service: InternService,
    meeting_service: MeetingService,
    venue_service: VenueService,
    on_success: Optional[Callable] = None,
):
    """Opens modal to schedule a collective meeting for interns of a venue or all interns."""
    venues = venue_service.get_all()
    venue_options = {0: "Todos os Locais de Estágio"}
    venue_options.update({v.venue_id: v.venue_name for v in venues if v.venue_id is not None})

    all_interns = intern_service.get_all_interns()

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("groups", color="primary", size="md")
                ui.label("Reunião Coletiva de Supervisão").classes("text-xl font-bold text-slate-800")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        with ui.column().classes("w-full gap-3 pt-2"):
            with ui.grid(columns=2).classes("w-full gap-3"):
                venue_filter = ui.select(
                    label="Filtrar por Local",
                    options=venue_options,
                    value=0,
                ).classes("w-full")

                date_input = ui.input("Data do Encontro", value=date.today().isoformat()).classes("w-full")
                with date_input.add_slot("append"):
                    ui.icon("event").classes("cursor-pointer")
                    with ui.menu():
                        ui.date().bind_value(date_input)

            topic_input = ui.input(
                label="Pauta do Encontro Coletivo",
                placeholder="Ex: Alinhamento das Diretrizes Curriculares e Ética",
            ).classes("w-full")

            presence_chk = ui.checkbox("Registrar como Presente para Todos", value=True).classes("text-sm")

            ui.label("Selecione os Participantes:").classes("text-xs font-bold text-slate-700 uppercase mt-1")

            intern_list_container = ui.column().classes("w-full max-h-48 overflow-y-auto border border-slate-200 rounded p-2 gap-1")

            checkboxes = {}

            def update_intern_checkboxes():
                intern_list_container.clear()
                checkboxes.clear()
                v_id = venue_filter.value

                filtered = [
                    i for i in all_interns
                    if (v_id == 0 or i.venue_id == v_id) and i.is_active
                ]

                with intern_list_container:
                    if not filtered:
                        ui.label("Nenhum aluno ativo encontrado para o filtro.").classes("text-xs text-slate-400 p-2")
                        return

                    for intern in filtered:
                        chk = ui.checkbox(
                            f"{intern.name} (RA: {intern.registration_number or 'S/N'})",
                            value=True,
                        ).classes("text-sm")
                        checkboxes[intern.intern_id] = chk

            venue_filter.on_value_change(lambda _: update_intern_checkboxes())
            update_intern_checkboxes()

        def handle_save_batch_meeting():
            topic = (topic_input.value or "").strip()
            if not topic:
                ui.notify("Informe a pauta da reunião coletiva.", color="warning")
                return

            participating_ids = [i_id for i_id, chk in checkboxes.items() if chk.value]
            if not participating_ids:
                ui.notify("Selecione ao menos um aluno participante.", color="warning")
                return

            try:
                for intern_id in participating_ids:
                    m = Meeting(
                        intern_id=intern_id,
                        meeting_date=date_input.value,
                        meeting_topic=topic,
                        is_intern_present=bool(presence_chk.value),
                    )
                    meeting_service.add_new_meeting(m)

                ui.notify(f"Reunião coletiva agendada para {len(participating_ids)} alunos!", color="positive")
                dialog.close()
                if on_success:
                    on_success()
            except Exception as e:
                ui.notify(f"Erro ao agendar reunião coletiva: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-2 pt-4 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Agendar para Selecionados", icon="check", on_click=handle_save_batch_meeting).props("color=primary")

    dialog.open()
