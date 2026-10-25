"""Исполнение SQL студента и сверка с независимым расчётом на разных данных."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from enum import StrEnum

from lab.database import ROOT, Case, open_case
from lab.reference import amounts, join_counts


class Task(StrEnum):
    JOINS = "joins"
    AMOUNTS = "amounts"
    PAYMENTS = "payments"
    RECONCILE = "reconcile"
    FINAL = "final"


@dataclass(frozen=True)
class QueryContract:
    file_name: str
    columns: tuple[str, ...]
    cases: tuple[Case, ...]


CONTRACTS = {
    Task.JOINS: QueryContract(
        "joins.sql",
        ("order_id", "item_count", "shipment_count", "joined_rows"),
        (Case.BASE, Case.DELIVERY, Case.EQUAL_ITEM, Case.EMPTY_ORDER),
    ),
    Task.AMOUNTS: QueryContract(
        "amounts.sql",
        ("order_id", "order_amount_cents"),
        (Case.BASE, Case.QUANTITY, Case.EQUAL_ITEM, Case.EMPTY_ORDER),
    ),
    Task.PAYMENTS: QueryContract(
        "payments.sql",
        ("order_id", "paid_amount_cents"),
        (Case.BASE, Case.PAYMENT_REIMPORT, Case.FAILED_PAYMENT, Case.EMPTY_ORDER),
    ),
    Task.RECONCILE: QueryContract(
        "reconcile.sql",
        ("order_id", "order_amount_cents", "paid_amount_cents", "unpaid_amount_cents"),
        tuple(Case),
    ),
    Task.FINAL: QueryContract(
        "final_report.sql",
        ("order_id", "order_status", "order_amount_cents", "paid_amount_cents", "unpaid_amount_cents"),
        tuple(Case),
    ),
}


class CheckError(ValueError):
    """SQL не соответствует объявленному контракту задания."""


def expected_rows(connection: sqlite3.Connection, task: Task) -> dict[int, tuple[int | str, ...]]:
    if task is Task.JOINS:
        return {
            order_id: (row.order_id, row.item_count, row.shipment_count, row.joined_rows)
            for order_id, row in join_counts(connection).items()
        }
    results = amounts(connection)
    if task is Task.AMOUNTS:
        return {order_id: (order_id, row.order_amount_cents) for order_id, row in results.items()}
    if task is Task.PAYMENTS:
        return {order_id: (order_id, row.paid_amount_cents) for order_id, row in results.items()}
    rows: dict[int, tuple[int | str, ...]] = {
        order_id: (order_id, row.order_amount_cents, row.paid_amount_cents, row.unpaid_amount_cents)
        for order_id, row in results.items()
    }
    if task is Task.FINAL:
        statuses = dict(connection.execute("SELECT order_id, order_status FROM orders"))
        return {order_id: (order_id, statuses[order_id], *row[1:]) for order_id, row in rows.items()}
    return rows


def check_rows(connection: sqlite3.Connection, sql: str, task: Task, case: Case) -> None:
    contract = CONTRACTS[task]
    expected = expected_rows(connection, task)
    rows = execute_query(connection, sql, contract)
    compare_rows(rows, contract, expected, case)


def execute_query(
    connection: sqlite3.Connection, sql: str, contract: QueryContract
) -> list[tuple[int | str | None, ...]]:
    connection.execute("PRAGMA query_only = ON")
    try:
        cursor = connection.execute(sql)
        if cursor.description is None:
            raise CheckError("Ожидается SELECT, возвращающий строки")
        names = tuple(column[0] for column in cursor.description)
        if names != contract.columns:
            raise CheckError(f"Ожидаются столбцы {', '.join(contract.columns)}; получены {', '.join(names)}")
        return cursor.fetchall()
    except sqlite3.Error as error:
        raise CheckError(f"Ошибка SQL: {error}") from error
    finally:
        connection.execute("PRAGMA query_only = OFF")


def compare_rows(
    rows: list[tuple[int | str | None, ...]],
    contract: QueryContract,
    expected: dict[int, tuple[int | str, ...]],
    case: Case,
) -> None:
    if len(rows) != len(expected):
        raise CheckError(f"{case}: ожидалось {len(expected)} строк, получено {len(rows)}")
    seen: set[int] = set()
    for row in rows:
        if not isinstance(row[0], int):
            raise CheckError(f"{case}: order_id должен быть целым числом")
        order_id = row[0]
        if order_id in seen:
            raise CheckError(f"{case}: заказ {order_id} повторяется; нужна одна строка на заказ")
        seen.add(order_id)
        if order_id not in expected:
            raise CheckError(f"{case}: лишний заказ {order_id}")
        for column, actual, wanted in zip(contract.columns, row, expected[order_id], strict=True):
            if type(actual) is not type(wanted) or actual != wanted:
                raise CheckError(f"{case}: заказ {order_id}, {column}: получено {actual!r}, ожидается {wanted}")
    if seen != expected.keys():
        raise CheckError(f"{case}: отсутствуют заказы {sorted(expected.keys() - seen)}")


def check_task(task: Task) -> None:
    contract = CONTRACTS[task]
    path = ROOT / "queries" / contract.file_name
    if not path.is_file():
        raise CheckError(f"Файл запроса не найден: queries/{contract.file_name}")
    sql = path.read_text(encoding="utf-8")
    for case in contract.cases:
        with closing(open_case(case)) as connection:
            check_rows(connection, sql, task, case)


def smoke() -> None:
    with closing(open_case(Case.BASE)) as connection:
        sizes = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("users", "orders", "order_items", "payments", "shipments")
        }
        required = {"users": 10, "orders": 12, "order_items": 23, "payments": 15, "shipments": 10}
        if sizes != required:
            raise CheckError(f"Нарушен состав исходных таблиц: {sizes}")
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise CheckError("Нарушены внешние ключи")
        results = amounts(connection)
        if len(results) != 12 or results[101].order_amount_cents != 15000:
            raise CheckError("Не прошла независимая сверка исходных строк")
    with closing(open_case(Case.PAYMENT_REIMPORT)) as connection:
        if amounts(connection)[105].paid_amount_cents != 10000:
            raise CheckError("Повторный импорт платежа изменил сумму")
