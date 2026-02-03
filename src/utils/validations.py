"""
Validation and Formatting Utilities.

This module centralizes reusable functions for validating input data
(like emails and dates) and for converting data formats between the UI
(BR format) and the database (ISO format).
"""
from datetime import datetime
import re
from typing import Any, Optional


DATE_BR_FORMAT = "%d/%m/%Y"  # Example: 25/12/2026 (UI input)
DATE_ISO_FORMAT = "%Y-%m-%d"  # Example: 2026-12-25 (database)

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def _try_parse_date(date_str: str) -> datetime:
    """
    Attempts to parse a date string using supported formats.

    This is an internal helper function used by date validation
    and normalization routines. It accepts both UI (BR) and
    database (ISO) date formats.

    Supported formats:
        - DD/MM/YYYY
        - YYYY-MM-DD

    Args:
        date_str (str): Date string to be parsed.

    Returns:
        datetime: Parsed datetime object.

    Raises:
        ValueError: If the date string does not match any supported format.
    """
    for fmt in (DATE_BR_FORMAT, DATE_ISO_FORMAT):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date format. Expected {DATE_BR_FORMAT} or {DATE_ISO_FORMAT}."
    )


def validate_email_format(email: str) -> None:
    """
    Verifies if a string matches a valid email format.

    Args:
        email (str): Email address to be validated.

    Raises:
        ValueError: If the email does not match the expected format.
    """
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Invalid email format.")


def validate_date_range(start_date_str: str, end_date_str: str) -> None:
    """
    Validates that two dates are valid and that the end date
    is strictly later than the start date.

    Both dates may be provided either in UI format (DD/MM/YYYY)
    or in ISO format (YYYY-MM-DD).

    Args:
        start_date_str (str): Start date.
        end_date_str (str): End date.

    Raises:
        ValueError: If dates are invalid or if the end date
        is not later than the start date.
    """
    dt_start = _try_parse_date(start_date_str)
    dt_end = _try_parse_date(end_date_str)

    if dt_end <= dt_start:
        raise ValueError("End date must be later than start date.")


def validate_required_fields(data_object: Any, fields_map: dict) -> None:
    """
    Validates the presence and basic integrity of required fields
    in a domain object.

    A field is considered missing if:
        - The attribute does not exist
        - The value is None
        - The value is an empty or whitespace-only string

    This function is intentionally generic and reusable across
    different domain entities (Intern, Venue, etc.).

    Args:
        data_object (Any): Domain object to be validated.
        fields_map (dict): Mapping of object attribute names to
            human-readable field names for error messages.

    Raises:
        ValueError: If one or more required fields are missing.
    """
    missing = []

    for attr, ui_attr_name in fields_map.items():
        value = getattr(data_object, attr, None)

        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(ui_attr_name)

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def parse_date_to_iso(date_str: str) -> str:
    """
    Converts a date string to ISO format (YYYY-MM-DD).

    The function is idempotent:
        - If the date is already in ISO format, it is returned unchanged.
        - If the date is in UI format (DD/MM/YYYY), it is converted.
        - Any other format raises an error.

    Args:
        date_str (str): Date string in ISO or UI format.

    Returns:
        str: Date string in ISO format.

    Raises:
        ValueError: If the date does not match any supported format.
    """
    dt = _try_parse_date(date_str)
    return dt.strftime(DATE_ISO_FORMAT)


def format_date_to_br(iso_date_str: Optional[str]) -> str:
    """
    Converts an ISO date string (YYYY-MM-DD) to UI format (DD/MM/YYYY).

    This function is intended for presentation purposes only,
    such as populating form fields or reports.

    Args:
        iso_date_str (Optional[str]): ISO date string from the database.

    Returns:
        str: Date formatted as DD/MM/YYYY, or an empty string if input is None.
        If parsing fails, the original value is returned as a fallback.
    """
    if not iso_date_str:
        return ""

    try:
        dt = datetime.strptime(iso_date_str, DATE_ISO_FORMAT)
        return dt.strftime(DATE_BR_FORMAT)
    except ValueError:
        return iso_date_str
