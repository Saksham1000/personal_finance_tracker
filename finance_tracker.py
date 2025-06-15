#!/usr/bin/env python3
"""
Personal Finance Tracker with Data Analytics Dashboard

A comprehensive financial management application that demonstrates:
- Object-oriented programming
- Data persistence with SQLite
- Data visualization with matplotlib and seaborn
- API integration
- Error handling and logging
- Clean code practices

Author: Saksham Lamsal
Date: June 2025
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    """Data class for financial transactions"""
    id: Optional[int]
    date: str
    category: str
    description: str
    amount: float
    transaction_type: str  # 'income' or 'expense'
    
class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, db_path: str = "finance_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT UNIQUE NOT NULL,
                    monthly_limit REAL NOT NULL,
                    created_date TEXT NOT NULL
                )
            """)
            conn.commit()
        logger.info("Database initialized successfully")
    
    def add_transaction(self, transaction: Transaction) -> int:
        """Add a new transaction to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (date, category, description, amount, transaction_type)
                VALUES (?, ?, ?, ?, ?)
            """, (transaction.date, transaction.category, transaction.description, 
                  transaction.amount, transaction.transaction_type))
            conn.commit()
            transaction_id = cursor.lastrowid
        logger.info(f"Transaction added with ID: {transaction_id}")
        return transaction_id
    
    def get_transactions(self, start_date: str = None, end_date: str = None) -> List[Transaction]:
        """Retrieve transactions from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute("""
                    SELECT * FROM transactions 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                """, (start_date, end_date))
            else:
                cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
            
            rows = cursor.fetchall()
            return [Transaction(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
    
    def set_budget(self, category: str, monthly_limit: float):
        """Set or update budget for a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO budgets (category, monthly_limit, created_date)
                VALUES (?, ?, ?)
            """, (category, monthly_limit, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
        logger.info(f"Budget set for {category}: ${monthly_limit}")
    
    def get_budgets(self) -> Dict[str, float]:
        """Get all budget limits"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, monthly_limit FROM budgets")
            return dict(cursor.fetchall())

class FinanceAnalyzer:
    """Handles financial data analysis and visualization"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def generate_summary_report(self, months: int = 3) -> Dict:
        """Generate a comprehensive financial summary"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        transactions = self.db_manager.get_transactions(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if not transactions:
            return {"message": "No transactions found for the specified period"}
        
        df = pd.DataFrame([
            {
                'date': t.date,
                'category': t.category,
                'amount': t.amount,
                'type': t.transaction_type
            } for t in transactions
        ])
        
        df['date'] = pd.to_datetime(df['date'])
        
        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expenses = df[df['type'] == 'expense']['amount'].sum()
        net_savings = total_income - total_expenses
        
        # Category-wise analysis
        expense_by_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum().to_dict()
        income_by_category = df[df['type'] == 'income'].groupby('category')['amount'].sum().to_dict()
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'savings_rate': (net_savings / total_income * 100) if total_income > 0 else 0,
            'expense_by_category': expense_by_category,
            'income_by_category': income_by_category,
            'transaction_count': len(transactions)
        }
    
    def create_expense_pie_chart(self, save_path: str = "expense_breakdown.png"):
        """Create a pie chart showing expense breakdown by category"""
        transactions = self.db_manager.get_transactions()
        expenses = [t for t in transactions if t.transaction_type == 'expense']
        
        if not expenses:
            print("No expense data available for visualization")
            return
        
        df = pd.DataFrame([{
            'category': t.category,
            'amount': t.amount
        } for t in expenses])
        
        category_totals = df.groupby('category')['amount'].sum()
        
        plt.figure(figsize=(10, 8))
        plt.pie(category_totals.values, labels=category_totals.index, autopct='%1.1f%%')
        plt.title('Expense Breakdown by Category', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        logger.info(f"Expense pie chart saved to {save_path}")
    
    def create_monthly_trend_chart(self, save_path: str = "monthly_trends.png"):
        """Create a line chart showing monthly income vs expenses"""
        transactions = self.db_manager.get_transactions()
        
        if not transactions:
            print("No transaction data available for visualization")
            return
        
        df = pd.DataFrame([{
            'date': t.date,
            'amount': t.amount,
            'type': t.transaction_type
        } for t in transactions])
        
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        monthly_data = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        
        plt.figure(figsize=(12, 6))
        if 'income' in monthly_data.columns:
            plt.plot(monthly_data.index.astype(str), monthly_data['income'], 
                    marker='o', label='Income', linewidth=2)
        if 'expense' in monthly_data.columns:
            plt.plot(monthly_data.index.astype(str), monthly_data['expense'], 
                    marker='s', label='Expenses', linewidth=2)
        
        plt.title('Monthly Income vs Expenses Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Amount (NPR)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        logger.info(f"Monthly trend chart saved to {save_path}")
    
    def check_budget_status(self) -> Dict:
        """Check current spending against budget limits"""
        budgets = self.db_manager.get_budgets()
        if not budgets:
            return {"message": "No budgets set"}
        
        current_month = datetime.now().strftime('%Y-%m')
        transactions = self.db_manager.get_transactions(
            f"{current_month}-01",
            f"{current_month}-31"
        )
        
        expenses = [t for t in transactions if t.transaction_type == 'expense']
        spending_by_category = {}
        
        for expense in expenses:
            category = expense.category
            spending_by_category[category] = spending_by_category.get(category, 0) + expense.amount
        
        budget_status = {}
        for category, limit in budgets.items():
            spent = spending_by_category.get(category, 0)
            remaining = limit - spent
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            budget_status[category] = {
                'budget': limit,
                'spent': spent,
                'remaining': remaining,
                'percentage_used': percentage,
                'status': 'over' if remaining < 0 else 'warning' if percentage > 80 else 'good'
            }
        
        return budget_status

class CurrencyConverter:
    """Handle currency conversion using free API"""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert amount from one currency to another"""
        try:
            response = requests.get(f"{self.base_url}{from_currency}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if to_currency in data['rates']:
                    rate = data['rates'][to_currency]
                    converted_amount = amount * rate
                    logger.info(f"Converted {amount} {from_currency} to {converted_amount:.2f} {to_currency}")
                    return converted_amount
            return None
        except requests.RequestException as e:
            logger.error(f"Currency conversion failed: {e}")
            return None

class FinanceTracker:
    """Main application class that ties everything together"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.analyzer = FinanceAnalyzer(self.db_manager)
        self.currency_converter = CurrencyConverter()
        logger.info("Finance Tracker initialized")
    
    def add_transaction(self, date: str, category: str, description: str, 
                      amount: float, transaction_type: str):
        """Add a new transaction"""
        transaction = Transaction(None, date, category, description, amount, transaction_type)
        return self.db_manager.add_transaction(transaction)
    
    def get_summary(self, months: int = 3) -> Dict:
        """Get financial summary"""
        return self.analyzer.generate_summary_report(months)
    
    def create_visualizations(self):
        """Generate all visualization charts"""
        self.analyzer.create_expense_pie_chart()
        self.analyzer.create_monthly_trend_chart()
    
    def set_budget(self, category: str, amount: float):
        """Set budget for a category"""
        self.db_manager.set_budget(category, amount)
    
    def check_budgets(self) -> Dict:
        """Check budget status"""
        return self.analyzer.check_budget_status()
    
    def export_data(self, filename: str = "financial_data.csv"):
        """Export all transactions to CSV"""
        transactions = self.db_manager.get_transactions()
        
        data = []
        for t in transactions:
            data.append({
                'Date': t.date,
                'Category': t.category,
                'Description': t.description,
                'Amount': t.amount,
                'Type': t.transaction_type
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Data exported to {filename}")
        return filename

def demo_application():
    """Demonstrate the application with sample data"""
    print("=" * 60)
    print("PERSONAL FINANCE TRACKER - DEMO")
    print("=" * 60)
    
    # Initialize the tracker
    tracker = FinanceTracker()
    
    # Add sample transactions
    sample_transactions = [
        ("2025-06-01", "Salary", "Monthly salary", 3500, "income"),
        ("2025-06-02", "Groceries", "Weekly grocery shopping", 120, "expense"),
        ("2025-06-03", "Transportation", "Gas for car", 45, "expense"),
        ("2025-06-05", "Entertainment", "Movie tickets", 25, "expense"),
        ("2025-06-07", "Utilities", "Electricity bill", 85, "expense"),
        ("2025-06-10", "Freelance", "Web design project", 500, "income"),
        ("2025-06-12", "Groceries", "Grocery shopping", 95, "expense"),
        ("2025-06-13", "Healthcare", "Doctor visit", 75, "expense"),
    ]
    
    print("Adding sample transactions...")
    for transaction in sample_transactions:
        tracker.add_transaction(*transaction)
    
    # Set some budgets
    print("\nSetting budgets...")
    tracker.set_budget("Groceries", 300)
    tracker.set_budget("Transportation", 150)
    tracker.set_budget("Entertainment", 100)
    tracker.set_budget("Utilities", 200)
    
    # Generate summary
    print("\n" + "=" * 40)
    print("FINANCIAL SUMMARY")
    print("=" * 40)
    summary = tracker.get_summary(1)
    print(f"Period: {summary['period']}")
    print(f"Total Income: ${summary['total_income']:.2f}")
    print(f"Total Expenses: ${summary['total_expenses']:.2f}")
    print(f"Net Savings: ${summary['net_savings']:.2f}")
    print(f"Savings Rate: {summary['savings_rate']:.1f}%")
    
    # Check budgets
    print("\n" + "=" * 40)
    print("BUDGET STATUS")
    print("=" * 40)
    budget_status = tracker.check_budgets()
    for category, status in budget_status.items():
        print(f"{category}:")
        print(f"  Budget: ${status['budget']:.2f}")
        print(f"  Spent: ${status['spent']:.2f}")
        print(f"  Remaining: ${status['remaining']:.2f}")
        print(f"  Status: {status['status'].upper()}")
        print()
    
    # Create visualizations
    print("Creating visualizations...")
    tracker.create_visualizations()
    
    # Export data
    print("Exporting data...")
    csv_file = tracker.export_data()
    print(f"Data exported to {csv_file}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED!")
    print("Check the generated charts and CSV file.")
    print("=" * 60)

if __name__ == "__main__":
    demo_application()

