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
        
        # Check if the intern is near the deadline using the custom role
        is_near_deadline = index.data(Qt.ItemDataRole.UserRole)
        
        display_text = str(text)
        if is_near_deadline:
            # Add a warning icon/symbol if the deadline is approaching
            display_text = f"⚠️ {display_text}"
            
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, display_text)

        painter.restore()


class ProgressBarDelegate(QStyledItemDelegate):
    """
    A delegate that renders a progress bar inside a table cell.
    
    Used to visualize time elapsed for an internship.
    """

    def paint(self, painter: QPainter, option, index):
        """
        Paints a progress bar representing the percentage value from the model.
        """
        # Retrieve the progress percentage (0-100)
        try:
            progress_val = int(index.data() or 0)
        except (ValueError, TypeError):
            progress_val = 0

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background to match alternating row colors
        painter.fillRect(option.rect, QColor(COLORS["white"]))

        # --- Progress Bar Geometry ---
        # Define the outer rectangle for the progress bar frame
        margin_h = 20
        margin_v = 15
        progress_rect = option.rect.adjusted(margin_h, margin_v, -margin_h, -margin_v)
        
        # --- Background Track ---
        # Draw a slightly darker track for better white text contrast
        track_path = QPainterPath()
        track_path.addRoundedRect(progress_rect, 6, 6)
        painter.fillPath(track_path, QBrush(QColor("#BDBDBD")))
        
        # --- Filled Progress ---
        # Calculate the width of the filled portion based on percentage
        if progress_val > 0:
            fill_width = int(progress_rect.width() * (progress_val / 100.0))
            fill_rect = progress_rect.adjusted(0, 0, -(progress_rect.width() - fill_width), 0)
            
            fill_path = QPainterPath()
            fill_path.addRoundedRect(fill_rect, 6, 6)
            
            # Use dynamic colors: warning color if near the end
            color = QColor(COLORS["primary"]) # Default blue
            if progress_val > 80:
                color = QColor("#E67E22") # Stronger orange for better contrast
            if progress_val >= 99:
                color = QColor(COLORS["success"]) # Success green
                
            painter.fillPath(fill_path, QBrush(color))

        # --- Percentage Text ---
        # Use White for maximum contrast over all states
        painter.setPen(QColor("#FFFFFF"))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        text = f"{progress_val}%"
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, text)

        painter.restore()
