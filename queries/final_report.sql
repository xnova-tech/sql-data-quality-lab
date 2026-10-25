-- Исходный отчёт содержит ошибки. Исправьте SQL самостоятельно.
-- Контракт: одна строка на каждый заказ; четыре поля указаны ниже.
SELECT o.order_id, o.order_status,
       SUM(i.quantity * i.unit_price_cents) AS order_amount_cents,
       SUM(p.amount_cents) AS paid_amount_cents,
       SUM(i.quantity * i.unit_price_cents) - SUM(p.amount_cents) AS unpaid_amount_cents
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
JOIN payments AS p ON p.order_id = o.order_id
LEFT JOIN shipments AS s ON s.order_id = o.order_id
WHERE p.status = 'successful'
GROUP BY o.order_id;
