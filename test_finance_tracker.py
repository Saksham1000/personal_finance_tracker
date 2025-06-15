#!/usr/bin/env python3
"""
Unit Tests for Personal Finance Tracker

This module contains comprehensive tests for all components of the finance tracker,
demonstrating test-driven development practices and ensuring code reliability.
"""

import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from finance_tracker import (
    Transaction, DatabaseManager, FinanceAnalyzer, 
    CurrencyConverter, FinanceTracker
)

class TestTransaction(unittest.TestCase):
    """Test the Transaction data class"""
    
    def test_transaction_creation(self):
        """Test creating a transaction object"""
        transaction = Transaction(
            id=1,
            date="2025-06-13",
            category="Groceries",
            description="Weekly shopping",
            amount=125.50,
            transaction_type="expense"
        )
        
        self.assertEqual(transaction.id, 1)
        self.assertEqual(transaction.date, "2025-06-13")
        self.assertEqual(transaction.category, "Groceries")
        self.assertEqual(transaction.description, "Weekly shopping")
        self.assertEqual(transaction.amount, 125.50)
        self.assertEqual(transaction.transaction_type, "expense")

class TestDatabaseManager(unittest.TestCase):
    """Test the DatabaseManager class"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.db_manager = DatabaseManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_file.name)
    
    def test_database_initialization(self):
        """Test that database tables are created correctly"""
        # Database should be initialized in setUp
        transactions = self.db_manager.get_transactions()
        budgets = self.db_manager.get_budgets()
        
        self.assertEqual(len(transactions), 0)
        self.assertEqual(len(budgets), 0)
    
    def test_add_transaction(self):
        """Test adding a transaction to the database"""
        transaction = Transaction(
            id=None,
            date="2025-06-13",
            category="Groceries",
            description="Test transaction",
            amount=100.0,
            transaction_type="expense"
        )
        
        transaction_id = self.db_manager.add_transaction(transaction)
        self.assertIsInstance(transaction_id, int)
        self.assertGreater(transaction_id, 0)
        
        # Verify transaction was added
        transactions = self.db_manager.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].description, "Test transaction")
    
    def test_set_and_get_budget(self):
        """Test setting and retrieving budgets"""
        self.db_manager.set_budget("Groceries", 300.0)
        self.db_manager.set_budget("Transportation", 150.0)
        
        budgets = self.db_manager.get_budgets()
        
        self.assertEqual(len(budgets), 2)
        self.assertEqual(budgets["Groceries"], 300.0)
        self.assertEqual(budgets["Transportation"], 150.0)
    
    def test_get_transactions_with_date_range(self):
        """Test filtering transactions by date range"""
        # Add transactions with different dates
        transaction1 = Transaction(None, "2025-06-01", "Food", "Lunch", 15.0, "expense")
        transaction2 = Transaction(None, "2025-06-15", "Food", "Dinner", 25.0, "expense")
        transaction3 = Transaction(None, "2025-07-01", "Food", "Breakfast", 10.0, "expense")
        
        self.db_manager.add_transaction(transaction1)
        self.db_manager.add_transaction(transaction2)
        self.db_manager.add_transaction(transaction3)
        
        # Filter transactions for June 2025
        june_transactions = self.db_manager.get_transactions("2025-06-01", "2025-06-30")
        
        self.assertEqual(len(june_transactions), 2)
        descriptions = [t.description for t in june_transactions]
        self.assertIn("Lunch", descriptions)
        self.assertIn("Dinner", descriptions)
        self.assertNotIn("Breakfast", descriptions)

class TestFinanceAnalyzer(unittest.TestCase):
    """Test the FinanceAnalyzer class"""
    
    def setUp(self):
        """Set up test database and analyzer"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.db_manager = DatabaseManager(self.temp_file.name)
        self.analyzer = FinanceAnalyzer(self.db_manager)
        
        # Add sample data
        self._add_sample_data()
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_file.name)
    
    def _add_sample_data(self):
        """Add sample transactions for testing"""
        transactions = [
            Transaction(None, "2025-06-01", "Salary", "Monthly salary", 3000, "income"),
            Transaction(None, "2025-06-02", "Groceries", "Weekly shopping", 150, "expense"),
            Transaction(None, "2025-06-03", "Transportation", "Gas", 50, "expense"),
            Transaction(None, "2025-06-10", "Freelance", "Side project", 500, "income"),
        ]
        
        for transaction in transactions:
            self.db_manager.add_transaction(transaction)
    
    def test_generate_summary_report(self):
        """Test generating financial summary report"""
        summary = self.analyzer.generate_summary_report(months=1)
        
        self.assertIn('total_income', summary)
        self.assertIn('total_expenses', summary)
        self.assertIn('net_savings', summary)
        self.assertIn('savings_rate', summary)
        
        self.assertEqual(summary['total_income'], 3500)  # 3000 + 500
        self.assertEqual(summary['total_expenses'], 200)  # 150 + 50
        self.assertEqual(summary['net_savings'], 3300)  # 3500 - 200
        self.assertAlmostEqual(summary['savings_rate'], 94.29, places=1)  # 3300/3500 * 100
    
    def test_check_budget_status(self):
        """Test budget status checking"""
        # Set budgets
        self.db_manager.set_budget("Groceries", 200.0)
        self.db_manager.set_budget("Transportation", 100.0)
        
        budget_status = self.analyzer.check_budget_status()
        
        self.assertIn("Groceries", budget_status)
        self.assertIn("Transportation", budget_status)
        
        groceries_status = budget_status["Groceries"]
        self.assertEqual(groceries_status['budget'], 200.0)
        self.assertEqual(groceries_status['spent'], 150.0)
        self.assertEqual(groceries_status['remaining'], 50.0)
        self.assertEqual(groceries_status['status'], 'good')
        
        transport_status = budget_status["Transportation"]
        self.assertEqual(transport_status['budget'], 100.0)
        self.assertEqual(transport_status['spent'], 50.0)
        self.assertEqual(transport_status['remaining'], 50.0)
        self.assertEqual(transport_status['status'], 'good')

class TestCurrencyConverter(unittest.TestCase):
    """Test the CurrencyConverter class"""
    
    def setUp(self):
        """Set up currency converter"""
        self.converter = CurrencyConverter()
    
    @patch('requests.get')
    def test_successful_currency_conversion(self, mock_get):
        """Test successful currency conversion"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {
                'EUR': 0.85,
                'GBP': 0.75
            }
        }
        mock_get.return_value = mock_response
        
        result = self.converter.convert_currency(100, 'USD', 'EUR')
        
        self.assertEqual(result, 85.0)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_failed_currency_conversion(self, mock_get):
        """Test failed currency conversion"""
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.converter.convert_currency(100, 'USD', 'EUR')
        
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_currency_conversion_timeout(self, mock_get):
        """Test currency conversion with network timeout"""
        # Mock network timeout
        mock_get.side_effect = Exception("Timeout")
        
        result = self.converter.convert_currency(100, 'USD', 'EUR')
        
        self.assertIsNone(result)

class TestFinanceTracker(unittest.TestCase):
    """Test the main FinanceTracker class"""
    
    def setUp(self):
        """Set up finance tracker with temporary database"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Patch DatabaseManager to use our temp file
        with patch('finance_tracker.DatabaseManager') as mock_db_manager:
            mock_db_manager.return_value = DatabaseManager(self.temp_file.name)
            self.tracker = FinanceTracker()
            self.tracker.db_manager = DatabaseManager(self.temp_file.name)
            self.tracker.analyzer = FinanceAnalyzer(self.tracker.db_manager)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_file.name)
    
    def test_add_transaction_integration(self):
        """Test adding transaction through main interface"""
        transaction_id = self.tracker.add_transaction(
            date="2025-06-13",
            category="Food",
            description="Lunch",
            amount=15.0,
            transaction_type="expense"
        )
        
        self.assertIsInstance(transaction_id, int)
        
        # Verify transaction was added by getting summary
        summary = self.tracker.get_summary(months=1)
        self.assertEqual(summary['total_expenses'], 15.0)
    
    def test_set_budget_integration(self):
        """Test setting budget through main interface"""
        self.tracker.set_budget("Food", 200.0)
        
        # Add a transaction and check budget status
        self.tracker.add_transaction(
            date="2025-06-13",
            category="Food",
            description="Lunch",
            amount=50.0,
            transaction_type="expense"
        )
        
        budget_status = self.tracker.check_budgets()
        
        self.assertIn("Food", budget_status)
        self.assertEqual(budget_status["Food"]["budget"], 200.0)
        self.assertEqual(budget_status["Food"]["spent"], 50.0)
    
    def test_export_data(self):
        """Test data export functionality"""
        # Add some test data
        self.tracker.add_transaction(
            date="2025-06-13",
            category="Food",
            description="Test transaction",
            amount=25.0,
            transaction_type="expense"
        )
        
        # Export data
        temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_csv.close()
        
        try:
            filename = self.tracker.export_data(temp_csv.name)
            self.assertEqual(filename, temp_csv.name)
            
            # Verify file exists and has content
            self.assertTrue(os.path.exists(filename))
            
            with open(filename, 'r') as f:
                content = f.read()
                self.assertIn("Test transaction", content)
                self.assertIn("Food", content)
        
        finally:
            os.unlink(temp_csv.name)

class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.db_manager = DatabaseManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_file.name)
    
    def test_negative_amounts(self):
        """Test handling of negative amounts"""
        transaction = Transaction(
            id=None,
            date="2025-06-13",
            category="Refund",
            description="Return item",
            amount=-25.0,
            transaction_type="expense"
        )
        
        transaction_id = self.db_manager.add_transaction(transaction)
        self.assertIsInstance(transaction_id, int)
        
        transactions = self.db_manager.get_transactions()
        self.assertEqual(transactions[0].amount, -25.0)
    
    def test_zero_amounts(self):
        """Test handling of zero amounts"""
        transaction = Transaction(
            id=None,
            date="2025-06-13",
            category="Free",
            description="Free item",
            amount=0.0,
            transaction_type="expense"
        )
        
        transaction_id = self.db_manager.add_transaction(transaction)
        self.assertIsInstance(transaction_id, int)
    
    def test_empty_category_descriptions(self):
        """Test handling of empty strings"""
        transaction = Transaction(
            id=None,
            date="2025-06-13",
            category="",
            description="",
            amount=10.0,
            transaction_type="expense"
        )
        
        # Should still work even with empty strings
        transaction_id = self.db_manager.add_transaction(transaction)
        self.assertIsInstance(transaction_id, int)

if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)

