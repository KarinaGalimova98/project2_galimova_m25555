"""Engine module: welcome screen and simple command loop."""

from __future__ import annotations

import prompt


def print_help() -> None:
    """Print available commands."""
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome() -> None:
    """Show welcome message and handle simple commands."""
    print("Первая попытка запустить проект!\n")
    print("***")
    print_help()

    while True:
        command = prompt.string("Введите команду: ").strip().lower()

        if command == "help":
            print()
            print_help()
        elif command == "exit":
            print("Выход из программы.")
            break
        elif command == "":
            # пустой ввод — просто заново спросим команду
            continue
        else:
            print(f"Неизвестная команда: {command}")
