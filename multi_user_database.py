"""
Multi-User Database Layer for Family Budget Tracker
Handles all database operations with user authentication and data isolation
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os
import hashlib
import secrets
import config


class MultiUserDB:
    """Manages multi-user database operations with role-based access control"""
    
    def __init__(self, db_path=None):
        """Initialize connection to SQLite database"""
        if db_path is None:
            # Use persistent disk on Render (/data), fallback to local for development
            if os.path.exists("/data"):
                db_path = "/data/family_budget.db"
                print("📁 Using persistent disk storage at /data")
            else:
                db_path = os.path.join(os.path.dirname(__file__), "family_budget.db")
                print("📁 Using local storage (development mode)")
        
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
        
        # Households table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS households (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                relationship TEXT,
                is_active INTEGER DEFAULT 1,
                invite_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (household_id) REFERENCES households(id)
            )
        ''')
        
        # Income table (with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Allocations table (with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                allocated_amount REAL NOT NULL,
                spent_amount REAL DEFAULT 0,
                balance REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, category)
            )
        ''')
        
        # Expenses table (with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Monthly settlements table (with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_settlements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                total_income REAL NOT NULL,
                total_expenses REAL NOT NULL,
                total_savings REAL NOT NULL,
                settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, year, month)
            )
        ''')
        
        self.conn.commit()
    
    # ==================== AUTHENTICATION & USER MANAGEMENT ====================
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_admin_user(self, email, password, full_name, household_name):
        """Create admin user and household"""
        try:
            cursor = self.conn.cursor()
            
            # Create household
            cursor.execute(
                'INSERT INTO households (name) VALUES (?)',
                (household_name,)
            )
            household_id = cursor.lastrowid
            
            # Create admin user
            password_hash = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (household_id, email, password_hash, full_name, role, relationship)
                VALUES (?, ?, ?, ?, 'admin', 'self')
            ''', (household_id, email, password_hash, full_name))
            
            user_id = cursor.lastrowid
            
            # Update household created_by
            cursor.execute('UPDATE households SET created_by = ? WHERE id = ?', (user_id, household_id))
            
            self.conn.commit()
            return (True, user_id, "Admin account created successfully!")
        except sqlite3.IntegrityError:
            return (False, None, "Email already exists!")
        except Exception as e:
            print(f"Error creating admin: {str(e)}")
            self.conn.rollback()
            return (False, None, f"Error: {str(e)}")
    
    def authenticate_user(self, email, password):
        """Authenticate user and return user info"""
        try:
            cursor = self.conn.cursor()
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                SELECT id, household_id, email, full_name, role, is_active
                FROM users
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            
            if user and user['is_active']:
                return (True, dict(user))
            else:
                return (False, None)
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return (False, None)
    
    def generate_invite_token(self):
        """Generate unique invite token"""
        return secrets.token_urlsafe(32)
    
    def create_member(self, household_id, email, full_name, relationship, created_by_admin_id):
        """Create a new family member and generate invite token"""
        try:
            cursor = self.conn.cursor()
            
            # Generate temporary password and invite token
            temp_password = secrets.token_urlsafe(16)
            password_hash = self._hash_password(temp_password)
            invite_token = self.generate_invite_token()
            
            cursor.execute('''
                INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, invite_token)
                VALUES (?, ?, ?, ?, 'member', ?, ?)
            ''', (household_id, email, password_hash, full_name, relationship, invite_token))
            
            member_id = cursor.lastrowid
            self.conn.commit()
            
            return (True, member_id, invite_token)
        except sqlite3.IntegrityError:
            return (False, None, None)
        except Exception as e:
            print(f"Error creating member: {str(e)}")
            self.conn.rollback()
            return (False, None, None)
    
    def accept_invite(self, invite_token, new_password):
        """Accept invite and set new password"""
        try:
            cursor = self.conn.cursor()
            
            # Find user by invite token
            cursor.execute('SELECT id FROM users WHERE invite_token = ?', (invite_token,))
            user = cursor.fetchone()
            
            if not user:
                return (False, "Invalid invite token")
            
            # Update password and clear invite token
            password_hash = self._hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, invite_token = NULL
                WHERE id = ?
            ''', (password_hash, user['id']))
            
            self.conn.commit()
            return (True, "Password set successfully! You can now login.")
        except Exception as e:
            print(f"Error accepting invite: {str(e)}")
            self.conn.rollback()
            return (False, f"Error: {str(e)}")
    
    def get_household_members(self, household_id):
        """Get all members of a household"""
        try:
            query = '''
                SELECT id, email, full_name, role, relationship, is_active, 
                       invite_token IS NOT NULL as pending_invite
                FROM users
                WHERE household_id = ?
                ORDER BY role DESC, full_name
            '''
            df = pd.read_sql_query(query, self.conn, params=(household_id,))
            return df
        except Exception as e:
            print(f"Error fetching members: {str(e)}")
            return pd.DataFrame()
    
    def get_user_by_id(self, user_id):
        """Get user details by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, household_id, email, full_name, role, relationship, is_active
                FROM users
                WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error fetching user: {str(e)}")
            return None
    
    def deactivate_member(self, member_id):
        """Deactivate a family member"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (member_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deactivating member: {str(e)}")
            return False
    
    def delete_member(self, member_id):
        """
        Completely delete a member and all their data
        This invalidates their invite token and removes all associated records
        """
        try:
            cursor = self.conn.cursor()
            
            # Delete all member's financial data
            cursor.execute('DELETE FROM expenses WHERE user_id = ?', (member_id,))
            cursor.execute('DELETE FROM allocations WHERE user_id = ?', (member_id,))
            cursor.execute('DELETE FROM income WHERE user_id = ?', (member_id,))
            cursor.execute('DELETE FROM monthly_settlements WHERE user_id = ?', (member_id,))
            
            # Finally, delete the user account (this also invalidates the invite token)
            cursor.execute('DELETE FROM users WHERE id = ? AND role != ?', (member_id, 'admin'))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting member: {str(e)}")
            self.conn.rollback()
            return False
    
    # ==================== INCOME OPERATIONS (USER-SCOPED) ====================
    
    def add_income(self, user_id, date, source, amount):
        """Add a new income entry for a user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO income (user_id, date, source, amount) VALUES (?, ?, ?, ?)',
                (user_id, date, source, float(amount))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding income: {str(e)}")
            return False
    
    def get_all_income(self, user_id):
        """Get all income entries for a user"""
        try:
            query = 'SELECT date as "Date", source as "Source", amount as "Amount" FROM income WHERE user_id = ? ORDER BY date DESC'
            df = pd.read_sql_query(query, self.conn, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching income: {str(e)}")
            return pd.DataFrame(columns=["Date", "Source", "Amount"])
    
    def get_total_income(self, user_id):
        """Calculate total income for a user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM income WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error calculating total income: {str(e)}")
            return 0
    
    def get_income_with_ids(self, user_id):
        """Get all income entries with IDs for editing"""
        try:
            query = 'SELECT id, date, source, amount FROM income WHERE user_id = ? ORDER BY date DESC'
            df = pd.read_sql_query(query, self.conn, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching income with IDs: {str(e)}")
            return pd.DataFrame(columns=["id", "date", "source", "amount"])
    
    def update_income(self, income_id, user_id, date, source, amount):
        """Update an existing income entry"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE income SET date = ?, source = ?, amount = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
                (date, source, float(amount), income_id, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating income: {str(e)}")
            return False
    
    def delete_income(self, income_id, user_id):
        """Delete an income entry"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM income WHERE id = ? AND user_id = ?', (income_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting income: {str(e)}")
            return False
    
    # ==================== ALLOCATION OPERATIONS (USER-SCOPED) ====================
    
    def add_allocation(self, user_id, category, allocated_amount):
        """Add a new allocation category for a user"""
        try:
            cursor = self.conn.cursor()
            balance = float(allocated_amount)
            cursor.execute(
                'INSERT INTO allocations (user_id, category, allocated_amount, spent_amount, balance) VALUES (?, ?, ?, 0, ?)',
                (user_id, category, float(allocated_amount), balance)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Category '{category}' already exists for this user")
            return False
        except Exception as e:
            print(f"Error adding allocation: {str(e)}")
            return False
    
    def get_all_allocations(self, user_id):
        """Get all allocations for a user"""
        try:
            query = '''
                SELECT 
                    category as "Category", 
                    allocated_amount as "Allocated Amount", 
                    spent_amount as "Spent Amount", 
                    balance as "Balance" 
                FROM allocations 
                WHERE user_id = ?
                ORDER BY category
            '''
            df = pd.read_sql_query(query, self.conn, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching allocations: {str(e)}")
            return pd.DataFrame(columns=["Category", "Allocated Amount", "Spent Amount", "Balance"])
    
    def get_categories(self, user_id):
        """Get list of all allocation categories for a user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT category FROM allocations WHERE user_id = ? ORDER BY category', (user_id,))
            rows = cursor.fetchall()
            return [row['category'] for row in rows]
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return []
    
    def update_allocation_spent(self, user_id, category, expense_amount):
        """Update spent amount and balance for a category when expense is added"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            row = cursor.fetchone()
            
            if not row:
                print(f"Category '{category}' not found")
                return False
            
            allocated = row['allocated_amount']
            current_spent = row['spent_amount']
            
            new_spent = current_spent + float(expense_amount)
            new_balance = allocated - new_spent
            
            cursor.execute(
                'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND category = ?',
                (new_spent, new_balance, user_id, category)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating allocation: {str(e)}")
            return False
    
    def update_allocation_amount(self, user_id, category, new_allocated_amount):
        """Update allocated amount for a category"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                'SELECT spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            row = cursor.fetchone()
            
            if not row:
                print(f"Category '{category}' not found")
                return False
            
            current_spent = row['spent_amount']
            new_balance = float(new_allocated_amount) - current_spent
            
            cursor.execute(
                'UPDATE allocations SET allocated_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND category = ?',
                (float(new_allocated_amount), new_balance, user_id, category)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating allocation amount: {str(e)}")
            return False
    
    def delete_allocation(self, user_id, category):
        """Delete an allocation category"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM allocations WHERE user_id = ? AND category = ?', (user_id, category))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting allocation: {str(e)}")
            return False
    
    # ==================== EXPENSE OPERATIONS (USER-SCOPED) ====================
    
    def add_expense(self, user_id, date, category, amount, comment):
        """Add a new expense and auto-update allocation"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                'INSERT INTO expenses (user_id, date, category, amount, comment) VALUES (?, ?, ?, ?, ?)',
                (user_id, date, category, float(amount), comment)
            )
            
            self.update_allocation_spent(user_id, category, amount)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_all_expenses(self, user_id):
        """Get all expenses for a user"""
        try:
            query = '''
                SELECT 
                    date as "Date", 
                    category as "Category", 
                    amount as "Amount", 
                    comment as "Comment" 
                FROM expenses 
                WHERE user_id = ?
                ORDER BY date DESC
            '''
            df = pd.read_sql_query(query, self.conn, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching expenses: {str(e)}")
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Comment"])
    
    def get_total_expenses(self, user_id):
        """Calculate total expenses for a user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error calculating total expenses: {str(e)}")
            return 0
    
    def get_expenses_by_category(self, user_id, category):
        """Get expenses filtered by category"""
        try:
            query = '''
                SELECT 
                    date as "Date", 
                    category as "Category", 
                    amount as "Amount", 
                    comment as "Comment" 
                FROM expenses 
                WHERE user_id = ? AND category = ?
                ORDER BY date DESC
            '''
            df = pd.read_sql_query(query, self.conn, params=(user_id, category))
            return df
        except Exception as e:
            print(f"Error fetching expenses by category: {str(e)}")
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Comment"])
    
    def get_expenses_with_ids(self, user_id):
        """Get all expenses with IDs for editing"""
        try:
            query = 'SELECT id, date, category, amount, comment FROM expenses WHERE user_id = ? ORDER BY date DESC'
            df = pd.read_sql_query(query, self.conn, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching expenses with IDs: {str(e)}")
            return pd.DataFrame(columns=["id", "date", "category", "amount", "comment"])
    
    def update_expense(self, expense_id, user_id, date, category, amount, comment, old_category, old_amount):
        """Update an existing expense and recalculate allocations"""
        try:
            cursor = self.conn.cursor()
            
            #Reverse old expense
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, old_category)
            )
            old_row = cursor.fetchone()
            if old_row:
                old_allocated = old_row['allocated_amount']
                old_spent = old_row['spent_amount']
                new_old_spent = old_spent - float(old_amount)
                new_old_balance = old_allocated - new_old_spent
                cursor.execute(
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND category = ?',
                    (new_old_spent, new_old_balance, user_id, old_category)
                )
            
            # Add new expense
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            new_row = cursor.fetchone()
            if new_row:
                new_allocated = new_row['allocated_amount']
                new_spent = new_row['spent_amount']
                new_new_spent = new_spent + float(amount)
                new_new_balance = new_allocated - new_new_spent
                cursor.execute(
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND category = ?',
                    (new_new_spent, new_new_balance, user_id, category)
                )
            
            cursor.execute(
                'UPDATE expenses SET date = ?, category = ?, amount = ?, comment = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
                (date, category, float(amount), comment, expense_id, user_id)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def delete_expense(self, expense_id, user_id, category, amount):
        """Delete an expense and update allocation"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            row = cursor.fetchone()
            if row:
                allocated = row['allocated_amount']
                spent = row['spent_amount']
                new_spent = spent - float(amount)
                new_balance = allocated - new_spent
                cursor.execute(
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND category = ?',
                    (new_spent, new_balance, user_id, category)
                )
            
            cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting expense: {str(e)}")
            self.conn.rollback()
            return False
    
    # ==================== ADMIN ANALYTICS (HOUSEHOLD-WIDE) ====================
    
    def get_household_total_income(self, household_id):
        """Get total income for entire household"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT SUM(i.amount) as total
                FROM income i
                JOIN users u ON i.user_id = u.id
                WHERE u.household_id = ?
            ''', (household_id,))
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error calculating household income: {str(e)}")
            return 0
    
    def get_household_total_expenses(self, household_id):
        """Get total expenses for entire household"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT SUM(e.amount) as total
                FROM expenses e
                JOIN users u ON e.user_id = u.id
                WHERE u.household_id = ?
            ''', (household_id,))
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0
        except Exception as e:
            print(f"Error calculating household expenses: {str(e)}")
            return 0
    
    def get_household_member_summary(self, household_id):
        """Get income/expense summary by member"""
        try:
            query = '''
                SELECT 
                    u.full_name as "Member",
                    u.relationship as "Relationship",
                    COALESCE(SUM(i.amount), 0) as "Income",
                    COALESCE(SUM(e.amount), 0) as "Expenses",
                    COALESCE(SUM(i.amount), 0) - COALESCE(SUM(e.amount), 0) as "Savings"
                FROM users u
                LEFT JOIN income i ON u.id = i.user_id
                LEFT JOIN expenses e ON u.id = e.user_id
                WHERE u.household_id = ? AND u.is_active = 1
                GROUP BY u.id, u.full_name, u.relationship
                ORDER BY u.role DESC, u.full_name
            '''
            df = pd.read_sql_query(query, self.conn, params=(household_id,))
            return df
        except Exception as e:
            print(f"Error fetching household summary: {str(e)}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
