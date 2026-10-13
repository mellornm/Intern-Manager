"""
Evaluation Criteria Management Page for NiceGUI.
"""

from nicegui import ui

from core.models.evaluation_criteria import EvaluationCriteria
from ui.context import ServiceContainer
from ui.dialogs.criteria_dialog import open_criteria_dialog
from ui.layout import page_layout


def render_criteria_page(container: ServiceContainer):
    """Renders the grading criteria list and management view."""
    with page_layout(title="Critérios de Avaliação", active_path="/criteria"):
        # Header and Actions
        with ui.row().classes("w-full justify-between items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0"):
                ui.label("Critérios de Avaliação").classes("text-2xl sm:text-3xl font-extrabold text-slate-900")
                ui.label("Parâmetros e pesos utilizados para o cálculo da média ponderada.").classes("text-sm text-slate-500")

            ui.button(
                "Novo Critério",
                icon="add",
                on_click=lambda: open_criteria_dialog(
                    service=container.criteria_service,
                    on_success=refresh_table,
                ),
            ).props("color=primary")

        table_container = ui.column().classes("w-full gap-3")

        def refresh_table():
            table_container.clear()
            criteria_list = container.criteria_service.list_active_criteria()

            with table_container:
                if not criteria_list:
                    with ui.card().classes("w-full p-8 card-shadow items-center justify-center gap-2"):
                        ui.icon("rule", size="xl").classes("text-slate-300")
                        ui.label("Nenhum critério de avaliação cadastrado.").classes("text-slate-500")
                    return

                total_weight = sum(c.weight for c in criteria_list if c.weight)
                ui.label(f"Total de {len(criteria_list)} critério(s) ativo(s) • Soma dos pesos: {total_weight:.1f}").classes("text-xs text-slate-500 px-1")

                for crit in criteria_list:
                    with ui.card().classes("w-full p-4 card-shadow flex-row items-center justify-between gap-3"):
                        with ui.row().classes("items-center gap-3"):
                            ui.avatar("rule", color="blue-1", text_color="primary", size="md")
                            with ui.column().classes("gap-0"):
                                ui.label(crit.name).classes("font-bold text-base text-slate-900")
                                if crit.description:
                                    ui.label(crit.description).classes("text-xs text-slate-500")

                        with ui.row().classes("items-center gap-4"):
                            ui.badge(f"Peso {crit.weight}", color="blue-8").classes("text-xs font-bold px-3 py-1")

                            with ui.row().classes("items-center gap-1"):
                                ui.button(
                                    icon="edit",
                                    on_click=lambda c=crit: open_criteria_dialog(
                                        service=container.criteria_service,
                                        criteria=c,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=primary").tooltip("Editar Critério")

                                ui.button(
                                    icon="delete",
                                    on_click=lambda c=crit: confirm_delete_criteria(c),
                                ).props("flat round dense size=sm color=negative").tooltip("Excluir Critério")

        def confirm_delete_criteria(crit: EvaluationCriteria):
            with ui.dialog() as del_dialog, ui.card().classes("p-6 dialog-card"):
                ui.label("Confirmar Exclusão").classes("text-lg font-bold text-slate-800")
                ui.label(f"Deseja excluir o critério '{crit.name}'?").classes("text-sm text-slate-600")

                with ui.row().classes("w-full justify-end gap-2 pt-4"):
                    ui.button("Cancelar", on_click=del_dialog.close).props("flat color=grey")

                    def do_del():
                        if crit.criteria_id:
                            container.criteria_service.delete(crit.criteria_id)
                            ui.notify("Critério excluído.", color="info")
                            del_dialog.close()
                            refresh_table()

                    ui.button("Excluir", icon="delete", on_click=do_del).props("color=negative")
            del_dialog.open()

        refresh_table()
