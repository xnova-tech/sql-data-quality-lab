"""Независимая сверка строк источника без исполнения студенческого SQL."""

import sqlite3
from dataclasses import dataclass


class DataQualityError(ValueError):
    """Противоречивые строки источника не позволяют считать итог."""


@dataclass(frozen=True)
class OrderAmounts:
    order_id: int
    order_amount_cents: int
    paid_amount_cents: int

    @property
    def unpaid_amount_cents(self) -> int:
        return self.order_amount_cents - self.paid_amount_cents


@dataclass(frozen=True)
class JoinCounts:
    order_id: int
    item_count: int
    shipment_count: int
    joined_rows: int


def amounts(connection: sqlite3.Connection) -> dict[int, OrderAmounts]:
    order_ids = [row[0] for row in connection.execute("SELECT order_id FROM orders")]
    item_amounts = dict.fromkeys(order_ids, 0)
    for order_id, quantity, price in connection.execute("SELECT order_id, quantity, unit_price_cents FROM order_items"):
        item_amounts[order_id] += quantity * price

    transactions: dict[tuple[int, str], int] = {}
    for order_id, reference, status, value in connection.execute(
        "SELECT order_id, transaction_ref, status, amount_cents FROM payments"
    ):
        if status != "successful":
            continue
        key = (order_id, reference)
        if key in transactions and transactions[key] != value:
            raise DataQualityError(f"Конфликт успешной транзакции {reference} заказа {order_id}: разные суммы")
        transactions[key] = value

    paid_amounts = dict.fromkeys(order_ids, 0)
    for (order_id, _), value in transactions.items():
        paid_amounts[order_id] += value
    return {order_id: OrderAmounts(order_id, item_amounts[order_id], paid_amounts[order_id]) for order_id in order_ids}


def join_counts(connection: sqlite3.Connection) -> dict[int, JoinCounts]:
    item_counts = dict.fromkeys((row[0] for row in connection.execute("SELECT order_id FROM orders")), 0)
    shipment_counts = item_counts.copy()
    for (order_id,) in connection.execute("SELECT order_id FROM order_items"):
        item_counts[order_id] += 1
    for (order_id,) in connection.execute("SELECT order_id FROM shipments"):
        shipment_counts[order_id] += 1
    return {
        order_id: JoinCounts(
            order_id,
            count,
            shipment_counts[order_id],
            max(count, 1) * max(shipment_counts[order_id], 1),
        )
        for order_id, count in item_counts.items()
    }
