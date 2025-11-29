"""Engine: command loop and user interaction for primitive DB."""

from __future__ import annotations

import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

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

        elif command == "list_tables":
            list_tables(metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
