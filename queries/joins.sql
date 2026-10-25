-- Одна строка на заказ: order_id, item_count, shipment_count, joined_rows.
-- joined_rows — число строк после LEFT JOIN позиций и доставок.
-- Напишите запрос самостоятельно. Следующий SELECT — пустая заготовка.
SELECT order_id, 0 AS item_count, 0 AS shipment_count, 0 AS joined_rows
FROM orders WHERE 1 = 0;
