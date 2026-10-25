-- Одна строка на заказ: order_id, order_amount_cents, paid_amount_cents, unpaid_amount_cents.
-- Получите суммы позиций и платежей независимо и сверьте разницу.
SELECT order_id, 0 AS order_amount_cents, 0 AS paid_amount_cents,
       0 AS unpaid_amount_cents FROM orders WHERE 1 = 0;
