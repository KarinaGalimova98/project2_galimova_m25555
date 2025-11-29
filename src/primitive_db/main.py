#!/usr/bin/env python3

"""Entry point for primitive_db project."""

from __future__ import annotations

from .engine import run


def main() -> None:
    """Run the database application."""
    run()


if __name__ == "__main__":
    main()
