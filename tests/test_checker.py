"""Проверяющий отклоняет характерные неверные SQL-решения."""

import pytest
from lab.checker import CONTRACTS, CheckError, Task, check_rows, smoke
from lab.database import Case, open_case


def test_starter_smoke() -> None:
    smoke()


@pytest.mark.parametrize("task", list(Task))
def test_empty_query_is_rejected(task: Task) -> None:
    sql = "SELECT " + ", ".join(f"0 AS {column}" for column in CONTRACTS[task].columns) + " WHERE 1 = 0"
    connection = open_case(Case.BASE)
    try:
        with pytest.raises(CheckError, match="строк"):
            check_rows(connection, sql, task, Case.BASE)
    finally:
        connection.close()


@pytest.mark.parametrize(
    ("sql", "message"),
    [
        ("SELECT order_id, 0 AS order_amount_cents FROM orders", "order_amount_cents"),
        ("SELECT order_id, 0 AS order_amount_cents FROM orders WHERE order_id < 110", "строк"),
        ("SELECT order_id, 0 AS order_amount_cents FROM orders UNION ALL SELECT 101, 0", "строк"),
    ],
)
def test_wrong_query_is_rejected(sql: str, message: str) -> None:
    connection = open_case(Case.BASE)
    try:
        with pytest.raises(CheckError, match=message):
            check_rows(connection, sql, Task.AMOUNTS, Case.BASE)
    finally:
        connection.close()


def test_checker_does_not_accept_writes() -> None:
    connection = open_case(Case.BASE)
    try:
        with pytest.raises(CheckError, match="Ошибка SQL"):
            check_rows(connection, "DELETE FROM orders", Task.AMOUNTS, Case.BASE)
    finally:
        connection.close()
