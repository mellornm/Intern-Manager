from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, 
    QListWidget, QLabel, QGroupBox, QSplitter, QPushButton
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from services.meeting_service import MeetingService
from services.visit_service import VisitService
from repository.meeting_repo import MeetingRepository
from repository.visit_repo import VisitRepository
from repository.intern_repo import InternRepository

class CalendarView(QWidget):
    """
    UI View for supervising meetings and technical visits on a calendar.
    """
    def __init__(self):
        super().__init__()
        # Repositories & Services
        self.meeting_service = MeetingService(MeetingRepository())
        self.visit_service = VisitService(VisitRepository())
        self.intern_repo = InternRepository()
        
        self._setup_ui()
        self._load_month_data()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Calendário de Supervisão")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        btn_today = QPushButton("Mês Atual")
        btn_today.clicked.connect(self._go_to_today)
        header_layout.addStretch()
        header_layout.addWidget(btn_today)
        
        layout.addLayout(header_layout)
        
        # Splitter for Calendar and Details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        
        # Styling to fix the month/year selector arrows and layout
        self.calendar.setStyleSheet(f"""
            QCalendarWidget QToolButton {{
                color: #2c3e50;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                padding: 2px 10px; /* Gives more space for text and arrow */
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: #e0e0e0;
            }}
            QCalendarWidget QToolButton::menu-indicator {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                right: 5px;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{ 
                background-color: white; 
            }}
        """)
        
        self.calendar.selectionChanged.connect(self._on_date_selected)
        self.calendar.currentPageChanged.connect(self._load_month_data)
        
        splitter.addWidget(self.calendar)
        
        # Right: Event List
        self.details_group = QGroupBox("Eventos do Dia")
        details_layout = QVBoxLayout(self.details_group)
        
        self.lbl_selected_date = QLabel("Selecione uma data")
        self.lbl_selected_date.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        details_layout.addWidget(self.lbl_selected_date)
        
        self.list_events = QListWidget()
        details_layout.addWidget(self.list_events)
        
        splitter.addWidget(self.details_group)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)

    def _go_to_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.setCurrentPage(QDate.currentDate().year(), QDate.currentDate().month())

    def _load_month_data(self):
        """
        Loads all meetings and visits for the current visible month and highlights calendar days.
        """
        month = self.calendar.monthShown()
        year = self.calendar.yearShown()
        
        meetings = self.meeting_service.get_calendar_events(month, year)
        visits = self.visit_service.get_calendar_events(month, year)
        
        # Reset formatting
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Format for days with events
        meeting_format = QTextCharFormat()
        meeting_format.setBackground(QColor("#e1f5fe"))  # Light Blue
        meeting_format.setFontWeight(QFont.Bold)
        
        visit_format = QTextCharFormat()
        visit_format.setBackground(QColor("#f1f8e9"))   # Light Green
        visit_format.setFontWeight(QFont.Bold)
        
        both_format = QTextCharFormat()
        both_format.setBackground(QColor("#fff3e0"))    # Light Orange
        both_format.setFontWeight(QFont.Bold)

        # Map dates to event types
        event_map = {} # date_str -> set of types
        
        for m in meetings:
            event_map.setdefault(m.meeting_date, set()).add("meeting")
        for v in visits:
            event_map.setdefault(v.visit_date, set()).add("visit")
            
        for date_str, types in event_map.items():
            qdate = QDate.fromString(date_str, Qt.ISODate)
            if "meeting" in types and "visit" in types:
                self.calendar.setDateTextFormat(qdate, both_format)
            elif "meeting" in types:
                self.calendar.setDateTextFormat(qdate, meeting_format)
            else:
                self.calendar.setDateTextFormat(qdate, visit_format)
                
        self._on_date_selected()

    def _on_date_selected(self):
        """
        Shows details of meetings/visits for the selected date.
        """
        selected_date = self.calendar.selectedDate()
        date_iso = selected_date.toString(Qt.ISODate)
        self.lbl_selected_date.setText(selected_date.toString("dd/MM/yyyy"))
        
        self.list_events.clear()
        
        # Fetch events for this specific date
        # Note: We reuse the range logic with start=end for simplicity
        meetings = self.meeting_service.repo.get_meetings_in_range(date_iso, date_iso)
        visits = self.visit_service.repo.get_visits_in_range(date_iso, date_iso)
        
        if not meetings and not visits:
            self.list_events.addItem("Nenhum evento agendado.")
            return
            
        for m in meetings:
            intern = self.intern_repo.get_by_id(m.intern_id)
            name = intern.name if intern else f"ID: {m.intern_id}"
            item = f"📅 REUNIÃO: {name}"
            self.list_events.addItem(item)
            
        for v in visits:
            intern = self.intern_repo.get_by_id(v.intern_id)
            name = intern.name if intern else f"ID: {v.intern_id}"
            item = f"📍 VISITA: {name}"
            self.list_events.addItem(item)
