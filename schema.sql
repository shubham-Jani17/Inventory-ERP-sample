-- =============================================
-- Mini Inventory Management System - Schema
-- =============================================

CREATE DATABASE IF NOT EXISTS inventory_db1;
USE inventory_db1;

-- Items Master Table
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_code VARCHAR(50) UNIQUE NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    quantity INT DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'Nos',
    reorder_level INT DEFAULT 10,
    rate DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    transaction_type ENUM('IN', 'OUT') NOT NULL,
    quantity INT NOT NULL,
    note TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- -- Sample Data
-- INSERT INTO items (item_code, item_name, category, quantity, unit, reorder_level, rate) VALUES
-- ('ITEM-001', 'Laptop', 'Electronics', 15, 'Nos', 5, 45000.00),
-- ('ITEM-002', 'Office Chair', 'Furniture', 8, 'Nos', 3, 5500.00),
-- ('ITEM-003', 'A4 Paper Ream', 'Stationery', 3, 'Ream', 10, 350.00),
-- ('ITEM-004', 'Keyboard', 'Electronics', 20, 'Nos', 8, 1200.00),
-- ('ITEM-005', 'Monitor', 'Electronics', 6, 'Nos', 4, 12000.00),
-- ('ITEM-006', 'Desk', 'Furniture', 2, 'Nos', 3, 8000.00),
-- ('ITEM-007', 'Pen Box', 'Stationery', 50, 'Box', 15, 120.00);

-- INSERT INTO transactions (item_id, transaction_type, quantity, note, date) VALUES
-- (1, 'IN', 10, 'Initial stock', '2024-01-01'),
-- (1, 'OUT', 2, 'Issued to HR dept', '2024-01-05'),
-- (2, 'IN', 5, 'Purchase from vendor', '2024-01-03'),
-- (3, 'IN', 20, 'Monthly stationery order', '2024-01-04'),
-- (3, 'OUT', 17, 'Distributed to teams', '2024-01-06'),
-- (4, 'IN', 15, 'New batch received', '2024-01-07'),
-- (5, 'OUT', 2, 'Issued to accounts', '2024-01-08');
