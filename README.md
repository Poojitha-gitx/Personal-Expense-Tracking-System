# Personal Expense Tracking and Analysis System

An academic, beginner-friendly web application designed to help individuals record personal expenses and gain clear, data-driven insights into their monthly spending patterns and category-wise expenditure.

---

## 📌 Project Overview

- **Project Objective:** Record personal expenses and help users understand monthly spending and category-wise expenditure.
- **Academic Scope:** Single-user learning project using fictional or voluntarily entered expense data. It is an educational tracking system, not a banking or financial-advice system.
- **Key Modules:**
  1. **Expense Management (CRUD):** Add, edit, delete, and list expenses with positive amount enforcement and decimal-safe handling.
  2. **Filtering Engine:** Filter records dynamically by date range (`start_date` to `end_date`), category, and description search. Totals automatically reflect the filtered view.
  3. **Data Analysis with Pandas & NumPy:**
     - **Pandas:** Grouping expenses by month and category, calculating expenditure percentages.
     - **NumPy:** Statistical measures including Mean, Median, Standard Deviation, Min, Max, and Daily Average.
  4. **Data Visualization with Matplotlib:** Category-wise donut/pie chart and month-wise bar chart rendered cleanly on the dashboard.
  5. **Monthly Reports:** Itemized monthly statements with printable/exportable views.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3, Vanilla JavaScript | Responsive financial dashboard, modern dark sidebar, KPI summary cards, filter bars, modals |
| **Backend** | Python Flask (v3.x) | Web routing, form validation, request handling, JSON APIs |
| **Database** | MySQL (with SQLite Fallback) | Relational database storage with foreign key constraints |
| **Data Analysis** | Pandas & NumPy | Grouping by month/category, numerical summary statistics |
| **Data Visualization** | Matplotlib | High-DPI pie and bar chart image generation (rendered as Base64) |

---

## 📂 Project Directory Structure

```text
PersonalExpense tracker/
├── app.py                 # Flask web application entry point and routes
├── config.py              # Configuration loader for environment variables
├── database.py            # MySQL database connection, queries, and CRUD helpers
├── analytics.py           # Pandas, NumPy, and Matplotlib data analysis pipeline
├── init_db.py             # One-click database initialization & test script
├── schema.sql             # MySQL schema definitions + sample fictional data
├── requirements.txt       # Python dependencies list
├── .gitignore             # Git ignore file (keeps .env and caches untracked)
├── .env.example           # Example configuration template
├── README.md              # Project documentation and setup guide
├── static/
│   ├── css/
│   │   └── style.css      # Vanilla CSS styling with modern financial theme
│   └── js/
│       └── app.js         # Client-side validation, AJAX modals, print trigger
└── templates/
    ├── base.html          # Base layout with sidebar, navbar, and modals
    ├── index.html         # Dashboard overview (KPIs, charts, recent transactions)
    ├── expenses.html      # Expense ledger with date/category filters and CRUD
    ├── analytics.html     # Statistical analytics table (NumPy & Pandas)
    ├── reports.html       # Monthly expense report generator & printable view
    └── categories.html    # Category management view
```

---

## 🗄️ Database Schema

### Table 1: `categories`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `category_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique category identifier |
| `category_name` | VARCHAR(100) | NOT NULL, UNIQUE | Name of expense category |

### Table 2: `expenses`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `expense_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique expense identifier |
| `expense_date` | DATE | NOT NULL | Date when the expense occurred |
| `category_id` | INT | FOREIGN KEY (`category_id`) | Category classification reference |
| `amount` | DECIMAL(10, 2) | NOT NULL, CHECK (`amount` > 0) | Monetary amount spent |
| `description` | VARCHAR(255) | NOT NULL | Short note / purpose of expense |
| `payment_method` | VARCHAR(50) | NOT NULL | e.g. UPI, Cash, Credit Card, Debit Card |

---

## 🚀 Step-by-Step Setup Guide

### 1. Prerequisites
- **Python 3.9+** installed on your computer.
- **MySQL Server** (via MySQL Community Server, MySQL Workbench, or XAMPP / WampServer).

---

### 2. Install Python Dependencies
Open your terminal or command prompt inside the project folder:
```bash
cd "PersonalExpense tracker"
pip install -r requirements.txt
```

---

### 3. Configure Database Settings (`.env`)
Copy `.env.example` to `.env` (or edit the existing `.env`):
```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=expense_tracker_db

# Flask Application Secret Key
SECRET_KEY=your_secure_random_flask_secret_key_here
```
> **Security Note:** Never commit your `.env` file to version control. The included `.gitignore` file automatically ensures `.env` stays private on your local machine.

---

### 4. Initialize Database & Load Sample Data

#### Option A: One-click Python script (Recommended)
Simply run:
```bash
python init_db.py
```
This script will connect to your database, create the tables, and insert 30 fictional expense records across various categories and months.

#### Option B: Via MySQL Command Line or Workbench
You can also run the SQL commands directly from `schema.sql`:
```bash
mysql -u root -p < schema.sql
```

---

### 5. Run the Flask Web Application
Start the Flask development server:
```bash
python app.py
```

You should see output similar to:
```text
[*] Starting Personal Expense Tracking and Analysis System on http://127.0.0.1:5000 ...
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Testing Acceptance Criteria

1. **Add an Expense:** Click `+ Add Expense` in the top bar. Try entering a negative number or `0` — notice the client and server validation stops it and enforces positive values. Enter a valid expense (e.g. `250.00`) and verify it appears in the ledger.
2. **Edit & Delete:** In the Expenses Ledger, click the pencil icon to edit an expense via the pop-up modal. Click the trash icon to test deletion with a confirmation prompt.
3. **Date & Category Filters:** Go to **Expenses Ledger**, select a date range (e.g. from `2026-09-01` to `2026-09-30`) or pick `Food & Dining`. Click **Apply Filters**. Verify the **Filtered Total** and matching records update accurately.
4. **Data Analytics:** Navigate to **Data Analytics** to inspect the **NumPy** statistics table (`np.mean`, `np.median`, `np.std`, `np.min`, `np.max`) and the **Pandas** category breakdown table.
5. **Matplotlib Visualizations:** Review the Category Donut/Pie Chart and Monthly Bar Chart on both the Dashboard and the Data Analytics tab.
6. **Monthly Reports:** Click **Monthly Reports**, pick a month (e.g. `2026-10`), and inspect the itemized ledger and category breakdown. Click **Print / Export Statement** to open a print-ready view.
7. **Empty Data Handling:** If all expenses are deleted or no records match a filter, clean, graceful empty state cards appear instead of server errors.

---

## 📚 Academic Submission Notes
- **Independent Project:** Developed strictly within academic scope without third-party payment gateways, banking APIs, or authentication overhead.
- **Data Integrity:** Strict decimal formatting (`DECIMAL(10,2)` in MySQL, `float` rounded to 2 places in Python) guarantees no fractional currency drift.
- **Code Readability:** Every file contains clear docstrings and comments explaining how backend routes interact with the analytical libraries.
