INSERT INTO users (user_id, display_name) VALUES
    (1, 'Покупатель 01'), (2, 'Покупатель 02'), (3, 'Покупатель 03'),
    (4, 'Покупатель 04'), (5, 'Покупатель 05'), (6, 'Покупатель 06'),
    (7, 'Покупатель 07'), (8, 'Покупатель 08'), (9, 'Покупатель 09'),
    (10, 'Покупатель 10');

INSERT INTO orders (order_id, user_id, order_status) VALUES
    (101, 1, 'shipped'), (102, 2, 'processing'), (103, 3, 'new'),
    (104, 4, 'shipped'), (105, 5, 'processing'), (106, 6, 'cancelled'),
    (107, 7, 'new'), (108, 8, 'shipped'), (109, 9, 'processing'),
    (110, 10, 'new'), (111, 1, 'processing'), (112, 2, 'shipped');

INSERT INTO order_items (item_id, order_id, quantity, unit_price_cents) VALUES
    (1, 101, 2, 2500), (2, 101, 1, 5000), (3, 101, 1, 5000),
    (4, 102, 1, 4000), (5, 102, 2, 1000),
    (6, 103, 1, 7800), (7, 103, 1, 1200),
    (8, 104, 3, 2000), (9, 104, 1, 1500),
    (10, 105, 1, 9999), (11, 105, 1, 1),
    (12, 106, 1, 3000), (13, 106, 2, 500),
    (14, 107, 1, 750), (15, 107, 1, 750),
    (16, 108, 1, 12000), (17, 108, 1, 1000),
    (18, 109, 2, 3200), (19, 109, 1, 1600),
    (20, 110, 1, 2500), (21, 111, 1, 6000),
    (22, 112, 1, 8000), (23, 112, 2, 2000);

INSERT INTO payments (event_id, order_id, transaction_ref, status, amount_cents) VALUES
    (1, 101, 'tx-101-a', 'successful', 15000),
    (2, 101, 'tx-101-a', 'successful', 15000),
    (3, 102, 'tx-102-a', 'successful', 2000),
    (4, 102, 'tx-102-b', 'pending', 4000),
    (5, 103, 'tx-103-a', 'failed', 9000),
    (6, 104, 'tx-104-a', 'successful', 7500),
    (7, 105, 'tx-105-a', 'successful', 5000),
    (8, 105, 'tx-105-b', 'successful', 5000),
    (9, 106, 'tx-106-a', 'failed', 4000),
    (10, 108, 'tx-108-a', 'successful', 13000),
    (11, 109, 'tx-109-a', 'successful', 8000),
    (12, 110, 'tx-110-a', 'pending', 2500),
    (13, 111, 'tx-111-a', 'successful', 6500),
    (14, 112, 'tx-112-a', 'successful', 5000),
    (15, 112, 'tx-112-b', 'successful', 7000);

INSERT INTO shipments (shipment_id, order_id, status) VALUES
    (1, 101, 'delivered'), (2, 101, 'delivered'),
    (3, 102, 'planned'), (4, 104, 'delivered'),
    (5, 104, 'shipped'), (6, 105, 'planned'),
    (7, 108, 'delivered'), (8, 108, 'shipped'),
    (9, 109, 'planned'), (10, 112, 'delivered');
