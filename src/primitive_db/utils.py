"""Utility helpers for the primitive DB project."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

DATA_DIR = "data"

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


def load_table_data(table_name: str):
    """Load table data from data/<table>.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_table_data(table_name: str, data):
    """Save table data to data/<table>.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
