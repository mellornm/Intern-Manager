from datetime import datetime
from typing import Optional

import qtawesome as qta

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles import COLORS


class ChartWidget(QFrame):
    """
    A custom QFrame that holds a Matplotlib Figure and Canvas.

    This provides a convenient container for charts and includes type hints
    for better static analysis with tools like Pylance.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvas] = None


class DashboardView(QWidget):
    """
    A widget that serves as the main dashboard for the application.

    It displays key performance indicators (KPIs) in summary cards and
    visualizes data through Matplotlib charts for a quick overview of
    the internship program's status.
    """

    def __init__(self, intern_service, doc_service, meeting_service, venue_service):
        """
        Initializes the DashboardView with required services.

        Args:
            intern_service: Service for intern-related data.
            doc_service: Service for document-related data.
            meeting_service: Service for meeting-related data.
            venue_service: Service for venue-related data.
        """
        super().__init__()
        self.i_service = intern_service
        self.d_service = doc_service
        self.m_service = meeting_service
        self.v_service = venue_service

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        """Initializes and configures the UI components for the dashboard."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # --- Header ---
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Monitoramento de Estágio")
        title.setStyleSheet(
            f"font-size: 28px; font-weight: 800; color: {COLORS['dark']};"
        )
        subtitle = QLabel("Status de alocação e conformidade documental.")
        subtitle.setStyleSheet(f"font-size: 14px; color: {COLORS['secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        btn_refresh = QPushButton(" Atualizar Dados")
        btn_refresh.setIcon(qta.icon("fa5s.sync-alt", color="white"))
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        btn_refresh.clicked.connect(self.refresh_data)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(btn_refresh)
        layout.addLayout(header_layout)

        # --- Top-level KPI Cards ---
        self.cards_container = QHBoxLayout()
        self.cards_container.setSpacing(20)
        layout.addLayout(self.cards_container)

        self.card_total = self._create_card_widget(
            "Total Alunos", "fa5s.user-graduate", COLORS["primary"]
        )
        self.card_no_venue = self._create_card_widget(
            "Sem Local", "fa5s.map-marker-alt", COLORS["danger"]
        )
        self.card_pending = self._create_card_widget(
            "Documentos Pendentes", "fa5s.file-contract", COLORS["warning"]
        )
        self.card_meetings = self._create_card_widget(
            "Reuniões (Mês)", "fa5s.calendar-check", COLORS["success"]
        )

        self.cards_container.addWidget(self.card_total)
        self.cards_container.addWidget(self.card_no_venue)
        self.cards_container.addWidget(self.card_pending)
        self.cards_container.addWidget(self.card_meetings)

        # --- Charts Area (50/50 Split) ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # Chart 1: Venue Distribution (Pie Chart)
        self.chart1_frame = self._create_chart_frame("Distribuição de Locais")
        charts_layout.addWidget(self.chart1_frame)

        # Chart 2: Document Status (Bar Chart with Filter)
        doc_container = QFrame()
        doc_container.setStyleSheet(
            f"background-color: {COLORS['white']}; border-radius: 12px; border: 1px solid {COLORS['border']};"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        doc_container.setGraphicsEffect(shadow)

        doc_layout = QVBoxLayout(doc_container)
        doc_layout.setContentsMargins(10, 15, 10, 5)

        # Header for the document chart
        doc_header = QHBoxLayout()
        lbl_doc = QLabel("Status Documental")
        lbl_doc.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {COLORS['dark']}; border: none;"
        )

        self.combo_doc_filter = QComboBox()

        # Document types for the filter dropdown, aligned with database entries.
        doc_types = [
            "Todos",
            "Contrato de Estágio",
            "Ficha de Frequência",
            "Diário de Campo",
            "Projeto de Intervenção",
            "Avaliação do Supervisor Local",
        ]
        self.combo_doc_filter.addItems(doc_types)
        self.combo_doc_filter.setCurrentIndex(1)  # Default to "Contrato de Estágio"
        self.combo_doc_filter.setFixedWidth(200)
        self.combo_doc_filter.currentTextChanged.connect(self.refresh_data)

        doc_header.addWidget(lbl_doc)
        doc_header.addStretch()
        doc_header.addWidget(self.combo_doc_filter)
        doc_layout.addLayout(doc_header)

        # Canvas for the document chart
        self.fig_docs = Figure(figsize=(4, 3), dpi=100)
        self.fig_docs.patch.set_facecolor("none")
        self.canvas_docs = FigureCanvas(self.fig_docs)
        self.canvas_docs.setStyleSheet("background-color: transparent;")
        doc_layout.addWidget(self.canvas_docs)

        charts_layout.addWidget(doc_container)
        layout.addLayout(charts_layout, stretch=1)

    def _create_card_widget(self, title: str, icon_name: str, color_hex: str) -> QFrame:
        """
        Creates a styled QFrame to be used as a KPI card.

        Args:
            title: The text to display below the value.
            icon_name: The Font Awesome icon identifier.
            color_hex: The hex color for the icon.

        Returns:
            A configured QFrame ready to be added to the layout.
        """
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background-color: {COLORS['white']}; border-radius: 12px; border: 1px solid {COLORS['border']}; }}"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        frame.setMinimumHeight(100)
        frame.setMaximumHeight(120)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon(icon_name, color=color_hex).pixmap(QSize(36, 36)))
        lbl_icon.setStyleSheet("border: none; background: transparent;")

        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        lbl_val = QLabel("0")
        lbl_val.setObjectName("value_label")
        lbl_val.setStyleSheet(
            f"font-size: 24px; font-weight: 800; color: {COLORS['dark']}; border: none; background: transparent;"
        )

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLORS['secondary']}; border: none; background: transparent; text-transform: uppercase;"
        )

        vbox.addWidget(lbl_val)
        vbox.addWidget(lbl_title)

        layout.addLayout(vbox)
        layout.addStretch()
        layout.addWidget(lbl_icon)
        return frame

    def _create_chart_frame(self, title: str) -> ChartWidget:
        """
        Creates a styled frame container for a Matplotlib chart.

        Args:
            title: The title to display above the chart.

        Returns:
            A configured ChartWidget with a figure and canvas initialized.
        """
        frame = ChartWidget()
        frame.setStyleSheet(
            f"background-color: {COLORS['white']}; border-radius: 12px; border: 1px solid {COLORS['border']};"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 15, 10, 5)

        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {COLORS['dark']}; border: none;"
        )
        layout.addWidget(lbl)

        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor("none")
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")

        layout.addWidget(canvas)
        frame.canvas = canvas
        frame.figure = fig
        return frame

    def _update_card_value(self, card_widget: QFrame, value: int):
        """Finds the 'value_label' in a card and updates its text."""
        lbl = card_widget.findChild(QLabel, "value_label")
        if lbl:
            lbl.setText(str(value))

    def refresh_data(self):
        """
        Fetches the latest data from all relevant services and updates the UI.

        This includes recalculating card values and redrawing all charts.
        """
        interns = self.i_service.get_all_interns()

        total_interns = len(interns)
        no_venue_count = sum(1 for i in interns if not i.venue_id)

        # Calculate total pending documents for the KPI card
        total_pending_items = 0
        for i in interns:
            docs = self.d_service.get_documents_by_intern(i.intern_id)
            if not docs or any(d.status != "Aprovado" for d in docs):
                total_pending_items += 1

        # Calculate meetings held in the current month
        all_meetings = self.m_service.repo.get_all()
        now = datetime.now()
        meetings_month = sum(
            1
            for m in all_meetings
            if datetime.strptime(m.meeting_date, "%Y-%m-%d").month == now.month
        )

        self._update_card_value(self.card_total, total_interns)
        self._update_card_value(self.card_no_venue, no_venue_count)
        self._update_card_value(self.card_pending, total_pending_items)
        self._update_card_value(self.card_meetings, meetings_month)

        self._plot_venue_distribution(self.chart1_frame, total_interns, no_venue_count)

        filter_doc = self.combo_doc_filter.currentText()
        self._plot_docs_filtered(filter_doc, interns)

    def _plot_venue_distribution(self, frame: ChartWidget, total: int, no_venue: int):
        """
        Generates and renders a donut chart for intern venue allocation.

        Args:
            frame: The target widget to draw the chart in.
            total: The total number of interns.
            no_venue: The number of interns without an assigned venue.
        """
        if frame.figure is None or frame.canvas is None:
            return

        frame.figure.clear()
        ax = frame.figure.add_axes((0, 0, 0.6, 1))

        with_venue = total - no_venue
        if total == 0:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        else:
            labels = ["Alocados", "Sem Local"]
            sizes = [with_venue, no_venue]
            colors = [COLORS["success"], COLORS["danger"]]

            pie_result = ax.pie(
                sizes,
                autopct="%1.0f%%",
                startangle=90,
                colors=colors,
                pctdistance=0.80,
                textprops={"color": "#FFFFFF", "fontsize": 10, "weight": "bold"},
                wedgeprops={"width": 0.4, "edgecolor": "white"},
            )
            wedges = pie_result[0]

            frame.figure.legend(
                wedges,
                labels,
                title="Status",
                loc="center left",
                bbox_to_anchor=(0.65, 0.5),
                frameon=False,
            )

        frame.canvas.draw()

    def _plot_docs_filtered(self, filter_name: str, interns: list):
        """
        Generates a horizontal bar chart of document statuses.

        The chart is filtered by the document name selected in the dropdown.

        Args:
            filter_name: The name of the document to filter by, or "Todos".
            interns: A list of all intern objects to process.
        """
        self.fig_docs.clear()
        ax = self.fig_docs.add_subplot(111)

        ok_count = 0
        pending_count = 0

        if filter_name == "Todos":
            # If 'All', an intern is 'pending' if any document is not approved.
            for i in interns:
                docs = self.d_service.get_documents_by_intern(i.intern_id)
                if not docs or any(d.status != "Aprovado" for d in docs):
                    pending_count += 1
                else:
                    ok_count += 1
        else:
            # For a specific document type
            for i in interns:
                docs = self.d_service.get_documents_by_intern(i.intern_id)
                target_docs = [
                    d for d in docs if filter_name.lower() in d.document_name.lower()
                ]
                # An intern is 'ok' if at least one matching doc is approved.
                # Otherwise, they are 'pending' for this document type.
                if not target_docs or not any(
                    d.status == "Aprovado" for d in target_docs
                ):
                    pending_count += 1
                else:
                    ok_count += 1

        categories = ["Aprovado", "Pendente"]
        values = [ok_count, pending_count]
        colors = [COLORS["success"], COLORS["warning"]]

        if sum(values) == 0:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        else:
            bars = ax.barh(categories, values, color=colors, height=0.4)
            ax.bar_label(bars, padding=3, fontweight="bold")
            ax.set_xlim(0, max(values) * 1.2 if max(values) > 0 else 1)

            # Clean up chart aesthetics
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.get_xaxis().set_visible(False)
            ax.tick_params(axis="y", length=0)

        self.fig_docs.tight_layout()
        self.canvas_docs.draw()
