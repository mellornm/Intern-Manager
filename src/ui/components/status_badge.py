"""
Status badges and progress pills for document compliance and active status.
"""

from nicegui import ui


def create_status_badge(status: str):
    """
    Renders a colored badge based on status text.
    """
    status_lower = (status or "").lower()

    if status_lower in ("aprovado", "ativo", "entregue", "concluído", "concluido"):
        return ui.badge(status, color="green-7").classes("text-xs font-semibold px-2 py-1 rounded")
    elif status_lower in ("reprovado", "inativo", "sem local"):
        return ui.badge(status, color="red-7").classes("text-xs font-semibold px-2 py-1 rounded")
    elif status_lower in ("pendente", "com pendência", "com pendencia"):
        return ui.badge(status, color="amber-8").classes("text-xs font-semibold px-2 py-1 rounded")
    elif status_lower in ("não se aplica", "nao se aplica"):
        return ui.badge(status, color="grey-6").classes("text-xs font-semibold px-2 py-1 rounded")
    else:
        return ui.badge(status or "N/A", color="blue-7").classes("text-xs font-semibold px-2 py-1 rounded")


def create_progress_pill(approved: int, total: int):
    """
    Renders a document completion progress indicator.
    """
    if total == 0:
        return ui.badge("Sem Docs", color="grey-5").classes("text-xs font-semibold")

    pct = int((approved / total) * 100)
    color = "green-7" if pct == 100 else ("amber-8" if pct >= 50 else "red-7")

    with ui.row().classes("items-center gap-1.5"):
        ui.linear_progress(value=pct / 100, show_value=False, color=color).classes("w-16 rounded")
        ui.label(f"{approved}/{total} ({pct}%)").classes("text-xs font-medium text-slate-600")
