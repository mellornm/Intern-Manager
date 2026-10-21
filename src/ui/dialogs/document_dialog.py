"""
Document audit and management dialog for NiceGUI.
"""

from typing import Callable, Optional
from nicegui import ui

from core.models.document import Document
from core.models.intern import Intern
from services.document_service import DocumentService
from ui.components.status_badge import create_status_badge

STANDARD_FEEDBACKS = {
    "--- Selecione um motivo ---": "",
    "Assinatura Faltando": "Documento recusado. Motivo: Falta a assinatura do supervisor de campo ou do estagiário.",
    "Data Inválida": "Documento recusado. Motivo: As datas informadas não correspondem ao período do estágio cadastrado.",
    "Carimbo Ausente": "Documento recusado. Motivo: É obrigatório o carimbo e assinatura da instituição concedente.",
    "Documento Errado": "Documento recusado. Motivo: O arquivo enviado não corresponde ao modelo oficial da universidade.",
    "Rasuras": "Documento recusado. Motivo: O documento apresenta rasuras ou está ilegível.",
}


def open_document_dialog(
    intern: Intern,
    service: DocumentService,
    on_close: Optional[Callable] = None,
):
    """Opens modal to manage and audit documents for a given intern."""
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-4xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("folder_shared", color="primary", size="md")
                with ui.column().classes("gap-0"):
                    ui.label(f"Documentos: {intern.name}").classes("text-xl font-bold text-slate-800")
                    ui.label(f"RA: {intern.registration_number or 'N/A'}").classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        # Container for the document list table
        table_container = ui.column().classes("w-full gap-4 pt-2")

        def refresh_docs():
            table_container.clear()
            if not intern.intern_id:
                return

            docs = service.get_by_intern_id(intern.intern_id)

            with table_container:
                # Top Toolbar
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.row().classes("gap-2"):
                        ui.button(
                            "Gerar Kit Padrão",
                            icon="auto_fix_high",
                            on_click=lambda: handle_generate_defaults(),
                        ).props("outline color=primary size=sm")

                        ui.button(
                            "Adicionar Documento",
                            icon="add",
                            on_click=lambda: open_add_doc_dialog(),
                        ).props("flat color=primary size=sm")

                    ui.label(f"Total: {len(docs)} documentos").classes("text-xs text-slate-500")

                if not docs:
                    with ui.column().classes("w-full items-center py-8 gap-2"):
                        ui.icon("description", size="xl").classes("text-slate-300")
                        ui.label("Nenhum documento registrado para este aluno.").classes("text-slate-500")
                        ui.button("Gerar Kit Padrão", on_click=lambda: handle_generate_defaults()).props("color=primary size=sm")
                    return

                # Render documents list
                with ui.column().classes("w-full gap-2"):
                    for d in docs:
                        with ui.card().classes("w-full p-3 flex-row items-center justify-between border border-slate-200"):
                            with ui.row().classes("items-center gap-3"):
                                ui.icon("insert_drive_file", color="primary", size="sm")
                                with ui.column().classes("gap-0"):
                                    ui.label(d.document_name).classes("font-semibold text-slate-800 text-sm")
                                    if d.feedback:
                                        ui.label(f"Parecer: {d.feedback}").classes("text-xs text-red-600 font-medium")

                            with ui.row().classes("items-center gap-3"):
                                create_status_badge(d.status or "Pendente")
                                ui.button(
                                    "Auditar",
                                    icon="verified",
                                    on_click=lambda doc=d: open_audit_subdialog(doc),
                                ).props("flat size=sm color=primary")

                                ui.button(
                                    icon="delete",
                                    on_click=lambda doc_id=d.document_id: handle_delete_doc(doc_id),
                                ).props("flat round dense size=sm color=negative").tooltip("Excluir Documento")

        def handle_generate_defaults():
            if intern.intern_id:
                service.create_initial_documents_batch(intern.intern_id)
                ui.notify("Kit padrão de documentos gerado!", color="positive")
                refresh_docs()

        def handle_delete_doc(doc_id):
            if doc_id:
                service.delete_document(doc_id)
                ui.notify("Documento excluído.", color="info")
                refresh_docs()

        def open_add_doc_dialog():
            with ui.dialog() as add_dialog, ui.card().classes("p-5 dialog-card w-96"):
                ui.label("Novo Documento").classes("font-bold text-lg text-slate-800")
                name_input = ui.input("Nome do Documento", placeholder="Ex: Termo Aditivo").classes("w-full")

                def confirm_add():
                    val = (name_input.value or "").strip()
                    if not val:
                        ui.notify("Informe o nome do documento.", color="warning")
                        return
                    if intern.intern_id:
                        new_doc = Document(
                            intern_id=intern.intern_id,
                            document_name=val,
                            status="Pendente",
                        )
                        service.add_new_document(new_doc)
                        ui.notify("Documento adicionado!", color="positive")
                        add_dialog.close()
                        refresh_docs()

                with ui.row().classes("w-full justify-end gap-2 pt-3"):
                    ui.button("Cancelar", on_click=add_dialog.close).props("flat color=grey")
                    ui.button("Adicionar", on_click=confirm_add).props("color=primary")
            add_dialog.open()

        def open_audit_subdialog(doc):
            with ui.dialog() as audit_dialog, ui.card().classes("p-6 dialog-card w-full max-w-lg"):
                with ui.row().classes("w-full items-center justify-between pb-2 border-b border-slate-200"):
                    ui.label(f"Auditoria: {doc.document_name}").classes("font-bold text-slate-800 text-base")
                    ui.button(icon="close", on_click=audit_dialog.close).props("flat round dense size=sm")

                status_select = ui.select(
                    label="Decisão de Conformidade",
                    options=["Pendente", "Aprovado", "Reprovado"],
                    value=doc.status or "Pendente",
                ).classes("w-full")

                reason_select = ui.select(
                    label="Motivo da Recusa (Preenchimento Rápido)",
                    options=list(STANDARD_FEEDBACKS.keys()),
                    value="--- Selecione um motivo ---",
                ).classes("w-full")

                feedback_input = ui.textarea(
                    label="Parecer / Observações do Documento",
                    value=doc.feedback or "",
                ).classes("w-full")

                def on_reason_change(e):
                    text = STANDARD_FEEDBACKS.get(e.value, "")
                    if text:
                        feedback_input.value = text

                reason_select.on_value_change(on_reason_change)

                def confirm_audit():
                    chosen_status = status_select.value
                    chosen_feedback = feedback_input.value or ""

                    if doc.document_id:
                        doc.status = chosen_status
                        doc.feedback = chosen_feedback
                        service.update_document(doc)
                        ui.notify(f"Documento marcado como {chosen_status}!", color="positive")
                        audit_dialog.close()
                        refresh_docs()

                with ui.row().classes("w-full justify-end gap-2 pt-4 border-t border-slate-200 mt-2"):
                    ui.button("Cancelar", on_click=audit_dialog.close).props("flat color=grey")
                    ui.button("Salvar Decisão", icon="done", on_click=confirm_audit).props("color=primary")

            audit_dialog.open()

        refresh_docs()

        with ui.row().classes("w-full justify-end pt-4 border-t border-slate-200 mt-3"):
            ui.button("Fechar", on_click=dialog.close).props("flat color=grey")

    if on_close:
        dialog.on("hide", on_close)

    dialog.open()
