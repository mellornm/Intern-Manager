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

    init_name = criteria.name if is_edit and criteria else ""
    init_desc = criteria.description if is_edit and criteria else ""
    init_weight = (
        criteria.weight if (is_edit and criteria and criteria.weight is not None) else 2.5
    )

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-md p-0 rounded-2xl overflow-hidden shadow-2xl border border-slate-200"
    ):
        with ui.row().classes(
            "w-full px-6 py-4 bg-slate-50 border-b border-slate-200 items-center justify-between"
        ):
            with ui.row().classes("items-center gap-3"):
                ui.avatar("rule", color="blue-1", text_color="primary", size="md")
                with ui.column().classes("gap-0"):
                    ui.label(dialog_title).classes("text-base sm:text-lg font-bold text-slate-900")
                    ui.label("Defina o título e o peso máximo da nota").classes(
                        "text-xs text-slate-500"
                    )
            ui.button(icon="close", on_click=dialog.close).props(
                "flat round dense size=sm color=grey-7"
            )

        with ui.column().classes("w-full px-6 py-5 gap-4"):
            name_input = (
                ui.input(
                    "Nome do Critério *",
                    value=init_name,
                    placeholder="Ex: Assiduidade e Pontualidade",
                )
                .classes("w-full")
                .props("outlined dense hide-bottom-space")
            )
            with name_input.add_slot("prepend"):
                ui.icon("label", size="xs").classes("text-slate-400")

            desc_input = (
                ui.textarea(
                    "Descrição / Orientações",
                    value=init_desc,
                    placeholder="Ex: Avaliação de cumprimento da escala e compromissos...",
                )
                .classes("w-full")
                .props("outlined dense rows=2 hide-bottom-space")
            )

            weight_input = (
                ui.number(
                    "Peso / Nota Máxima do Critério *",
                    value=init_weight,
                    min=0.1,
                    max=100.0,
                    step=0.5,
                    format="%.1f",
                )
                .classes("w-full")
                .props("outlined dense hide-bottom-space")
            )
            with weight_input.add_slot("prepend"):
                ui.icon("scale", size="xs").classes("text-slate-400")

        def handle_save():
            name = (name_input.value or "").strip()
            if not name:
                name_input.props("error error-message='Informe o nome do critério'")
                ui.notify("O nome do critério é obrigatório.", color="negative")
                return
            name_input.props(remove="error")

            weight = float(weight_input.value or 0.0)
            if weight <= 0:
                ui.notify("O peso deve ser maior que zero.", color="negative")
                return

            if is_edit and criteria:
                criteria.name = name
                criteria.description = desc_input.value or ""
                criteria.weight = weight

                try:
                    service.update_criteria(criteria)
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

        with ui.row().classes(
            "w-full px-6 py-3.5 bg-slate-50 border-t border-slate-200 justify-end items-center gap-2"
        ):
            ui.button("Cancelar", on_click=dialog.close).props("flat no-caps color=grey-7")
            ui.button("Salvar Critério", icon="check", on_click=handle_save).props(
                "unelevated no-caps color=primary"
            ).classes("px-5 font-semibold")

    dialog.open()
