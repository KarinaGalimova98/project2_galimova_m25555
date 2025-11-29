#!/usr/bin/env python3

"""Entry point for primitive_db project."""

from .engine import welcome


def main() -> None:
    """Run the application."""
    welcome()


if __name__ == "__main__":
    main()
