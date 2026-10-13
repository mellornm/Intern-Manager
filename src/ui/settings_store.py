"""
Persistent settings storage for InternManager web interface.
Uses JSON storage in USER_DATA_ROOT.
"""

import json
from typing import Any, Dict
from config import USER_DATA_ROOT

SETTINGS_FILE = USER_DATA_ROOT / "settings.json"


def get_default_settings() -> Dict[str, Any]:
    return {
        "institution_name": "Instituição de Ensino",
        "coordinator_name": "Coordenador não definido",
        "city_state": "Cidade - UF",
        "logo_path": "",
    }


def load_settings() -> Dict[str, Any]:
    """Loads system settings from JSON file with fallback to defaults."""
    settings = get_default_settings()

    # Try loading from JSON file first
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                settings.update(saved)
                return settings
        except Exception as e:
            print(f"Erro ao carregar settings.json: {e}")

    return settings


def save_settings(data: Dict[str, Any]) -> None:
    """Saves settings to JSON file."""
    current = load_settings()
    current.update(data)

    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar settings.json: {e}")
