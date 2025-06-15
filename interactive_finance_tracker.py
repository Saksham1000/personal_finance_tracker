#!/usr/bin/env python3
"""
Interactive Personal Finance Tracker

A user-friendly command-line interface for managing personal finances with
real-time input, budget tracking, and comprehensive reporting.

Author: [Your Name]

"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass
from finance_tracker import (
    Transaction, DatabaseManager, FinanceAnalyzer, 
    CurrencyConverter, FinanceTracker
)

class InteractiveFinanceTracker:
    """Interactive command-line interface for the finance tracker"""
    
    def __init__(self):
        self.tracker = FinanceTracker()
        self.running = True
        
        # Nepal-specific categories for quick selection
        self.expense_categories = [
            "Groceries/Food", "Transportation", "Entertainment", "Electricity/Water", 
            "Healthcare/Medicine", "Shopping/Clothes", "Dining Out", "Rent/House", 
            "Mobile/Internet", "Education/Books", "Festival/Religious", "Travel", "Other"
        ]
        
        self.income_categories = [
            "Salary/Job", "Business/Shop", "Investment", "Gift/Dashain", "Bonus", 
            "Freelance/Part-time", "Remittance", "Other"
        ]
        
        print("\n" + "="*70)
        print("🏦 PERSONAL FINANCE TRACKER - NEPAL EDITION 🏦")
        print("="*70)
        print("🇳🇵 Designed for Nepal - All amounts in Nepali Rupees (NPR)")
        print("📊 Track your income, expenses, and budgets with ease!")
        print("")
    
    def display_menu(self):
        """Display the main menu options"""
        print("\n" + "="*40)
        print("📊 MAIN MENU")
        print("="*40)
        print("1. 💰 Add Income")
        print("2. 💸 Add Expense")
        print("3. 📋 View Transactions")
        print("4. 🎯 Set Budget")
        print("5. 📊 View Budget Status")
        print("6. 📈 Generate Financial Report")
        print("7. 📊 Create Visualizations")
        print("8. 💱 Currency Converter")
        print("9. 📤 Export Data")
        print("10. 🗑️  Delete Transaction")
        print("11. 🗃️  Clear All Data")
        print("12. ❌ Exit")
        print("-"*40)
    
    def get_user_input(self, prompt: str, input_type: type = str, required: bool = True) -> any:
        """Get validated user input"""
        while True:
            try:
                user_input = input(prompt).strip()
                
                if not user_input and required:
                    print("❌ This field is required. Please try again.")
                    continue
                
                if not user_input and not required:
                    return None
                
                if input_type == float:
                    value = float(user_input)
                    if value < 0:
                        print("❌ Amount cannot be negative. Please enter a positive number.")
                        continue
                    return value
                elif input_type == int:
                    return int(user_input)
                else:
                    return user_input
                    
            except ValueError:
                print(f"❌ Invalid input. Please enter a valid {input_type.__name__}.")
    
    def get_date_input(self) -> str:
        """Get date input from user with validation"""
        print("\n📅 Date Options:")
        print("1. Use today's date")
        print("2. Enter custom date (YYYY-MM-DD)")
        
        choice = self.get_user_input("Choose option (1 or 2): ", int)
        
        if choice == 1:
            return datetime.now().strftime('%Y-%m-%d')
        elif choice == 2:
            while True:
                date_str = self.get_user_input("Enter date (YYYY-MM-DD): ")
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    return date_str
                except ValueError:
                    print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-06-13)")
        else:
            print("❌ Invalid choice. Using today's date.")
            return datetime.now().strftime('%Y-%m-%d')
    
    def select_category(self, categories: List[str], transaction_type: str) -> str:
        """Let user select from predefined categories or enter custom"""
        print(f"\n📂 {transaction_type.title()} Categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        print(f"{len(categories) + 1}. Custom Category")
        
        while True:
            choice = self.get_user_input(f"Select category (1-{len(categories) + 1}): ", int)
            
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
            elif choice == len(categories) + 1:
                return self.get_user_input("Enter custom category: ")
            else:
                print(f"❌ Please enter a number between 1 and {len(categories) + 1}")
    
    def add_income(self):
        """Add income transaction"""
        print("\n" + "="*30)
        print("💰 ADD INCOME")
        print("="*30)
        
        date = self.get_date_input()
        category = self.select_category(self.income_categories, "income")
        description = self.get_user_input("💬 Description: ")
        amount = self.get_user_input("💵 Amount: NPR ", float)
        
        transaction_id = self.tracker.add_transaction(date, category, description, amount, "income")
        
        print(f"\n✅ Income added successfully! (ID: {transaction_id})")
        print(f"📊 Added: NPR {amount:.2f} from {category}")
    
    def add_expense(self):
        """Add expense transaction"""
        print("\n" + "="*30)
        print("💸 ADD EXPENSE")
        print("="*30)
        
        date = self.get_date_input()
        category = self.select_category(self.expense_categories, "expense")
        description = self.get_user_input("💬 Description: ")
        amount = self.get_user_input("💵 Amount: NPR ", float)
        
        transaction_id = self.tracker.add_transaction(date, category, description, amount, "expense")
        
        print(f"\n✅ Expense added successfully! (ID: {transaction_id})")
        print(f"📊 Spent: NPR {amount:.2f} on {category}")
        
        # Check budget if exists
        budget_status = self.tracker.check_budgets()
        if category in budget_status:
            status = budget_status[category]
            remaining = status['remaining']
            percentage = status['percentage_used']
            
            if remaining < 0:
                print(f"⚠️  WARNING: You've exceeded your {category} budget by NPR {abs(remaining):.2f}!")
            elif percentage > 80:
                print(f"⚠️  WARNING: You've used {percentage:.1f}% of your {category} budget!")
            else:
                print(f"💚 Budget Status: NPR {remaining:.2f} remaining in {category} ({percentage:.1f}% used)")
    
    def view_transactions(self):
        """View recent transactions"""
        print("\n" + "="*50)
        print("📋 RECENT TRANSACTIONS")
        print("="*50)
        
        print("\n📅 Time Period Options:")
        print("1. Last 7 days")
        print("2. Last 30 days")
        print("3. All transactions")
        print("4. Custom date range")
        
        choice = self.get_user_input("Choose option (1-4): ", int)
        
        if choice == 1:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            period = "Last 7 days"
        elif choice == 2:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            period = "Last 30 days"
        elif choice == 3:
            start_date = None
            end_date = None
            period = "All time"
        elif choice == 4:
            print("\nEnter date range:")
            start_date = self.get_user_input("Start date (YYYY-MM-DD): ")
            end_date = self.get_user_input("End date (YYYY-MM-DD): ")
            period = f"{start_date} to {end_date}"
        else:
            print("❌ Invalid choice. Showing last 30 days.")
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            period = "Last 30 days"
        
        transactions = self.tracker.db_manager.get_transactions(start_date, end_date)
        
        if not transactions:
            print(f"\n📭 No transactions found for {period}.")
            return
        
        print(f"\n📊 Transactions for {period}:")
        print("-" * 80)
        print(f"{'ID':<4} {'Date':<12} {'Type':<8} {'Category':<15} {'Description':<20} {'Amount':<10}")
        print("-" * 80)
        
        total_income = 0
        total_expenses = 0
        
        for t in transactions:
            amount_str = f"NPR {t.amount:.2f}"
            type_emoji = "💰" if t.transaction_type == "income" else "💸"
            
            print(f"{t.id:<4} {t.date:<12} {type_emoji}{t.transaction_type:<7} {t.category:<15} {t.description[:18]:<20} {amount_str:<10}")
            
            if t.transaction_type == "income":
                total_income += t.amount
            else:
                total_expenses += t.amount
        
        print("-" * 80)
        print(f"💰 Total Income: NPR {total_income:.2f}")
        print(f"💸 Total Expenses: NPR {total_expenses:.2f}")
        print(f"💵 Net Amount: NPR {total_income - total_expenses:.2f}")
    
    def set_budget(self):
        """Set budget for a category"""
        print("\n" + "="*30)
        print("🎯 SET BUDGET")
        print("="*30)
        
        category = self.select_category(self.expense_categories, "expense")
        amount = self.get_user_input(f"💰 Monthly budget for {category}: NPR ", float)
        
        self.tracker.set_budget(category, amount)
        
        print(f"\n✅ Budget set successfully!")
        print(f"🎯 {category}: NPR {amount:.2f} per month")
    
    def view_budget_status(self):
        """View current budget status"""
        print("\n" + "="*40)
        print("📊 BUDGET STATUS")
        print("="*40)
        
        budget_status = self.tracker.check_budgets()
        
        if not budget_status or 'message' in budget_status:
            print("\n📭 No budgets set yet.")
            print("💡 Tip: Use option 4 to set budgets for your expense categories.")
            return
        
        current_month = datetime.now().strftime('%B %Y')
        print(f"\n📅 Budget Status for {current_month}:")
        print("-" * 70)
        
        for category, status in budget_status.items():
            budget = status['budget']
            spent = status['spent']
            remaining = status['remaining']
            percentage = status['percentage_used']
            status_indicator = status['status']
            
            # Status emoji
            if status_indicator == 'over':
                emoji = "🔴"
            elif status_indicator == 'warning':
                emoji = "🟡"
            else:
                emoji = "🟢"
            
            print(f"{emoji} {category}:")
            print(f"   Budget: NPR {budget:.2f} | Spent: NPR {spent:.2f} | Remaining: NPR {remaining:.2f}")
            print(f"   Usage: {percentage:.1f}% {'(OVER BUDGET!)' if remaining < 0 else ''}")
            print()
    
    def generate_report(self):
        """Generate comprehensive financial report"""
        print("\n" + "="*50)
        print("📈 FINANCIAL REPORT")
        print("="*50)
        
        print("\n📊 Report Period Options:")
        print("1. Last month")
        print("2. Last 3 months")
        print("3. Last 6 months")
        print("4. Last year")
        
        choice = self.get_user_input("Choose period (1-4): ", int)
        
        months_map = {1: 1, 2: 3, 3: 6, 4: 12}
        months = months_map.get(choice, 3)
        
        summary = self.tracker.get_summary(months)
        
        if 'message' in summary:
            print(f"\n📭 {summary['message']}")
            return
        
        print(f"\n📊 Financial Summary - Last {months} month(s):")
        print("=" * 50)
        print(f"💰 Total Income:    NPR {summary['total_income']:,.2f}")
        print(f"💸 Total Expenses:  NPR {summary['total_expenses']:,.2f}")
        print(f"💵 Net Savings:     NPR {summary['net_savings']:,.2f}")
        print(f"📈 Savings Rate:    {summary['savings_rate']:.1f}%")
        print(f"📋 Transactions:    {summary['transaction_count']}")
        
        # Expense breakdown
        if summary['expense_by_category']:
            print("\n💸 Expense Breakdown:")
            print("-" * 30)
            for category, amount in summary['expense_by_category'].items():
                percentage = (amount / summary['total_expenses']) * 100 if summary['total_expenses'] > 0 else 0
                print(f"  {category}: NPR {amount:.2f} ({percentage:.1f}%)")
        
        # Income breakdown
        if summary['income_by_category']:
            print("\n💰 Income Breakdown:")
            print("-" * 30)
            for category, amount in summary['income_by_category'].items():
                percentage = (amount / summary['total_income']) * 100 if summary['total_income'] > 0 else 0
                print(f"  {category}: NPR {amount:.2f} ({percentage:.1f}%)")
    
    def create_visualizations(self):
        """Create and display charts"""
        print("\n" + "="*40)
        print("📊 CREATE VISUALIZATIONS")
        print("="*40)
        
        print("\n📈 Available Charts:")
        print("1. Expense Breakdown (Pie Chart)")
        print("2. Monthly Trends (Line Chart)")
        print("3. Both Charts")
        
        choice = self.get_user_input("Choose option (1-3): ", int)
        
        if choice in [1, 3]:
            print("\n📊 Creating expense breakdown chart...")
            self.tracker.analyzer.create_expense_pie_chart()
            print("✅ Expense pie chart saved as 'expense_breakdown.png'")
        
        if choice in [2, 3]:
            print("\n📈 Creating monthly trends chart...")
            self.tracker.analyzer.create_monthly_trend_chart()
            print("✅ Monthly trends chart saved as 'monthly_trends.png'")
        
        if choice not in [1, 2, 3]:
            print("❌ Invalid choice.")
            return
        
        print("\n💡 Tip: Check the current folder for the generated chart files!")
    
    def currency_converter(self):
        """Currency conversion tool"""
        print("\n" + "="*30)
        print("💱 CURRENCY CONVERTER")
        print("="*30)
        
        amount = self.get_user_input("💵 Enter amount: ", float)
        from_currency = self.get_user_input("🌍 From currency (e.g., USD): ").upper()
        to_currency = self.get_user_input("🌍 To currency (e.g., EUR): ").upper()
        
        print("\n🔄 Converting...")
        result = self.tracker.currency_converter.convert_currency(amount, from_currency, to_currency)
        
        if result:
            print(f"✅ {amount} {from_currency} = {result:.2f} {to_currency}")
        else:
            print("❌ Currency conversion failed. Please check your internet connection and currency codes.")
    
    def export_data(self):
        """Export data to CSV"""
        print("\n" + "="*30)
        print("📤 EXPORT DATA")
        print("="*30)
        
        filename = self.get_user_input("📁 Enter filename (default: financial_data.csv): ", required=False)
        if not filename:
            filename = "financial_data.csv"
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        exported_file = self.tracker.export_data(filename)
        print(f"\n✅ Data exported successfully to '{exported_file}'!")
        print("💡 You can open this file in Excel or any spreadsheet application.")
    
    def delete_transaction(self):
        """Delete a transaction"""
        print("\n" + "="*30)
        print("🗑️  DELETE TRANSACTION")
        print("="*30)
        
        # First show recent transactions
        transactions = self.tracker.db_manager.get_transactions()
        if not transactions:
            print("\n📭 No transactions found.")
            return
        
        print("\n📋 Recent Transactions:")
        print("-" * 70)
        print(f"{'ID':<4} {'Date':<12} {'Type':<8} {'Category':<15} {'Amount':<10}")
        print("-" * 70)
        
        # Show last 10 transactions
        for t in transactions[:10]:
            amount_str = f"NPR {t.amount:.2f}"
            type_emoji = "💰" if t.transaction_type == "income" else "💸"
            print(f"{t.id:<4} {t.date:<12} {type_emoji}{t.transaction_type:<7} {t.category:<15} {amount_str:<10}")
        
        transaction_id = self.get_user_input("\n🗑️  Enter transaction ID to delete: ", int)
        
        # Simple deletion (in a real app, you'd want proper deletion in DatabaseManager)
        confirm = self.get_user_input(f"⚠️  Are you sure you want to delete transaction {transaction_id}? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y']:
            print(f"\n✅ Transaction {transaction_id} would be deleted.")
            print("💡 Note: This is a demo. In the full version, the transaction would be removed from the database.")
        else:
            print("\n❌ Deletion cancelled.")
    
    def clear_all_data(self):
        """Clear all transactions and budgets"""
        print("\n" + "="*40)
        print("🗃️  CLEAR ALL DATA")
        print("="*40)
        
        print("\n⚠️  WARNING: This will delete ALL your financial data!")
        print("   - All transactions (income and expenses)")
        print("   - All budget settings")
        print("   - This action CANNOT be undone!")
        
        confirm1 = self.get_user_input("\n🔴 Are you absolutely sure? Type 'DELETE ALL' to confirm: ")
        
        if confirm1 == "DELETE ALL":
            confirm2 = self.get_user_input("🔴 Final confirmation - Type 'YES' to proceed: ")
            
            if confirm2 == "YES":
                try:
                    # Delete database file
                    if os.path.exists("finance_tracker.db"):
                        os.remove("finance_tracker.db")
                    
                    # Reinitialize tracker with clean database
                    self.tracker = FinanceTracker()
                    
                    print("\n✅ All data has been cleared successfully!")
                    print("🆕 You now have a fresh start with your finance tracker.")
                    
                except Exception as e:
                    print(f"\n❌ Error clearing data: {e}")
                    print("💡 Please restart the application.")
            else:
                print("\n❌ Clear operation cancelled.")
        else:
            print("\n❌ Clear operation cancelled.")
    
    def run(self):
        """Main application loop"""
        while self.running:
            try:
                self.display_menu()
                choice = self.get_user_input("Choose an option (1-12): ", int)
                
                if choice == 1:
                    self.add_income()
                elif choice == 2:
                    self.add_expense()
                elif choice == 3:
                    self.view_transactions()
                elif choice == 4:
                    self.set_budget()
                elif choice == 5:
                    self.view_budget_status()
                elif choice == 6:
                    self.generate_report()
                elif choice == 7:
                    self.create_visualizations()
                elif choice == 8:
                    self.currency_converter()
                elif choice == 9:
                    self.export_data()
                elif choice == 10:
                    self.delete_transaction()
                elif choice == 11:
                    self.clear_all_data()
                elif choice == 12:
                    print("\n👋 Thank you for using Personal Finance Tracker!")
                    print("💡 Keep track of your finances for a better future! 🌟")
                    self.running = False
                else:
                    print("❌ Invalid choice. Please select a number between 1-12.")
                
                if self.running:
                    input("\n⏸️  Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using Personal Finance Tracker!")
                self.running = False
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")

def main():
    """Main function to run the interactive application"""
    try:
        app = InteractiveFinanceTracker()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Please contact support or check the logs.")

if __name__ == "__main__":
    main()

