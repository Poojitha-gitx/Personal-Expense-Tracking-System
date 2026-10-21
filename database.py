"""
Database Connection and Data Access Layer for MySQL
Strictly uses MySQL with categories and expenses tables.
All database credentials are read directly from .env via Config.
"""

import os
from decimal import Decimal
import mysql.connector
from mysql.connector import Error as MySQLError
from config import Config

def get_db_connection(include_database=True):
    """
    Establish a connection to MySQL server using credentials from .env.
    """
    conn_params = {
        'host': Config.MYSQL_HOST,
        'port': Config.MYSQL_PORT,
        'user': Config.MYSQL_USER,
        'password': Config.MYSQL_PASSWORD,
    }
    if include_database:
        conn_params['database'] = Config.MYSQL_DB
        
    return mysql.connector.connect(**conn_params)

def init_db():
    """
    Initializes the MySQL database and tables from schema.sql.
    Creates expense_tracker_db if missing, and creates:
    - categories (category_id, category_name)
    - expenses (expense_id, expense_date, category_id, amount, description, payment_method)
    Populates sample fictional data if tables are empty.
    """
    try:
        # Step 1: Connect to MySQL server without database to ensure database exists
        server_conn = get_db_connection(include_database=False)
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        server_cursor.close()
        server_conn.close()

        # Step 2: Connect to the specific database
        conn = get_db_connection(include_database=True)
        cursor = conn.cursor()

        # Check if categories table exists
        cursor.execute("SHOW TABLES LIKE 'categories'")
        has_categories = cursor.fetchone()

        if not has_categories:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            for statement in sql_script.split(';'):
                stmt = statement.strip()
                if stmt and not stmt.lower().startswith('create database') and not stmt.lower().startswith('use '):
                    cursor.execute(stmt)
            conn.commit()
            print("[INFO] MySQL schema.sql executed.")

        # Ensure all standard academic categories exist without duplicating or deleting existing data
        default_categories = [
            'Food & Dining',
            'Shopping',
            'Transportation',
            'Education',
            'Healthcare',
            'Entertainment',
            'Bills & Utilities',
            'Groceries',
            'Other'
        ]
        for cat in default_categories:
            cursor.execute("INSERT IGNORE INTO categories (category_name) VALUES (%s)", (cat,))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "MySQL database initialized successfully."
    except MySQLError as err:
        return False, f"MySQL Error: {err}"

# --------------------------------------------------------------------
# Category CRUD Helpers (MySQL)
# --------------------------------------------------------------------

def get_categories():
    """Retrieve all categories from MySQL categories table."""
    conn = get_db_connection()
    categories = []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name ASC")
        categories = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return categories

def add_category(category_name):
    """Add a new category to MySQL."""
    name = category_name.strip()
    if not name:
        return False, "Category name cannot be empty."
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        return True, "Category added successfully."
    except Exception as e:
        return False, f"Error adding category: {str(e)}"
    finally:
        conn.close()

def delete_category(category_id):
    """Delete a category from MySQL if no expenses reference it."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE category_id = %s", (category_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            return False, f"Cannot delete category: {count} expense records are linked to it."
        
        cursor.execute("DELETE FROM categories WHERE category_id = %s", (category_id,))
        conn.commit()
        cursor.close()
        return True, "Category deleted successfully."
    except Exception as e:
        return False, f"Error deleting category: {str(e)}"
    finally:
        conn.close()

# --------------------------------------------------------------------
# Expense CRUD & Filter Helpers (MySQL)
# --------------------------------------------------------------------

def get_expenses(start_date=None, end_date=None, category_id=None, search=None):
    """
    Retrieve expenses from MySQL with optional filters:
    - start_date (YYYY-MM-DD)
    - end_date (YYYY-MM-DD)
    - category_id (int)
    - search keyword
    """
    conn = get_db_connection()
    expenses = []
    
    query = """
        SELECT 
            e.expense_id,
            e.expense_date,
            e.category_id,
            c.category_name,
            e.amount,
            e.description,
            e.payment_method
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND e.expense_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND e.expense_date <= %s"
        params.append(end_date)
    if category_id:
        query += " AND e.category_id = %s"
        params.append(int(category_id))
    if search:
        query += " AND (e.description LIKE %s OR e.payment_method LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
        
    query += " ORDER BY e.expense_date DESC, e.expense_id DESC"
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for r in rows:
            # Ensure Decimal amounts and dates are standard Python types
            r['amount'] = float(r['amount']) if isinstance(r['amount'], Decimal) else float(r['amount'])
            r['expense_date'] = str(r['expense_date'])
            expenses.append(r)
        cursor.close()
    finally:
        conn.close()
        
    return expenses

def get_expense_by_id(expense_id):
    """Retrieve single expense record by ID from MySQL."""
    conn = get_db_connection()
    expense = None
    query = """
        SELECT 
            e.expense_id,
            e.expense_date,
            e.category_id,
            c.category_name,
            e.amount,
            e.description,
            e.payment_method
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        WHERE e.expense_id = %s
    """
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (expense_id,))
        expense = cursor.fetchone()
        if expense:
            expense['amount'] = float(expense['amount'])
            expense['expense_date'] = str(expense['expense_date'])
        cursor.close()
    finally:
        conn.close()
        
    return expense

def add_expense(expense_date, category_id, amount, description, payment_method):
    """
    Insert new expense record into MySQL.
    Acceptance Criteria:
    - Amount must be positive (> 0)
    - Decimal safe conversion
    """
    try:
        amount_val = round(float(amount), 2)
    except (ValueError, TypeError):
        return False, "Amount must be a valid number."
        
    if amount_val <= 0:
        return False, "Expense amount must be strictly greater than zero."
        
    if not expense_date:
        return False, "Expense date is required."
        
    if not description or not description.strip():
        return False, "Expense description is required."
        
    conn = get_db_connection()
    query = """
        INSERT INTO expenses (expense_date, category_id, amount, description, payment_method)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (expense_date, int(category_id), amount_val, description.strip(), payment_method.strip())
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        return True, "Expense recorded successfully!"
    except Exception as e:
        return False, f"Failed to record expense: {str(e)}"
    finally:
        conn.close()

def update_expense(expense_id, expense_date, category_id, amount, description, payment_method):
    """Update existing expense record in MySQL."""
    try:
        amount_val = round(float(amount), 2)
    except (ValueError, TypeError):
        return False, "Amount must be a valid number."
        
    if amount_val <= 0:
        return False, "Expense amount must be strictly greater than zero."
        
    if not expense_date:
        return False, "Expense date is required."
        
    if not description or not description.strip():
        return False, "Expense description is required."
        
    conn = get_db_connection()
    query = """
        UPDATE expenses 
        SET expense_date = %s, category_id = %s, amount = %s, description = %s, payment_method = %s
        WHERE expense_id = %s
    """
    params = (expense_date, int(category_id), amount_val, description.strip(), payment_method.strip(), int(expense_id))
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        return True, "Expense updated successfully!"
    except Exception as e:
        return False, f"Failed to update expense: {str(e)}"
    finally:
        conn.close()

def delete_expense(expense_id):
    """Delete an expense record from MySQL."""
    conn = get_db_connection()
    query = "DELETE FROM expenses WHERE expense_id = %s"
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (int(expense_id),))
        conn.commit()
        cursor.close()
        return True, "Expense deleted successfully!"
    except Exception as e:
        return False, f"Failed to delete expense: {str(e)}"
    finally:
        conn.close()

def get_database_status():
    """Returns MySQL connection details and status."""
    return {
        'engine': 'MySQL',
        'host': Config.MYSQL_HOST,
        'port': Config.MYSQL_PORT,
        'db': Config.MYSQL_DB,
        'user': Config.MYSQL_USER
    }
