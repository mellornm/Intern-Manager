"""
Status badges and progress pills for document compliance and active status.
"""

from nicegui import ui


def create_status_badge(status: str):
    """
    Renders a semantic badge based on status text.
    """
    status_lower = (status or "").lower()

    if status_lower in ("aprovado", "ativo", "entregue"):
        return (
            ui.badge(status, color="green-1", text_color="green-9")
            .classes("text-[11px] font-bold px-2 py-0.5 rounded-md border border-green-200")
        )
    elif status_lower in ("concluído", "concluido"):
        return (
            ui.badge(status, color="blue-1", text_color="blue-9")
            .classes("text-[11px] font-bold px-2 py-0.5 rounded-md border border-blue-200")
        )
    elif status_lower in ("reprovado", "inativo", "sem local", "erro de data"):
        return (
            ui.badge(status, color="red-1", text_color="red-9")
            .classes("text-[11px] font-bold px-2 py-0.5 rounded-md border border-red-200")
        )
    elif status_lower in ("pendente", "com pendência", "com pendencia", "a iniciar", "incompleto"):
        return (
            ui.badge(status, color="amber-1", text_color="amber-9")
            .classes("text-[11px] font-bold px-2 py-0.5 rounded-md border border-amber-200")
        )
    elif status_lower in ("não se aplica", "nao se aplica"):
        return (
            ui.badge(status, color="grey-2", text_color="grey-8")
            .classes("text-[11px] font-semibold px-2 py-0.5 rounded-md border border-slate-200")
        )
    else:
        return (
            ui.badge(status or "N/A", color="blue-1", text_color="blue-9")
            .classes("text-[11px] font-semibold px-2 py-0.5 rounded-md border border-blue-200")
        )


def create_progress_pill(approved: int, total: int):
    """
    Renders a document completion progress indicator.
    """
    if total == 0:
        return ui.badge("Sem Docs", color="grey-3", text_color="grey-8").classes(
            "text-xs font-semibold px-2 py-0.5 rounded"
        )

    pct = int((approved / total) * 100)
    color = "green-7" if pct == 100 else ("amber-8" if pct >= 50 else "red-6")

    with ui.row().classes("items-center gap-2"):
        ui.linear_progress(value=pct / 100, show_value=False, color=color).props(
            "rounded size=6px track-color=grey-3"
        ).classes("w-20")
        ui.label(f"{approved}/{total} ({pct}%)").classes("text-xs font-semibold text-slate-600")
