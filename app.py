"""
Personal Expense Tracking and Analysis System
Flask Web Application Main Entry Point
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
import database
import analytics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static'
)
app.config.from_object(Config)

# Initialize database schema safely at startup (resilient to serverless cold starts)
try:
    with app.app_context():
        database.init_db()
except Exception as e:
    print(f"[INFO] Initial database connection check deferred: {e}")


@app.context_processor
def inject_global_data():
    """Inject common metadata and categories into all templates."""
    try:
        categories_list = database.get_categories()
    except Exception:
        categories_list = []
    return {
        'current_year': datetime.now().year,
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'db_status': database.get_database_status(),
        'categories': categories_list
    }


# --------------------------------------------------------------------
# 1. Dashboard (Index)
# --------------------------------------------------------------------
@app.route('/')
@app.route('/index')
@app.route('/api')
@app.route('/api/index')
@app.route('/api/index.py')
def index():
    """
    Main dashboard displaying summary KPI cards, Matplotlib charts,
    and recent expense records.
    """
    categories = database.get_categories()
    all_expenses = database.get_expenses()
    
    # Run Pandas/NumPy analytics pipeline
    analysis = analytics.analyze_expenses(all_expenses)
    
    # Calculate current month's spending
    current_month_str = datetime.now().strftime('%Y-%m')
    current_month_total = 0.0
    for m in analysis['monthly_totals']:
        if m['month_year'] == current_month_str:
            current_month_total = m['total_amount']
            break
            
    # Recent 7 expenses
    recent_expenses = all_expenses[:7] if all_expenses else []
    
    return render_template(
        'index.html',
        categories=categories,
        total_expenses=analysis['total_expenses'],
        current_month_total=current_month_total,
        transaction_count=analysis['transaction_count'],
        highest_category=analysis['highest_category'],
        summary_stats=analysis['summary_stats'],
        category_breakdown=analysis['category_breakdown'][:5],
        recent_expenses=recent_expenses,
        pie_chart=analysis['pie_chart'],
        bar_chart=analysis['bar_chart'],
        has_data=analysis['has_data']
    )

# --------------------------------------------------------------------
# 2. Expenses Management (CRUD & Filters)
# --------------------------------------------------------------------
@app.route('/expenses')
def expenses_list():
    """
    List expenses with date range and category filters.
    Computes exact totals that match the filtered records.
    """
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    category_id = request.args.get('category_id', '').strip()
    search = request.args.get('search', '').strip()
    
    categories = database.get_categories()
    filtered_expenses = database.get_expenses(
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        category_id=category_id if category_id else None,
        search=search if search else None
    )
    
    # Compute totals for filtered records (Acceptance Criteria)
    filtered_total = sum(exp['amount'] for exp in filtered_expenses)
    filtered_count = len(filtered_expenses)
    filtered_avg = (filtered_total / filtered_count) if filtered_count > 0 else 0.0
    
    return render_template(
        'expenses.html',
        expenses=filtered_expenses,
        categories=categories,
        filtered_total=round(filtered_total, 2),
        filtered_count=filtered_count,
        filtered_avg=round(filtered_avg, 2),
        start_date=start_date,
        end_date=end_date,
        selected_category=int(category_id) if category_id and category_id.isdigit() else '',
        search=search
    )

@app.route('/expenses/add', methods=['POST'])
def add_expense():
    """Record a new expense."""
    expense_date = request.form.get('expense_date')
    category_id = request.form.get('category_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    payment_method = request.form.get('payment_method', 'Cash')
    
    success, msg = database.add_expense(
        expense_date=expense_date,
        category_id=category_id,
        amount=amount,
        description=description,
        payment_method=payment_method
    )
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
        
    redirect_target = request.referrer or url_for('expenses_list')
    return redirect(redirect_target)

@app.route('/expenses/edit/<int:expense_id>', methods=['POST'])
def edit_expense(expense_id):
    """Update an existing expense."""
    expense_date = request.form.get('expense_date')
    category_id = request.form.get('category_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    payment_method = request.form.get('payment_method')
    
    success, msg = database.update_expense(
        expense_id=expense_id,
        expense_date=expense_date,
        category_id=category_id,
        amount=amount,
        description=description,
        payment_method=payment_method
    )
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
        
    return redirect(url_for('expenses_list'))

@app.route('/expenses/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    """Delete an expense record."""
    success, msg = database.delete_expense(expense_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('expenses_list'))

# --------------------------------------------------------------------
# 3. Analytics & Visualizations (Pandas, NumPy, Matplotlib)
# --------------------------------------------------------------------
@app.route('/analytics')
def analytics_view():
    """
    Dedicated Data Analysis view highlighting:
    - NumPy summary statistics table
    - Pandas category breakdown table with percentages
    - Pandas monthly aggregation
    - Payment methods distribution
    - Full-sized Matplotlib charts
    """
    all_expenses = database.get_expenses()
    analysis = analytics.analyze_expenses(all_expenses)
    
    return render_template(
        'analytics.html',
        analysis=analysis
    )

# --------------------------------------------------------------------
# 4. Monthly Expense Reports
# --------------------------------------------------------------------
@app.route('/reports')
def monthly_reports():
    """
    Generate and inspect monthly expense reports:
    - Selectable month dropdown
    - Monthly total, daily average, and highest category
    - Category percentage breakdown
    - Complete transaction ledger for that month
    - Printable report layout
    """
    all_expenses = database.get_expenses()
    analysis = analytics.analyze_expenses(all_expenses)
    
    # Available months list
    available_months = [m['month_year'] for m in analysis['monthly_totals']]
    # Sort reverse chronological
    available_months.reverse()
    
    selected_month = request.args.get('month', '').strip()
    if not selected_month and available_months:
        selected_month = available_months[0]
        
    report_data = None
    if selected_month:
        report_data = analytics.generate_monthly_report_analysis(all_expenses, selected_month)
        
    return render_template(
        'reports.html',
        available_months=available_months,
        selected_month=selected_month,
        report=report_data
    )

# --------------------------------------------------------------------
# 5. Category Management
# --------------------------------------------------------------------
@app.route('/categories')
def categories_view():
    """Manage categories: list, add, delete."""
    categories = database.get_categories()
    all_expenses = database.get_expenses()
    
    # Count expenses in each category
    counts = {}
    totals = {}
    for exp in all_expenses:
        cid = exp['category_id']
        counts[cid] = counts.get(cid, 0) + 1
        totals[cid] = totals.get(cid, 0.0) + exp['amount']
        
    for cat in categories:
        cat['expense_count'] = counts.get(cat['category_id'], 0)
        cat['total_amount'] = round(totals.get(cat['category_id'], 0.0), 2)
        
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
def add_category():
    """Add a new expense category."""
    category_name = request.form.get('category_name', '')
    success, msg = database.add_category(category_name)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('categories_view'))

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    """Delete a category if no expenses are linked."""
    success, msg = database.delete_category(category_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('categories_view'))

# --------------------------------------------------------------------
# 6. JSON API Endpoints for UI / Modals
# --------------------------------------------------------------------
@app.route('/api/expenses/<int:expense_id>')
def api_get_expense(expense_id):
    """Returns single expense details in JSON format for the Edit modal."""
    expense = database.get_expense_by_id(expense_id)
    if expense:
        return jsonify({'success': True, 'expense': expense})
    return jsonify({'success': False, 'message': 'Expense not found'}), 404

if __name__ == '__main__':
    print("[*] Starting Personal Expense Tracking and Analysis System on http://127.0.0.1:5000 ...")
    app.run(debug=True, host='127.0.0.1', port=5000)
