PRAGMA foreign_keys = ON;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    display_name TEXT NOT NULL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    order_status TEXT NOT NULL CHECK (order_status IN ('new', 'processing', 'shipped', 'cancelled'))
);
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0)
);
CREATE TABLE payments (
    event_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    transaction_ref TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('successful', 'pending', 'failed')),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
);
CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    status TEXT NOT NULL CHECK (status IN ('planned', 'shipped', 'delivered'))
);
