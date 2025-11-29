"""Parsing helpers for WHERE, SET and VALUES clauses."""

from __future__ import annotations

from typing import Dict, List, Optional


def parse_where(args: List[str]) -> Optional[Dict[str, str]]:
    """Parse WHERE clause tokens into a dict.

    Example: ["age", "=", "28"] -> {"age": "28"}
    """
    if len(args) != 3 or args[1] != "=":
        print("Некорректное условие WHERE.")
        return None

    column = args[0]
    value = args[2]

    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    return {column: value}


def parse_set(args):
    if len(args) != 3 or args[1] != "=":
        print("Некорректное выражение SET.")
        return None

    col = args[0]
    val = args[2].strip('"')
    return {col: val}
