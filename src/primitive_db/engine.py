"""Engine: command loop and user interaction for primitive DB."""

from __future__ import annotations

import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata
from .utils import load_table_data, save_table_data
from .parser import parse_where, parse_set
from .core import (
    insert,
    select,
    update,
    delete,
    print_table,
)



METADATA_FILE = "db_meta.json"


def print_help() -> None:
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Main loop of the database engine."""
    print("***База данных***")
    print_help()

    while True:
        user_input = prompt.string("Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        command = args[0]

        if command == "help":
            print_help()
            continue

        if command == "exit":
            print("Выход из программы.")
            break

        metadata = load_metadata(METADATA_FILE)

        if command == "create_table":
            if len(args) < 3:
                print(
                    "Некорректное значение: недостаточно аргументов. "
                    "Попробуйте снова."
                )
                continue

            table_name = args[1]
            columns = args[2:]
            metadata = create_table(metadata, table_name, columns)
            save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение: ожидается имя таблицы. Попробуйте снова.")
                continue

            table_name = args[1]
            metadata = drop_table(metadata, table_name)
            save_metadata(METADATA_FILE, metadata)

        elif command == "insert":
            if len(args) < 4 or args[1] != "into" or args[3] != "values":
                print("Некорректная команда insert")
                continue

            table = args[2]
            raw_vals = user_input.split("values", 1)[1].strip()
            raw_vals = raw_vals.strip("()")
            values = [v.strip() for v in raw_vals.split(",")]

            table_data = load_table_data(table)
            table_data = insert(metadata, table, values, table_data)
            save_table_data(table, table_data)

        elif command == "select":
            if len(args) < 3 or args[1] != "from":
                print("Некорректная команда select")
                continue

            table = args[2]
            table_data = load_table_data(table)

            if len(args) == 3:
                result = select(table_data)
                print_table(result)
            continue

            if args[3] != "where":
                print("Некорректная команда select")
                continue

            where = parse_where(args[4:])
            result = select(table_data, where)           
            print_table(result)


        elif command == "list_tables":
            list_tables(metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
