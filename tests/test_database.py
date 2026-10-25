"""Регрессии исходной модели и независимых расчётов."""

import sqlite3

import pytest
from lab.database import Case, open_case
from lab.reference import DataQualityError, amounts, join_counts


@pytest.mark.parametrize(
    ("case", "order_id", "amount", "paid"),
    [
        (Case.BASE, 101, 15000, 15000),
        (Case.BASE, 102, 6000, 2000),
        (Case.BASE, 103, 9000, 0),
        (Case.BASE, 105, 10000, 10000),
        (Case.BASE, 111, 6000, 6500),
        (Case.DELIVERY, 101, 15000, 15000),
        (Case.PAYMENT_REIMPORT, 105, 10000, 10000),
        (Case.FAILED_PAYMENT, 102, 6000, 2000),
        (Case.QUANTITY, 102, 30000, 2000),
        (Case.EQUAL_ITEM, 107, 2250, 0),
        (Case.EMPTY_ORDER, 113, 0, 0),
    ],
)
def test_independent_amounts(case: Case, order_id: int, amount: int, paid: int) -> None:
    connection = open_case(case)
    try:
        result = amounts(connection)[order_id]
        assert (result.order_amount_cents, result.paid_amount_cents) == (amount, paid)
    finally:
        connection.close()


def test_fanout_and_source_keys() -> None:
    connection = open_case(Case.BASE)
    try:
        assert join_counts(connection)[101].joined_rows == 6
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert len(amounts(connection)) == 12
    finally:
        connection.close()


def test_conflicting_reimport_is_error() -> None:
    connection = open_case(Case.BASE)
    try:
        connection.execute("INSERT INTO payments VALUES (16, 101, 'tx-101-a', 'successful', 14999)")
        with pytest.raises(DataQualityError, match="Конфликт успешной транзакции"):
            amounts(connection)
    finally:
        connection.close()


def test_foreign_key_rejects_unknown_order() -> None:
    connection = open_case(Case.BASE)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO shipments VALUES (11, 999, 'planned')")
    finally:
        connection.close()
