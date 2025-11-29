"""Utility helpers for the primitive DB project."""

from __future__ import annotations

import json
from typing import Any, Dict


def load_metadata(filepath: str) -> Dict[str, Any]:
    """Load database metadata from JSON file.

    Returns empty dict if file does not exist or is invalid.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Поврежден
        return {}


def save_metadata(filepath: str, data: Dict[str, Any]) -> None:
    """Save database metadata to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
