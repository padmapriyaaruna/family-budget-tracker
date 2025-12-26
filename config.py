"""
Configuration file for the Expense Tracker application
"""
import os

# Database Configuration
DATABASE_PATH = "expense_tracker.db"  # SQLite database file

# Google Sheets Configuration (Optional - for sync feature)
CREDENTIALS_FILE = "credentials.json"  # Path to your service account credentials (optional)
SPREADSHEET_NAME = "Expense_Tracker"   # Name of your Google Sheet (optional)

# Sheet names (worksheets within the spreadsheet)
INCOME_SHEET = "Income"
ALLOCATIONS_SHEET = "Allocations"
EXPENSES_SHEET = "Expenses"

# Application Constants
CURRENCY_SYMBOL = "₹"
DATE_FORMAT = "%Y-%m-%d"

# Sync Settings
SYNC_ENABLED = False  # Set to True if you want to use Google Sheets sync
AUTO_SYNC = False     # Set to True for automatic sync on app start
