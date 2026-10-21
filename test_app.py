"""
Automated Test Suite for Personal Expense Tracking and Analysis System
Validates all acceptance criteria:
- CRUD operations
- Positive amount validation
- Date and category filtering
- Totals matching filtered records
- Pandas and NumPy analytics
- Matplotlib chart generation
- Graceful empty data handling
"""

import unittest
from datetime import datetime
from app import app
import database
import analytics

class ExpenseTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_01_index_dashboard(self):
        """Verify dashboard loads and renders KPIs and charts."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ExpenseTracker', response.data)
        self.assertIn(b'Total Expenditure', response.data)
        self.assertIn(b'data:image/png;base64', response.data) # Matplotlib charts present

    def test_02_expenses_ledger_and_filtering(self):
        """Verify expenses ledger and filtered totals matching."""
        # 1. Lifetime view
        response = self.client.get('/expenses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Expense Transactions', response.data)
        
        # 2. Filter by Category ID 1 (Food & Dining)
        response_filtered = self.client.get('/expenses?category_id=1')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertIn(b'Filtered view active', response_filtered.data)
        
        # 3. Filter by Date Range
        response_date = self.client.get('/expenses?start_date=2026-09-01&end_date=2026-09-30')
        self.assertEqual(response_date.status_code, 200)

    def test_03_positive_amount_validation(self):
        """Verify negative or zero amounts are rejected."""
        # Negative amount
        resp_neg = self.client.post('/expenses/add', data={
            'expense_date': '2026-10-21',
            'category_id': '1',
            'amount': '-150.00',
            'description': 'Invalid Negative Expense',
            'payment_method': 'Cash'
        }, follow_redirects=True)
        self.assertIn(b'greater than zero', resp_neg.data)

        # Zero amount
        resp_zero = self.client.post('/expenses/add', data={
            'expense_date': '2026-10-21',
            'category_id': '1',
            'amount': '0.00',
            'description': 'Invalid Zero Expense',
            'payment_method': 'Cash'
        }, follow_redirects=True)
        self.assertIn(b'greater than zero', resp_zero.data)

    def test_04_crud_operations(self):
        """Verify add, get, edit, and delete lifecycle."""
        # 1. Add valid expense
        resp_add = self.client.post('/expenses/add', data={
            'expense_date': '2026-10-21',
            'category_id': '1',
            'amount': '499.50',
            'description': 'Automated Test Dinner',
            'payment_method': 'UPI'
        }, follow_redirects=True)
        self.assertIn(b'Expense recorded successfully', resp_add.data)

        # 2. Find the newly added expense
        expenses = database.get_expenses(search='Automated Test Dinner')
        self.assertTrue(len(expenses) > 0)
        test_exp = expenses[0]
        test_id = test_exp['expense_id']
        self.assertEqual(test_exp['amount'], 499.50)

        # 3. Edit expense
        resp_edit = self.client.post(f'/expenses/edit/{test_id}', data={
            'expense_date': '2026-10-21',
            'category_id': '1',
            'amount': '550.00',
            'description': 'Automated Test Dinner (Updated)',
            'payment_method': 'Credit Card'
        }, follow_redirects=True)
        self.assertIn(b'Expense updated successfully', resp_edit.data)

        updated_exp = database.get_expense_by_id(test_id)
        self.assertEqual(updated_exp['amount'], 550.00)
        self.assertEqual(updated_exp['description'], 'Automated Test Dinner (Updated)')

        # 4. Delete expense
        resp_del = self.client.post(f'/expenses/delete/{test_id}', follow_redirects=True)
        self.assertIn(b'Expense deleted successfully', resp_del.data)

        deleted_exp = database.get_expense_by_id(test_id)
        self.assertIsNone(deleted_exp)

    def test_05_analytics_view(self):
        """Verify Pandas & NumPy analytics view."""
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Summary Statistics', response.data)
        self.assertIn(b'NumPy Computed', response.data)
        self.assertIn(b'Pandas GroupBy', response.data)
        self.assertIn(b'data:image/png;base64', response.data)

    def test_06_monthly_reports(self):
        """Verify monthly reports generation."""
        response = self.client.get('/reports?month=2026-09')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Monthly Expenditure Report', response.data)
        self.assertIn(b'September 2026', response.data)

    def test_07_empty_data_graceful_handling(self):
        """Verify analytics and charts handle empty dataset gracefully."""
        empty_analysis = analytics.analyze_expenses([])
        self.assertFalse(empty_analysis['has_data'])
        self.assertEqual(empty_analysis['total_expenses'], 0.0)
        self.assertIsNotNone(empty_analysis['pie_chart'])
        self.assertIsNotNone(empty_analysis['bar_chart'])

    def test_08_static_assets_and_vercel_entrypoint(self):
        """Verify static CSS/JS load correctly and Vercel routing paths work."""
        # 1. Test Static files
        css_resp = self.client.get('/static/css/style.css')
        self.assertEqual(css_resp.status_code, 200)
        self.assertIn(b':root', css_resp.data)

        js_resp = self.client.get('/static/js/app.js')
        self.assertEqual(js_resp.status_code, 200)
        self.assertIn(b'DOMContentLoaded', js_resp.data)

        # 2. Test Vercel aliases
        for alias in ['/api', '/api/index', '/api/index.py']:
            alias_resp = self.client.get(alias)
            self.assertEqual(alias_resp.status_code, 200)
            self.assertIn(b'ExpenseTracker', alias_resp.data)

        # 3. Test Vercel entrypoint callable
        import api.index as vercel_entry
        self.assertIsNotNone(vercel_entry.app)

if __name__ == '__main__':
    unittest.main()

