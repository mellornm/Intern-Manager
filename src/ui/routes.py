"""
Web Route Definitions for InternManager Pro NiceGUI.
Connects HTTP/Websocket paths to page renders with pure dependency injection.
"""

from typing import Optional
from nicegui import ui

from ui.context import get_container
from ui.pages.calendar_page import render_calendar_page
from ui.pages.criteria_page import render_criteria_page
from ui.pages.dashboard_page import render_dashboard_page
from ui.pages.interns_page import render_interns_page
from ui.pages.settings_page import render_settings_page
from ui.pages.venues_page import render_venues_page


def register_routes():
    """Registers all application web pages with NiceGUI."""
    container = get_container()

    @ui.page("/")
    @ui.page("/dashboard")
    def dashboard():
        render_dashboard_page(container)

    @ui.page("/interns")
    def interns(filter: Optional[str] = None):
        render_interns_page(container, initial_filter=filter)

    @ui.page("/venues")
    def venues():
        render_venues_page(container)

    @ui.page("/criteria")
    def criteria():
        render_criteria_page(container)

    @ui.page("/calendar")
    def calendar():
        render_calendar_page(container)

    @ui.page("/settings")
    def settings():
        render_settings_page(container)
