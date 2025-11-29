"""Core logic for working with tables and metadata."""

from prettytable import PrettyTable
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


def insert(metadata, table_name, values, table_data):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name]["columns"][1:]  # без ID
    if len(values) != len(columns):
        print("Ошибка: количество значений не соответствует количеству столбцов.")
        return table_data

    parsed = {}

    for (col, col_type), raw_value in zip(columns, values):
        if col_type == "int":
            try:
                parsed[col] = int(raw_value)
            except ValueError:
                print(f"Ошибка: {raw_value} должно быть int.")
                return table_data

        elif col_type == "bool":
            if raw_value.lower() in ("true", "1"):
                parsed[col] = True
            elif raw_value.lower() in ("false", "0"):
                parsed[col] = False
            else:
                print(f"Ошибка: {raw_value} должно быть bool.")
                return table_data

        elif col_type == "str":
            parsed[col] = raw_value.strip('"')

    new_id = (table_data[-1]["ID"] + 1) if table_data else 1
    record = {"ID": new_id, **parsed}
    table_data.append(record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data, where=None):
    if where is None:
        return table_data

    key, value = next(iter(where.items()))

    def match(record):
        return str(record.get(key)) == str(value)

    return [r for r in table_data if match(r)]


def update(table_data, set_clause, where):
    key_where, value_where = next(iter(where.items()))
    updated = 0

    for record in table_data:
        if str(record.get(key_where)) == str(value_where):
            for k, v in set_clause.items():
                record[k] = v
            updated += 1

    if updated:
        print(f"Обновлено записей: {updated}")
    else:
        print("Записи не найдены.")

    return table_data


def delete(table_data, where):
    key_where, value_where = next(iter(where.items()))
    new_data = [r for r in table_data if str(r.get(key_where)) != str(value_where)]
    deleted = len(table_data) - len(new_data)

    if deleted:
        print(f"Удалено записей: {deleted}")
    else:
        print("Записи не найдены.")

    return new_data


def print_table(table_data):
    if not table_data:
        print("Нет данных.")
        return

    table = PrettyTable()
    headers = table_data[0].keys()
    table.field_names = list(headers)

    for row in table_data:
        table.add_row([row[h] for h in headers])

    print(table)
