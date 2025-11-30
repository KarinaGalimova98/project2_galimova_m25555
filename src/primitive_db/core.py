"""Core logic for working with tables, metadata and CRUD operations."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from prettytable import PrettyTable

from src.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

from .constants import ALLOWED_TYPES

select_cache = create_cacher()


def _parse_columns(raw_columns: List[str]) -> Tuple[bool, List[Tuple[str, str]]]:
    """Parse columns from 'name:type' strings.

    Returns (success, columns).
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

@handle_db_errors
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
        print("Некорректное значение: отсутствует описание столбцов.")
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

@handle_db_errors
@confirm_action("удаление таблицы")
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


# CRUD ops

def _cast_value(value: str, type_name: str) -> Any:
    """Cast string value to proper Python type based on column type."""
    if type_name == "int":
        return int(value)

    if type_name == "bool":
        if value.lower() in ("true", "1"):
            return True
        if value.lower() in ("false", "0"):
            return False
        raise ValueError("Ожидалось значение bool (true/false).")

    # str
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value

@handle_db_errors
@log_time
def insert(
    metadata: Dict[str, Any],
    table_name: str,
    values: List[str],
    table_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Insert new row into table."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    # Берём все столбцы, кроме ID
    columns = metadata[table_name]["columns"][1:]  # список dict: {name, type}

    if len(values) != len(columns):
        print("Ошибка: количество значений не соответствует количеству столбцов.")
        return table_data

    record: Dict[str, Any] = {}

    for column_def, raw_value in zip(columns, values):
        col_name = column_def["name"]
        col_type = column_def["type"]
        try:
            record[col_name] = _cast_value(raw_value, col_type)
        except ValueError as exc:
            print(f"Ошибка преобразования значения для {col_name}: {exc}")
            return table_data

    new_id = (table_data[-1]["ID"] + 1) if table_data else 1
    full_record = {"ID": new_id, **record}
    table_data.append(full_record)

    # DEBUG: можно оставить, можно потом убрать
    # print("DEBUG INSERT:", full_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(
    table_data: List[Dict[str, Any]],
    where: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Select rows, optionally with simple equality condition.

    Результаты кэшируются по ключу (условие + размер таблицы).
    """

    def compute() -> List[Dict[str, Any]]:
        if where is None:
            return table_data

        key_where, value_where = next(iter(where.items()))

        def match(record: Dict[str, Any]) -> bool:
            return str(record.get(key_where)) == str(value_where)

        return [r for r in table_data if match(r)]

    if where is None:
        cache_key = ("select_all", len(table_data))
    else:
        # сортировка пар для стабильного ключа
        cache_key = (
            "select_where",
            len(table_data),
            tuple(sorted(where.items())),
        )

    return select_cache(cache_key, compute)

@handle_db_errors
def update(
    table_data: List[Dict[str, Any]],
    set_clause: Dict[str, Any],
    where: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Update rows matching where condition."""
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

@handle_db_errors
@confirm_action("удаление записей")
def delete(
    table_data: List[Dict[str, Any]],
    where: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Delete rows matching where condition."""
    key_where, value_where = next(iter(where.items()))
    new_data = [r for r in table_data if str(r.get(key_where)) != str(value_where)]
    deleted = len(table_data) - len(new_data)

    if deleted:
        print(f"Удалено записей: {deleted}")
    else:
        print("Записи не найдены.")

    return new_data


def print_table(table_data: List[Dict[str, Any]]) -> None:
    """Pretty-print table data using PrettyTable."""
    if not table_data:
        print("Нет данных.")
        return

    table = PrettyTable()
    headers = list(table_data[0].keys())
    table.field_names = headers

    for row in table_data:
        table.add_row([row[h] for h in headers])

    print(table)
