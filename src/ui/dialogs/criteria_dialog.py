"""
Evaluation Criteria Add/Edit Dialog for NiceGUI.
"""

from typing import Callable, Optional
from nicegui import ui

from core.models.evaluation_criteria import EvaluationCriteria
from services.evaluation_criteria_service import EvaluationCriteriaService


def open_criteria_dialog(
    service: EvaluationCriteriaService,
    criteria: Optional[EvaluationCriteria] = None,
    on_success: Optional[Callable] = None,
):
    """Opens modal to add or edit evaluation criteria."""
    is_edit = criteria is not None
    dialog_title = "Editar Critério de Avaliação" if is_edit else "Novo Critério de Avaliação"

    init_name = criteria.name if is_edit else ""
    init_desc = criteria.description if is_edit else ""
    init_weight = criteria.weight if (is_edit and criteria.weight is not None) else 1.0

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-md p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("rule", color="primary", size="md")
                ui.label(dialog_title).classes("text-xl font-bold text-slate-800")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        with ui.column().classes("w-full gap-3 pt-2"):
            name_input = ui.input("Nome do Critério *", value=init_name, placeholder="Ex: Projeto de Intervenção").classes("w-full")
            desc_input = ui.input("Descrição / Instruções", value=init_desc, placeholder="Ex: Avaliação do relatório final").classes("w-full")
            weight_input = ui.number("Peso da Avaliação *", value=init_weight, min=0.1, max=100.0, step=0.5).classes("w-full")

        def handle_save():
            name = (name_input.value or "").strip()
            if not name:
                ui.notify("O nome do critério é obrigatório.", color="negative")
                return

            weight = float(weight_input.value or 1.0)
            if weight <= 0:
                ui.notify("O peso deve ser maior que zero.", color="negative")
                return

            if is_edit and criteria:
                criteria.name = name
                criteria.description = desc_input.value or ""
                criteria.weight = weight

                try:
                    criteria_service = service
                    criteria_service.update_criteria(criteria)
                    ui.notify("Critério atualizado com sucesso!", color="positive")
                    dialog.close()
                    if on_success:
                        on_success()
                except Exception as e:
                    ui.notify(f"Erro ao atualizar: {e}", color="negative")
            else:
                new_crit = EvaluationCriteria(
                    name=name,
                    description=desc_input.value or "",
                    weight=weight,
                )
                try:
                    service.add_new_criteria(new_crit)
                    ui.notify(f"Critério '{name}' adicionado!", color="positive")
                    dialog.close()
                    if on_success:
                        on_success()
                except Exception as e:
                    ui.notify(f"Erro ao salvar critério: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-2 pt-4 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Salvar Critério", icon="check", on_click=handle_save).props("color=primary")

    dialog.open()
