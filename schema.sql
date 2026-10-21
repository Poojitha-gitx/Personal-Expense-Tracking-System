-- ====================================================================
-- Database Schema: Personal Expense Tracking and Analysis System
-- Academic Project
-- Technology Stack: MySQL, Python Flask, Pandas, NumPy, Matplotlib
-- ====================================================================

CREATE DATABASE IF NOT EXISTS expense_tracker_db;
USE expense_tracker_db;

-- --------------------------------------------------------------------
-- 1. Table: categories
-- Stores expense category classifications
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- 2. Table: expenses
-- Stores individual personal expense transactions
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    CONSTRAINT chk_positive_amount CHECK (amount > 0),
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- 3. Initial Sample Data: Categories (Preserves existing data)
-- --------------------------------------------------------------------
INSERT IGNORE INTO categories (category_id, category_name) VALUES
(1, 'Food & Dining'),
(2, 'Rent & Utilities'),
(3, 'Transportation'),
(4, 'Groceries'),
(5, 'Entertainment'),
(6, 'Healthcare & Medical'),
(7, 'Education & Books'),
(8, 'Personal Care & Shopping');

-- --------------------------------------------------------------------
-- 4. Initial Sample Data: Fictional Expenses
-- Covers multiple months (August, September, October 2026)
-- --------------------------------------------------------------------
INSERT IGNORE INTO expenses (expense_id, expense_date, category_id, amount, description, payment_method) VALUES
-- August 2026
(1, '2026-08-01', 2, 8500.00, 'Monthly Apartment Rent', 'Net Banking'),
(2, '2026-08-03', 4, 1850.50, 'Supermarket Weekly Groceries', 'UPI'),
(3, '2026-08-05', 3, 450.00, 'Metro Card Recharge', 'Credit Card'),
(4, '2026-08-08', 1, 620.00, 'Weekend Lunch with Friends', 'UPI'),
(5, '2026-08-11', 2, 780.00, 'Electricity Bill Payment', 'Net Banking'),
(6, '2026-08-15', 7, 1250.00, 'Python Data Science Textbook', 'Debit Card'),
(7, '2026-08-18', 4, 2100.00, 'Organic Groceries and Milk', 'UPI'),
(8, '2026-08-22', 5, 850.00, 'Movie Tickets & Snacks', 'Credit Card'),
(9, '2026-08-25', 6, 650.00, 'Routine Health Checkup', 'Cash'),
(10, '2026-08-28', 3, 380.00, 'Cab Fare to Airport', 'UPI'),

-- September 2026
(11, '2026-09-01', 2, 8500.00, 'Monthly Apartment Rent', 'Net Banking'),
(12, '2026-09-02', 4, 1920.00, 'Monthly Pantry Supplies', 'Debit Card'),
(13, '2026-09-05', 1, 480.00, 'Coffee and Bistro Snacks', 'Cash'),
(14, '2026-09-09', 3, 1200.00, 'Monthly Commute Train Pass', 'UPI'),
(15, '2026-09-12', 2, 950.00, 'High-Speed Broadband Internet Bill', 'Credit Card'),
(16, '2026-09-16', 8, 2350.00, 'New Formal Shoes & Apparel', 'Credit Card'),
(17, '2026-09-19', 4, 1640.50, 'Fresh Vegetables and Fruits', 'UPI'),
(18, '2026-09-21', 1, 1150.00, 'Family Dinner at Restaurant', 'Credit Card'),
(19, '2026-09-24', 6, 420.00, 'Pharmacy Vitamins and Medicine', 'UPI'),
(20, '2026-09-27', 5, 499.00, 'Music Streaming Annual Subscription', 'Credit Card'),

-- October 2026
(21, '2026-10-01', 2, 8500.00, 'Monthly Apartment Rent', 'Net Banking'),
(22, '2026-10-02', 4, 2300.00, 'Monthly Bulk Groceries', 'Debit Card'),
(23, '2026-10-04', 3, 500.00, 'Fuel for Two-Wheeler', 'Cash'),
(24, '2026-10-07', 1, 740.00, 'Pizza Night Delivery', 'UPI'),
(25, '2026-10-10', 2, 620.00, 'Water and Gas Utility Bill', 'UPI'),
(26, '2026-10-12', 7, 1800.00, 'Web Development Online Course', 'Credit Card'),
(27, '2026-10-14', 4, 1420.00, 'Weekend Supermarket Shopping', 'UPI'),
(28, '2026-10-16', 8, 890.00, 'Haircut & Grooming Essentials', 'Cash'),
(29, '2026-10-18', 5, 1200.00, 'Concert Ticket', 'Debit Card'),
(30, '2026-10-20', 3, 310.00, 'Metro Commute Rides', 'UPI');
