"""Utility decorators and caching helpers for the DB project."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Hashable

import prompt

Func = Callable[..., Any]


def handle_db_errors(func: Func) -> Func:
    """Decorator: centralised error handling for DB functions."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: файл данных не найден. "
                "Возможно, база данных ещё не инициализирована.",
            )
        except KeyError as exc:
            print(f"Ошибка: таблица или столбец {exc!r} не найден.")
        except ValueError as exc:
            print(f"Ошибка валидации: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"Произошла непредвиденная ошибка: {exc}")
        return None

    return wrapper


def confirm_action(action_name: str) -> Callable[[Func], Func]:
    """Decorator factory: ask user confirmation before dangerous actions."""
    from functools import wraps

    def decorator(func: Func) -> Func:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ',
            ).strip().lower()
            if answer != "y":
                print("Операция отменена пользователем.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func: Func) -> Func:
    """Decorator: log execution time of a function."""

    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result

    return wrapper


def create_cacher() -> Callable[[Hashable, Callable[[], Any]], Any]:
    """Create simple in-memory cache based on a closure."""

    cache: Dict[Hashable, Any] = {}

    def cache_result(key: Hashable, value_func: Callable[[], Any]) -> Any:
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value

    return cache_result
