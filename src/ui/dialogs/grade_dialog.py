"""
Grades and Evaluation dialog with real-time weighted average calculation.
"""

from typing import Callable, Dict, Optional
from nicegui import ui

from core.models.grade import Grade
from core.models.intern import Intern
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService


def open_grade_dialog(
    intern: Intern,
    criteria_service: EvaluationCriteriaService,
    grade_service: GradeService,
    on_success: Optional[Callable] = None,
):
    """Opens modal to view and assign grades for an intern."""
    criteria_list = criteria_service.list_active_criteria()

    if not criteria_list:
        ui.notify("Nenhum critério de avaliação ativo cadastrado no sistema.", color="warning")
        return

    existing_grades = grade_service.get_by_intern_id(intern.intern_id) if intern.intern_id else []
    grades_map: Dict[int, float] = {
        g.criteria_id: g.value for g in existing_grades if g.criteria_id is not None
    }

    grade_inputs: Dict[int, ui.number] = {}

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("grade", color="amber-8", size="md")
                with ui.column().classes("gap-0"):
                    ui.label(f"Notas: {intern.name}").classes("text-xl font-bold text-slate-800")
                    ui.label(f"Semestre: {intern.term or 'N/A'}").classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        # Container for live average banner
        with ui.card().classes("w-full p-4 bg-slate-100 border border-slate-200 my-2 flex-row justify-between items-center"):
            with ui.column().classes("gap-0"):
                ui.label("MÉDIA PONDERADA").classes("text-xs font-bold text-slate-500")
                avg_label = ui.label("0.0").classes("text-2xl font-black text-blue-700")
            status_badge = ui.badge("Pendente", color="grey-6").classes("text-sm px-3 py-1 font-bold")

        def recalculate_average():
            total_weight = 0.0
            weighted_sum = 0.0

            for crit in criteria_list:
                if crit.criteria_id in grade_inputs:
                    val = float(grade_inputs[crit.criteria_id].value or 0.0)
                    weight = float(crit.weight or 1.0)
                    weighted_sum += val * weight
                    total_weight += weight

            final_avg = (weighted_sum / total_weight) if total_weight > 0 else 0.0
            avg_label.set_text(f"{final_avg:.1f}")

            if final_avg >= 7.0:
                status_badge.set_text("Aprovado")
                status_badge.props("color=green-7")
            elif final_avg >= 5.0:
                status_badge.set_text("Em Recuperação")
                status_badge.props("color=amber-8")
            else:
                status_badge.set_text("Reprovado")
                status_badge.props("color=red-7")

        # Form fields for each criterion
        with ui.column().classes("w-full gap-3 py-2 max-h-96 overflow-y-auto"):
            for crit in criteria_list:
                crit_id = crit.criteria_id
                init_val = grades_map.get(crit_id, 0.0)

                with ui.row().classes("w-full items-center justify-between p-2 border-b border-slate-100"):
                    with ui.column().classes("gap-0 max-w-xs"):
                        ui.label(crit.name).classes("font-semibold text-slate-800 text-sm")
                        ui.label(f"Peso: {crit.weight or 1.0} • {crit.description or ''}").classes("text-xs text-slate-400 truncate")

                    inp = ui.number(
                        value=init_val,
                        min=0.0,
                        max=10.0,
                        step=0.5,
                        format="%.1f",
                        on_change=lambda _: recalculate_average(),
                    ).classes("w-28").props("outlined dense")
                    grade_inputs[crit_id] = inp

        recalculate_average()

        def handle_save_grades():
            if not intern.intern_id:
                ui.notify("Erro: Aluno sem ID salvo.", color="negative")
                return

            try:
                grades_to_save = [
                    Grade(
                        intern_id=intern.intern_id,
                        criteria_id=crit_id,
                        value=float(inp.value or 0.0),
                    )
                    for crit_id, inp in grade_inputs.items()
                ]
                grade_service.save_batch_grades(grades_to_save)
                ui.notify("Notas salvas com sucesso!", color="positive")
                dialog.close()
                if on_success:
                    on_success()
            except Exception as e:
                ui.notify(f"Erro ao salvar notas: {e}", color="negative")

        with ui.row().classes("w-full justify-end gap-2 pt-4 border-t border-slate-200 mt-2"):
            ui.button("Cancelar", on_click=dialog.close).props("flat color=grey")
            ui.button("Salvar Avaliação", icon="save", on_click=handle_save_grades).props("color=primary")

    dialog.open()
