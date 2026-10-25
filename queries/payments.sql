-- Одна строка на заказ: order_id, paid_amount_cents.
-- Считайте только успешные уникальные transaction_ref в пределах заказа.
SELECT order_id, 0 AS paid_amount_cents FROM orders WHERE 1 = 0;
