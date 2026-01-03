"""
Database layer using SQLite for local storage
Handles all CRUD operations for Income, Allocations, and Expenses
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os
import config


class LocalDB:
    """Manages all database operations using SQLite as local storage"""
    
    def __init__(self, db_path=None):
        """Initialize connection to SQLite database"""
        if db_path is None:
            db_path = config.DATABASE_PATH
        
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._initialize_tables()
    
    def _connect(self):
        """Establish connection to SQLite database"""
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise
    
    def _initialize_tables(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Income table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                allocated_amount REAL NOT NULL,
                spent_amount REAL DEFAULT 0,
                balance REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        # Sync metadata table (for future sync functionality)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_sync TIMESTAMP,
                sync_status TEXT
            )
        ''')
        
        # Monthly settlements table (for archiving settled months)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_settlements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                total_income REAL NOT NULL,
                total_expenses REAL NOT NULL,
                total_savings REAL NOT NULL,
                settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(year, month)
            )
        ''')
        
        self.conn.commit()

    
    # ==================== INCOME OPERATIONS ====================
    
    def add_income(self, date, source, amount):
        """Add a new income entry"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO income (date, source, amount) VALUES (?, ?, ?)',
                (date, source, float(amount))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding income: {str(e)}")
            return False
    
    def get_all_income(self):
        """Get all income entries as DataFrame"""
        try:
            query = 'SELECT date as "Date", source as "Source", amount as "Amount" FROM income ORDER BY date DESC'
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error fetching income: {str(e)}")
            return pd.DataFrame(columns=["Date", "Source", "Amount"])
    
    def get_total_income(self):
        """Calculate total income"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM income')
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error calculating total income: {str(e)}")
            return 0
    
    def delete_income(self, row_index):
        """Delete an income entry by row index"""
        try:
            # Get all income sorted by date DESC
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM income ORDER BY date DESC')
            rows = cursor.fetchall()
            
            if 0 <= row_index < len(rows):
                income_id = rows[row_index]['id']
                cursor.execute('DELETE FROM income WHERE id = ?', (income_id,))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting income: {str(e)}")
            return False
    
    def update_income(self, income_id, date, source, amount):
        """Update an existing income entry"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE income SET date = ?, source = ?, amount = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (date, source, float(amount), income_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating income: {str(e)}")
            return False
    
    def get_income_with_ids(self):
        """Get all income entries with IDs for editing"""
        try:
            query = 'SELECT id, date, source, amount FROM income ORDER BY date DESC'
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error fetching income with IDs: {str(e)}")
            return pd.DataFrame(columns=["id", "date", "source", "amount"])
    
    # ==================== ALLOCATION OPERATIONS ====================
    
    def add_allocation(self, category, allocated_amount):
        """Add a new allocation category"""
        try:
            cursor = self.conn.cursor()
            balance = float(allocated_amount)
            cursor.execute(
                'INSERT INTO allocations (category, allocated_amount, spent_amount, balance) VALUES (?, ?, 0, ?)',
                (category, float(allocated_amount), balance)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Category '{category}' already exists")
            return False
        except Exception as e:
            print(f"Error adding allocation: {str(e)}")
            return False
    
    def get_all_allocations(self):
        """Get all allocations as DataFrame"""
        try:
            query = '''
                SELECT 
                    category as "Category", 
                    allocated_amount as "Allocated Amount", 
                    spent_amount as "Spent Amount", 
                    balance as "Balance" 
                FROM allocations 
                ORDER BY category
            '''
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error fetching allocations: {str(e)}")
            return pd.DataFrame(columns=["Category", "Allocated Amount", "Spent Amount", "Balance"])
    
    def get_categories(self):
        """Get list of all allocation categories"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT category FROM allocations ORDER BY category')
            rows = cursor.fetchall()
            return [row['category'] for row in rows]
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return []
    
    def update_allocation_spent(self, category, expense_amount):
        """Update spent amount and balance for a category when expense is added"""
        try:
            cursor = self.conn.cursor()
            
            # Get current values
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE category = ?',
                (category,)
            )
            row = cursor.fetchone()
            
            if not row:
                print(f"Category '{category}' not found")
                return False
            
            allocated = row['allocated_amount']
            current_spent = row['spent_amount']
            
            # Calculate new values
            new_spent = current_spent + float(expense_amount)
            new_balance = allocated - new_spent
            
            # Update the database
            cursor.execute(
                'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE category = ?',
                (new_spent, new_balance, category)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating allocation: {str(e)}")
            return False
    
    def update_allocation_amount(self, category, new_allocated_amount):
        """Update allocated amount for a category and recalculate balance"""
        try:
            cursor = self.conn.cursor()
            
            # Get current spent amount
            cursor.execute(
                'SELECT spent_amount FROM allocations WHERE category = ?',
                (category,)
            )
            row = cursor.fetchone()
            
            if not row:
                print(f"Category '{category}' not found")
                return False
            
            current_spent = row['spent_amount']
            new_balance = float(new_allocated_amount) - current_spent
            
            # Update the database
            cursor.execute(
                'UPDATE allocations SET allocated_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE category = ?',
                (float(new_allocated_amount), new_balance, category)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating allocation amount: {str(e)}")
            return False
    
    def delete_allocation(self, category):
        """Delete an allocation category"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM allocations WHERE category = ?', (category,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting allocation: {str(e)}")
            return False
    
    # ==================== EXPENSE OPERATIONS ====================
    
    def add_expense(self, date, category, amount, comment):
        """Add a new expense and auto-update allocation"""
        try:
            cursor = self.conn.cursor()
            
            # Add the expense
            cursor.execute(
                'INSERT INTO expenses (date, category, amount, comment) VALUES (?, ?, ?, ?)',
                (date, category, float(amount), comment)
            )
            
            # Update the allocation
            self.update_allocation_spent(category, amount)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_all_expenses(self):
        """Get all expenses as DataFrame"""
        try:
            query = '''
                SELECT 
                    date as "Date", 
                    category as "Category", 
                    amount as "Amount", 
                    comment as "Comment" 
                FROM expenses 
                ORDER BY date DESC
            '''
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error fetching expenses: {str(e)}")
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Comment"])
    
    def get_total_expenses(self):
        """Calculate total expenses"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM expenses')
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error calculating total expenses: {str(e)}")
            return 0
    
    def get_expenses_by_category(self, category):
        """Get expenses filtered by category"""
        try:
            query = '''
                SELECT 
                    date as "Date", 
                    category as "Category", 
                    amount as "Amount", 
                    comment as "Comment" 
                FROM expenses 
                WHERE category = ?
                ORDER BY date DESC
            '''
            df = pd.read_sql_query(query, self.conn, params=(category,))
            return df
        except Exception as e:
            print(f"Error fetching expenses by category: {str(e)}")
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Comment"])
    
    def get_expenses_with_ids(self):
        """Get all expenses with IDs for editing"""
        try:
            query = 'SELECT id, date, category, amount, comment FROM expenses ORDER BY date DESC'
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error fetching expenses with IDs: {str(e)}")
            return pd.DataFrame(columns=["id", "date", "category", "amount", "comment"])
    
    def update_expense(self, expense_id, date, category, amount, comment, old_category, old_amount):
        """Update an existing expense and recalculate allocations"""
        try:
            cursor = self.conn.cursor()
            
            # Reverse the old expense from old category
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE category = ?',
                (old_category,)
            )
            old_row = cursor.fetchone()
            if old_row:
                old_allocated = old_row['allocated_amount']
                old_spent = old_row['spent_amount']
                new_old_spent = old_spent - float(old_amount)
                new_old_balance = old_allocated - new_old_spent
                cursor.execute(
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE category = ?',
                    (new_old_spent, new_old_balance, old_category)
                )
            
            # Add the new expense to new category
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE category = ?',
                (category,)
            )
            new_row = cursor.fetchone()
            if new_row:
                new_allocated = new_row['allocated_amount']
                new_spent = new_row['spent_amount']
                new_new_spent = new_spent + float(amount)
                new_new_balance = new_allocated - new_new_spent
                cursor.execute(
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE category = ?',
                    (new_new_spent, new_new_balance, category)
                )
            
            # Update the expense
            cursor.execute(
                'UPDATE expenses SET date = ?, category = ?, amount = ?, comment = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (date, category, float(amount), comment, expense_id)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def delete_expense(self, expense_id, category, amount):
        """Delete an expense and update allocation"""
        try:
            cursor = self.conn.cursor()
            
            # Reverse the expense from allocation
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE category = ?',
                (category,)
            )
            row = cursor.fetchone()
            if row:
                allocated = row['allocated_amount']
                spent = row['spent_amount']
                new_spent = spent - float(amount)
                new_balance = allocated - new_spent
                cursor.execute(
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE category = ?',
                    (new_spent, new_balance, category)
                )
            
            # Delete the expense
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting expense: {str(e)}")
            self.conn.rollback()
            return False
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_years_with_data(self):
        """Get list of years that have expense data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT DISTINCT substr(date, 1, 4) as year 
                FROM expenses 
                ORDER BY year DESC
            ''')
            years = [row['year'] for row in cursor.fetchall()]
            return years if years else [str(datetime.now().year)]
        except Exception as e:
            print(f"Error fetching years: {str(e)}")
            return [str(datetime.now().year)]
    
    def get_months_with_data(self, year):
        """Get list of months that have data for a specific year"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT DISTINCT substr(date, 6, 2) as month 
                FROM expenses 
                WHERE substr(date, 1, 4) = ?
                ORDER BY month
            ''', (year,))
            months = [int(row['month']) for row in cursor.fetchall()]
            return months
        except Exception as e:
            print(f"Error fetching months: {str(e)}")
            return []
    
    def get_income_for_period(self, year, month=None):
        """Get total income for a year or specific month"""
        try:
            cursor = self.conn.cursor()
            if month:
                cursor.execute('''
                    SELECT SUM(amount) as total
                    FROM income
                    WHERE substr(date, 1, 4) = ? AND substr(date, 6, 2) = ?
                ''', (year, f'{month:02d}'))
            else:
                cursor.execute('''
                    SELECT SUM(amount) as total
                    FROM income
                    WHERE substr(date, 1, 4) = ?
                ''', (year,))
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error getting income for period: {str(e)}")
            return 0
    
    def get_expenses_for_period(self, year, month=None):
        """Get total expenses for a year or specific month"""
        try:
            cursor = self.conn.cursor()
            if month:
                cursor.execute('''
                    SELECT SUM(amount) as total
                    FROM expenses
                    WHERE substr(date, 1, 4) = ? AND substr(date, 6, 2) = ?
                ''', (year, f'{month:02d}'))
            else:
                cursor.execute('''
                    SELECT SUM(amount) as total
                    FROM expenses
                    WHERE substr(date, 1, 4) = ?
                ''', (year,))
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error getting expenses for period: {str(e)}")
            return 0
    
    def get_monthly_summary(self, year):
        """Get monthly summary of income, expenses, and savings for a year"""
        try:
            query = '''
                SELECT 
                    substr(date, 6, 2) as month,
                    SUM(CASE WHEN table_name = 'income' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN table_name = 'expense' THEN amount ELSE 0 END) as expenses
                FROM (
                    SELECT date, amount, 'income' as table_name FROM income WHERE substr(date, 1, 4) = ?
                    UNION ALL
                    SELECT date, amount, 'expense' as table_name FROM expenses WHERE substr(date, 1, 4) = ?
                )
                GROUP BY month
                ORDER BY month
            '''
            df = pd.read_sql_query(query, self.conn, params=(year, year))
            if not df.empty:
                df['month'] = df['month'].astype(int)
                df['savings'] = df['income'] - df['expenses']
            return df
        except Exception as e:
            print(f"Error getting monthly summary: {str(e)}")
            return pd.DataFrame(columns=['month', 'income', 'expenses', 'savings'])
    
    # ==================== SETTLEMENT OPERATIONS ====================
    
    def settle_current_month(self, year, month):
        """
        Settle the current month by archiving data and clearing allocations and expenses.
        Returns (success, message) tuple
        """
        try:
            cursor = self.conn.cursor()
            
            # Check if month is already settled
            if self.is_month_settled(year, month):
                return (False, f"Month {month}/{year} is already settled!")
            
            # Get total income for the month
            total_income = self.get_income_for_period(year, month)
            
            # Get total expenses for the month
            total_expenses = self.get_expenses_for_period(year, month)
            
            # Calculate savings
            total_savings = total_income - total_expenses
            
            # Archive the month data
            cursor.execute('''
                INSERT INTO monthly_settlements (year, month, total_income, total_expenses, total_savings)
                VALUES (?, ?, ?, ?, ?)
            ''', (year, month, total_income, total_expenses, total_savings))
            
            # Clear all allocations (reset for next month)
            cursor.execute('DELETE FROM allocations')
            
            # Clear all expenses
            cursor.execute('DELETE FROM expenses')
            
            self.conn.commit()
            return (True, f"Successfully settled month {month}/{year}!")
        except Exception as e:
            print(f"Error settling month: {str(e)}")
            self.conn.rollback()
            return (False, f"Error settling month: {str(e)}")
    
    def get_settled_months(self, year):
        """Get all settled months for a given year"""
        try:
            query = '''
                SELECT month, total_income, total_expenses, total_savings, settled_at
                FROM monthly_settlements
                WHERE year = ?
                ORDER BY month
            '''
            df = pd.read_sql_query(query, self.conn, params=(year,))
            return df
        except Exception as e:
            print(f"Error fetching settled months: {str(e)}")
            return pd.DataFrame(columns=['month', 'total_income', 'total_expenses', 'total_savings', 'settled_at'])
    
    def is_month_settled(self, year, month):
        """Check if a specific month is already settled"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM monthly_settlements
                WHERE year = ? AND month = ?
            ''', (year, month))
            result = cursor.fetchone()
            return result['count'] > 0
        except Exception as e:
            print(f"Error checking settlement status: {str(e)}")
            return False
    
    def get_all_settled_data(self, year):
        """Get combined settled and unsettled data for a year"""
        try:
            # Get settled months
            settled_df = self.get_settled_months(year)
            settled_df['settled'] = True
            settled_df.rename(columns={
                'total_income': 'income',
                'total_expenses': 'expenses',
                'total_savings': 'savings'
            }, inplace=True)
            
            # Get current unsettled summary
            unsettled_df = self.get_monthly_summary(year)
            if not unsettled_df.empty:
                unsettled_df['settled'] = False
                unsettled_df['settled_at'] = None
            
            # Combine both
            if not settled_df.empty and not unsettled_df.empty:
                combined_df = pd.concat([settled_df, unsettled_df], ignore_index=True)
            elif not settled_df.empty:
                combined_df = settled_df
            elif not unsettled_df.empty:
                combined_df = unsettled_df
            else:
                return pd.DataFrame(columns=['month', 'income', 'expenses', 'savings', 'settled', 'settled_at'])
            
            return combined_df.sort_values('month')
        except Exception as e:
            print(f"Error getting all settled data: {str(e)}")
            return pd.DataFrame(columns=['month', 'income', 'expenses', 'savings', 'settled', 'settled_at'])
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

