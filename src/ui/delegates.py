"""
Custom delegates for rendering items in Qt views.

This module provides specialized QStyledItemDelegate subclasses to customize
the appearance of data in components like QTableWidget.
"""

from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QColor, QPainter, QBrush, QPainterPath
from PySide6.QtCore import Qt
from ui.styles import COLORS


class StatusDelegate(QStyledItemDelegate):
    """
    A delegate to render a status string as a colored, rounded pill.

    This provides a more intuitive visual representation for status fields
    in a table, such as "Active", "Pending", or "Completed".
    """

    def paint(self, painter: QPainter, option, index):
        """
        Overrides the default paint method to draw the status pill.

        Args:
            painter (QPainter): The painter instance to use for drawing.
            option: Provides style options for the item.
            index: The model index of the item to be painted.
        """
        text = index.data()
        if not text:
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Ensure a clean background, which is important for alternating row colors.
        painter.fillRect(option.rect, QColor(COLORS["white"]))

        # --- Pill Style ---
        # Determine pill colors based on the status text.
        bg_color = QColor(COLORS["secondary"])
        text_color = QColor(COLORS["white"])

        lower_text = str(text).lower()
        if "concluído" in lower_text or "ativo" in lower_text:
            bg_color = QColor(COLORS["success"])
        elif "pendente" in lower_text or "reprovado" in lower_text:
            bg_color = QColor(COLORS["danger"])
        elif "andamento" in lower_text:
            bg_color = QColor(COLORS["primary"])
        elif "cancelado" in lower_text:
            bg_color = QColor(COLORS["dark"])

        # --- Pill Shape ---
        # Create a rounded rectangle for the pill background.
        rect = option.rect.adjusted(15, 8, -15, -8)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)

        painter.fillPath(path, QBrush(bg_color))

        # --- Pill Text ---
        # Draw the status text centered within the pill.
        painter.setPen(text_color)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(text))

        painter.restore()
