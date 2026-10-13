"""
PDF Report generation and download dialog for NiceGUI.
Uses ReportLab via ReportService and triggers browser download via ui.download().
"""

import zipfile
from typing import List
from nicegui import ui

from config import TEMP_DIR
from core.models.intern import Intern
from ui.context import ServiceContainer
from utils.text_utils import sanitize_filename


def open_report_dialog(
    intern: Intern,
    container: ServiceContainer,
):
    """Opens modal to preview summary and generate/download an intern's evaluation PDF."""
    if not intern.intern_id:
        ui.notify("Aluno sem ID registrado.", color="negative")
        return

    intern_id = intern.intern_id
    venue = container.venue_service.get_by_id(intern.venue_id) if intern.venue_id else None
    criteria_list = container.criteria_service.list_active_criteria()
    grades = container.grade_service.get_by_intern_id(intern_id)
    documents = container.document_service.get_by_intern_id(intern_id)
    meetings = container.meeting_service.get_by_intern_id(intern_id)
    observations = container.observation_service.get_by_intern_id(intern_id)
    visits = container.visit_service.get_by_intern_id(intern_id)

    pending_docs = sum(1 for d in documents if (d.status or "").lower() != "aprovado")

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("picture_as_pdf", color="negative", size="md")
                with ui.column().classes("gap-0"):
                    ui.label("Gerar Relatório de Estágio").classes("text-xl font-bold text-slate-800")
                    ui.label(intern.name).classes("text-xs text-slate-500 font-semibold")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        with ui.column().classes("w-full gap-3 py-3"):
            # Summary boxes
            with ui.card().classes("w-full p-4 bg-slate-50 border border-slate-200 gap-2"):
                ui.label("RESUMO DE DADOS DO RELATÓRIO").classes("text-xs font-bold text-slate-500")

                with ui.row().classes("items-center justify-between text-sm"):
                    ui.label("Critérios / Notas Cadastradas:")
                    if grades:
                        ui.badge(f"{len(grades)} notas lançadas", color="green-7")
                    else:
                        ui.badge("Sem notas lançadas", color="amber-8")

                with ui.row().classes("items-center justify-between text-sm"):
                    ui.label("Situação Documental:")
                    if pending_docs == 0 and documents:
                        ui.badge("100% Conforme", color="green-7")
                    else:
                        ui.badge(f"{pending_docs} pendentes", color="amber-8" if pending_docs else "grey-6")

                with ui.row().classes("items-center justify-between text-sm"):
                    ui.label("Encontros de Supervisão:")
                    ui.badge(f"{len(meetings)} reuniões", color="blue-7")

                with ui.row().classes("items-center justify-between text-sm"):
                    ui.label("Visitas Técnicas in loco:")
                    ui.badge(f"{len(visits)} visitas", color="blue-7")

        def handle_generate_pdf():
            safe_name = sanitize_filename(intern.name)
            ra_suffix = f"_{intern.registration_number}" if intern.registration_number else ""
            pdf_filename = f"Relatorio_{safe_name}{ra_suffix}.pdf"
            pdf_path = TEMP_DIR / pdf_filename

            try:
                container.report_service.generate_pdf(
                    filepath=str(pdf_path),
                    intern=intern,
                    venue=venue,
                    criteria_list=criteria_list,
                    grades=grades,
                    documents=documents,
                    meetings=meetings,
                    observations=observations,
                    visits=visits,
                )

                ui.notify("Relatório gerado com sucesso! Iniciando download...", color="positive")
                ui.download(str(pdf_path), filename=pdf_filename)
                dialog.close()
            except Exception as e:
                ui.notify(f"Erro ao gerar relatório: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-2 pt-3 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Gerar e Baixar PDF", icon="download", on_click=handle_generate_pdf).props("color=negative")

    dialog.open()


def export_batch_reports_zip(
    intern_ids: List[int],
    container: ServiceContainer,
):
    """
    Generates PDF evaluation reports for all given intern IDs and packages them into a ZIP file.
    Triggers client download via ui.download().
    """
    if not intern_ids:
        ui.notify("Nenhum aluno selecionado para emissão de relatórios.", color="warning")
        return

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    zip_filename = "Relatorios_Supervisao_Estagio.zip"
    zip_path = TEMP_DIR / zip_filename

    generated_count = 0
    criteria_list = container.criteria_service.list_active_criteria()

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for intern_id in intern_ids:
                intern = container.intern_service.get_by_id(intern_id)
                if not intern:
                    continue

                venue = container.venue_service.get_by_id(intern.venue_id) if intern.venue_id else None
                grades = container.grade_service.get_by_intern_id(intern_id)
                documents = container.document_service.get_by_intern_id(intern_id)
                meetings = container.meeting_service.get_by_intern_id(intern_id)
                observations = container.observation_service.get_by_intern_id(intern_id)
                visits = container.visit_service.get_by_intern_id(intern_id)

                safe_name = sanitize_filename(intern.name)
                ra_suffix = f"_{intern.registration_number}" if intern.registration_number else ""
                pdf_name = f"Relatorio_{safe_name}{ra_suffix}.pdf"
                pdf_temp = TEMP_DIR / pdf_name

                container.report_service.generate_pdf(
                    filepath=str(pdf_temp),
                    intern=intern,
                    venue=venue,
                    criteria_list=criteria_list,
                    grades=grades,
                    documents=documents,
                    meetings=meetings,
                    observations=observations,
                    visits=visits,
                )

                if pdf_temp.exists():
                    zip_file.write(pdf_temp, arcname=pdf_name)
                    generated_count += 1
                    pdf_temp.unlink(missing_ok=True)

        if generated_count > 0:
            ui.notify(f"{generated_count} relatórios empacotados com sucesso! Baixando arquivo ZIP...", color="positive")
            ui.download(str(zip_path), filename=zip_filename)
        else:
            ui.notify("Nenhum relatório foi gerado.", color="warning")

    except Exception as e:
        ui.notify(f"Erro ao gerar relatórios em lote: {e}", color="negative")
