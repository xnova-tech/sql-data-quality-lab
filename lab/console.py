"""Единая кодировка сообщений CLI на Windows, macOS и Linux."""

import sys
from io import TextIOWrapper


def configure_console() -> None:
    if isinstance(sys.stdout, TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")
