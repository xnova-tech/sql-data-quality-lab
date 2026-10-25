"""Создание синтетической базы и независимых контрольных вариантов."""

import sqlite3
from enum import StrEnum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATION_ID = 1481526866


class Case(StrEnum):
    BASE = "base"
    DELIVERY = "delivery"
    PAYMENT_REIMPORT = "payment_reimport"
    FAILED_PAYMENT = "failed_payment"
    QUANTITY = "quantity"
    EQUAL_ITEM = "equal_item"
    EMPTY_ORDER = "empty_order"


def create_database(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA application_id = {APPLICATION_ID}")
    for name in ("schema.sql", "seed.sql"):
        connection.executescript((ROOT / "data" / name).read_text(encoding="utf-8"))
    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        raise ValueError(f"Нарушены внешние ключи: {violations}")


def apply_case(connection: sqlite3.Connection, case: Case) -> None:
    if case is Case.DELIVERY:
        connection.execute("INSERT INTO shipments VALUES (11, 101, 'planned')")
    elif case is Case.PAYMENT_REIMPORT:
        connection.execute("INSERT INTO payments VALUES (16, 105, 'tx-105-a', 'successful', 5000)")
    elif case is Case.FAILED_PAYMENT:
        connection.execute("INSERT INTO payments VALUES (16, 102, 'tx-102-c', 'failed', 90000)")
    elif case is Case.QUANTITY:
        connection.execute("UPDATE order_items SET quantity = 7 WHERE item_id = 4")
    elif case is Case.EQUAL_ITEM:
        connection.execute("INSERT INTO order_items VALUES (24, 107, 1, 750)")
    elif case is Case.EMPTY_ORDER:
        connection.execute("INSERT INTO orders VALUES (113, 3, 'new')")
    connection.commit()


def open_case(case: Case) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    create_database(connection)
    apply_case(connection, case)
    return connection
