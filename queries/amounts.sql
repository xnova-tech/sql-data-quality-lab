-- Одна строка на заказ: order_id, order_amount_cents.
-- Стоимость позиции: quantity * unit_price_cents; отсутствие позиций = 0.
SELECT order_id, 0 AS order_amount_cents FROM orders WHERE 1 = 0;
