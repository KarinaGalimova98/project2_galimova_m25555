"""Core logic for working with tables and metadata."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

ALLOWED_TYPES = {"int", "str", "bool"}


def _parse_columns(raw_columns: List[str]) -> Tuple[bool, List[Tuple[str, str]]]:
    """Parse columns from 'name:type' strings.

    Returns (success, columns).
    On error prints message and returns (False, []).
    """
    parsed: List[Tuple[str, str]] = []

    for item in raw_columns:
        if ":" not in item:
            print(f"Некорректное значение: {item}. Попробуйте снова.")
            return False, []

        name, type_name = item.split(":", 1)
        name = name.strip()
        type_name = type_name.strip()

        if not name or not type_name:
            print(f"Некорректное значение: {item}. Попробуйте снова.")
            return False, []

        if type_name not in ALLOWED_TYPES:
            print(
                f"Некорректное значение: {item}. "
                "Поддерживаемые типы: int, str, bool."
            )
            return False, []

        parsed.append((name, type_name))

    return True, parsed


def create_table(
    metadata: Dict[str, Any],
    table_name: str,
    columns: List[str],
) -> Dict[str, Any]:

    """Create a new table in metadata.

    - Adds ID:int column if user did not specify it.
    - Validates types.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not columns:
        print("Некорректное значение: отсутствует описание столбцов. Попробуйте снова.")
        return metadata

    ok, parsed_columns = _parse_columns(columns)
    if not ok:
        return metadata

    has_id = any(col_name.lower() == "id" for col_name, _ in parsed_columns)
    if not has_id:
        parsed_columns.insert(0, ("ID", "int"))

    metadata[table_name] = {
        "columns": [
            {"name": col_name, "type": col_type}
            for col_name, col_type in parsed_columns
        ]
    }

    cols_str = ", ".join(f"{name}:{type_name}" for name, type_name in parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')

    return metadata


def drop_table(metadata: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """Drop table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: Dict[str, Any]) -> None:
    """Print all tables in metadata."""
    if not metadata:
        print("Таблицы отсутствуют.")
        return

    for name in metadata:
        print(f"- {name}")
