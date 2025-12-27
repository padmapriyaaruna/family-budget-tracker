"""
Multi-User Database Layer for Family Budget Tracker
Handles all database operations with user authentication and data isolation
"""
import sqlite3
import hashlib
import secrets
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# Check if we should use PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    print("🐘 PostgreSQL detected via DATABASE_URL")
else:
    print("📁 Using SQLite (local development)")

class MultiUserDB:
    """Manages multi-user database operations with role-based access control"""
    
    def __init__(self, db_path=None):
        """Initialize database connection"""
        self.use_postgres = USE_POSTGRES
        
        if USE_POSTGRES:
            # psycopg2 for regular queries
            self.conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            self.conn.autocommit = False
            print("✅ Connected to PostgreSQL")
            
            # SQLAlchemy engine for pandas queries (fixes connection issues)
            self.engine = create_engine(
                DATABASE_URL,
                poolclass=NullPool,  # No pooling for serverless
                connect_args={"sslmode": "require"}
            )
            print("✅ SQLAlchemy engine created for pandas queries")
            self.db_path = None
        else:
            if db_path is None:
                db_path = "/data/family_budget.db" if os.path.exists("/data") else os.path.join(os.path.dirname(__file__), "family_budget.db")
            self.db_path = db_path
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.engine = None  # No engine needed for SQLite
            print("✅ Connected to SQLite")
        
        self._initialize_tables()
    
    def _execute(self, cursor, query, params=None):
        """Helper method to execute queries with correct parameter syntax for the database type"""
        if self.use_postgres:
            # Convert ? placeholders to %s for PostgreSQL
            query = query.replace('?', '%s')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor
        
    def _initialize_tables(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Detect if using PostgreSQL or SQLite
        id_type = "SERIAL PRIMARY KEY" if self.use_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        bool_type = "BOOLEAN" if self.use_postgres else "INTEGER"
        text_type = "TEXT"
        
        # Households table (with is_active for super admin management)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS households (
                id {id_type},
                name {text_type} NOT NULL,
                created_by INTEGER,
                is_active {bool_type} DEFAULT {'TRUE' if self.use_postgres else '1'},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table (role can be: superadmin, admin, member)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                id {id_type},
                household_id INTEGER,
                email {text_type} UNIQUE NOT NULL,
                password_hash {text_type} NOT NULL,
                full_name {text_type} NOT NULL,
                role {text_type} DEFAULT 'member',
                relationship {text_type},
                is_active {bool_type} DEFAULT {'TRUE' if self.use_postgres else '1'},
                invite_token {text_type} UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (household_id) REFERENCES households(id)
            )
        ''')
        
        # Check and add is_active column to households if it doesn't exist (SQLite only)
        if not self.use_postgres:
            cursor.execute("PRAGMA table_info(households)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'is_active' not in columns:
                cursor.execute('ALTER TABLE households ADD COLUMN is_active INTEGER DEFAULT 1')
                print("✅ Added is_active column to households table")
        
        # Income table (with user_id)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS income (
                id {id_type},
                user_id INTEGER NOT NULL,
                date {text_type} NOT NULL,
                source {text_type} NOT NULL,
                amount {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Allocations table (with user_id)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS allocations (
                id {id_type},
                user_id INTEGER NOT NULL,
                category {text_type} NOT NULL,
                allocated_amount {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                spent_amount {'NUMERIC' if self.use_postgres else 'REAL'} DEFAULT 0,
                balance {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, category)
            )
        ''')
        
        # Expenses table (with user_id)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS expenses (
                id {id_type},
                user_id INTEGER NOT NULL,
                date {text_type} NOT NULL,
                category {text_type} NOT NULL,
                amount {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                comment {text_type},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Monthly settlements table (with user_id)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS monthly_settlements (
                id {id_type},
                user_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                total_income {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                total_expenses {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                total_savings {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, year, month)
            )
        ''')
        
        self.conn.commit()
        
        # Create super admin if it doesn't exist
        self._create_super_admin()
    
    # ==================== AUTHENTICATION & USER MANAGEMENT ====================
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _create_super_admin(self):
        """Create super admin user if it doesn't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Check if super admin exists
            self._execute(cursor, "SELECT id FROM users WHERE email = 'superadmin' AND role = 'superadmin'")
            if cursor.fetchone():
                return  # Super admin already exists
            
            # Get password from environment or use default
            superadmin_password = os.getenv('SUPERADMIN_PASSWORD', 'superuser')
            password_hash = self._hash_password(superadmin_password)
            
            # Create super admin (household_id is NULL)
            # Use ? placeholder - it will be auto-converted to %s for PostgreSQL
            is_active_value = True if self.use_postgres else 1
            self._execute(cursor, '''
                INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, is_active)
                VALUES (NULL, 'superadmin', ?, 'Super Administrator', 'superadmin', NULL, ?)
            ''', (password_hash, is_active_value))
            
            self.conn.commit()
            print("✅ Super admin created successfully")
        except Exception as e:
            print(f"❌ Error creating super admin: {str(e)}")
            # Don't fail if super admin already exists
    
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
            
            print(f"DEBUG: Authenticating user: {email}")
            print(f"DEBUG: Password hash: {password_hash}")
            
            self._execute(cursor, '''
                SELECT id, household_id, email, full_name, role, relationship, is_active
                FROM users
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            
            print(f"DEBUG: Query result: {user}")
            
            if user:
                print(f"DEBUG: User found - is_active: {user['is_active']} (type: {type(user['is_active'])})")
                if user['is_active']:
                    print(f"DEBUG: User is active, authentication successful")
                    return (True, dict(user))
                else:
                    print(f"DEBUG: User is inactive")
                    return (False, None)
            else:
                print(f"DEBUG: No user found with email and password")
                return (False, None)
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            import traceback
            traceback.print_exc()
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
            
            # Create member with appropriate method for database type
            if self.use_postgres:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, invite_token)
                    VALUES (?, ?, ?, ?, 'member', ?, ?)
                    RETURNING id
                ''', (household_id, email, password_hash, full_name, relationship, invite_token))
                member_id = cursor.fetchone()['id']
            else:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, invite_token)
                    VALUES (?, ?, ?, ?, 'member', ?, ?)
                ''', (household_id, email, password_hash, full_name, relationship, invite_token))
                member_id = cursor.lastrowid
            
            self.conn.commit()
            
            return (True, member_id, invite_token)
        except Exception as e:
            error_msg = str(e)
            print(f"Error creating member: {error_msg}")
            self.conn.rollback()
            # Check if it's a unique constraint violation (email already exists)
            if 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower():
                return (False, None, None)
            else:
                # Other error - log it
                import traceback
                traceback.print_exc()
                return (False, None, None)
    
    def accept_invite(self, invite_token, new_password):
        """Accept invite and set new password"""
        try:
            cursor = self.conn.cursor()
            
            # Find user by invite token
            self._execute(cursor, 'SELECT id FROM users WHERE invite_token = ?', (invite_token,))
            user = cursor.fetchone()
            
            if not user:
                return (False, "Invalid invite token")
            
            # Update password and clear invite token
            password_hash = self._hash_password(new_password)
            self._execute(cursor, '''
                UPDATE users 
                SET password_hash = ?, invite_token = NULL
                WHERE id = ?
            ''', (password_hash, user['id']))
            
            self.conn.commit()
            return (True, "Password set successfully! You can now login.")
        except Exception as e:
            print(f"Error accepting invite: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return (False, f"Error: {str(e)}")
    
    def get_household_members(self, household_id):
        """Get all members of a household"""
        try:
            # Use appropriate parameter placeholder
            param_placeholder = '%s' if self.use_postgres else '?'
            query = f'''
                SELECT id, email, full_name, role, relationship, is_active, 
                       invite_token, invite_token IS NOT NULL as pending_invite
                FROM users
                WHERE household_id = {param_placeholder}
                ORDER BY role DESC, full_name
            '''
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            df = pd.read_sql_query(query, conn_to_use, params=(household_id,))
            print(f"DEBUG: get_household_members returned {len(df)} rows for household {household_id}")
            return df
        except Exception as e:
            print(f"Error fetching members: {str(e)}")
            import traceback
            traceback.print_exc()
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
    
    # ==================== SUPER ADMIN METHODS ====================
    
    def get_all_households(self):
        """Get all households (for super admin)"""
        try:
            query = '''
                SELECT h.id, h.name, h.is_active, h.created_at,
                       u.full_name as admin_name, u.email as admin_email,
                       COUNT(DISTINCT m.id) as member_count
                FROM households h
                LEFT JOIN users u ON h.created_by = u.id
                LEFT JOIN users m ON m.household_id = h.id
                GROUP BY h.id, h.name, h.is_active, h.created_at, u.full_name, u.email
                ORDER BY h.created_at DESC
            '''
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            df = pd.read_sql_query(query, conn_to_use)
            print(f"DEBUG: get_all_households returned {len(df)} rows")
            if not df.empty:
                print(f"DEBUG: First row: {df.iloc[0].to_dict()}")
            return df
        except Exception as e:
            print(f"Error fetching households: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def create_household_with_admin(self, household_name, admin_email, admin_name, admin_password):
        """Super admin creates a new household with a family admin"""
        try:
            cursor = self.conn.cursor()
            
            # Check if email already exists
            self._execute(cursor, 'SELECT id FROM users WHERE email = ?', (admin_email,))
            if cursor.fetchone():
                return (False, None, "Email already exists")
            
            # Create household - use RETURNING for PostgreSQL
            is_active_value = True if self.use_postgres else 1
            if self.use_postgres:
                self._execute(cursor, 'INSERT INTO households (name, is_active) VALUES (?, ?) RETURNING id', (household_name, is_active_value))
                household_id = cursor.fetchone()['id']
            else:
                self._execute(cursor, 'INSERT INTO households (name, is_active) VALUES (?, ?)', (household_name, is_active_value))
                household_id = cursor.lastrowid
           
            # Create admin user - use RETURNING for PostgreSQL
            password_hash = self._hash_password(admin_password)
            if self.use_postgres:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, is_active)
                    VALUES (?, ?, ?, ?, 'admin', 'self', ?)
                    RETURNING id
                ''', (household_id, admin_email, password_hash, admin_name, is_active_value))
                admin_id = cursor.fetchone()['id']
            else:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, is_active)
                    VALUES (?, ?, ?, ?, 'admin', 'self', ?)
                ''', (household_id, admin_email, password_hash, admin_name, is_active_value))
                admin_id = cursor.lastrowid
            
            # Update household created_by
            self._execute(cursor, 'UPDATE households SET created_by = ? WHERE id = ?', (admin_id, household_id))
            
            self.conn.commit()
            return (True, household_id, f"Household '{household_name}' created successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating household: {str(e)}")
            return (False, None, str(e))
    
    def toggle_household_status(self, household_id):
        """Enable/disable a household"""
        try:
            cursor = self.conn.cursor()
            # For PostgreSQL, need to handle boolean vs integer
            if self.use_postgres:
                self._execute(cursor, 'UPDATE households SET is_active = CASE WHEN is_active = TRUE THEN FALSE ELSE TRUE END WHERE id = ?', (household_id,))
            else:
                self._execute(cursor, 'UPDATE households SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?', (household_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error toggling household status: {str(e)}")
            return False
    
    def delete_household(self, household_id):
        """Delete a household and all its users/data (super admin only)"""
        try:
            cursor = self.conn.cursor()
            
            # Get all users in the household
            self._execute(cursor, 'SELECT id FROM users WHERE household_id = ?', (household_id,))
            user_ids = [row['id'] for row in cursor.fetchall()]
            
            # Delete all user data
            for user_id in user_ids:
                self._execute(cursor, 'DELETE FROM expenses WHERE user_id = ?', (user_id,))
                self._execute(cursor, 'DELETE FROM allocations WHERE user_id = ?', (user_id,))
                self._execute(cursor, 'DELETE FROM income WHERE user_id = ?', (user_id,))
                self._execute(cursor, 'DELETE FROM monthly_settlements WHERE user_id = ?', (user_id,))
            
            # Delete users and household
            self._execute(cursor, 'DELETE FROM users WHERE household_id = ?', (household_id,))
            self._execute(cursor, 'DELETE FROM households WHERE id = ?', (household_id,))
            
            self.conn.commit()
            return (True, "Household deleted successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting household: {str(e)}")
            return (False, str(e))
    
    def get_all_users_super_admin(self):
        """Get all users across all households (for super admin)"""
        try:
            query = '''
                SELECT u.id, u.email, u.full_name, u.role, u.is_active,
                       h.name as household_name, u.created_at
                FROM users u
                LEFT JOIN households h ON u.household_id = h.id
                WHERE u.role != 'superadmin'
                ORDER BY h.name, u.role DESC, u.full_name
            '''
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            df = pd.read_sql_query(query, conn_to_use)
            print(f"DEBUG: get_all_users_super_admin returned {len(df)} rows")
            if not df.empty:
                print(f"DEBUG: First row: {df.iloc[0].to_dict()}")
            return df
        except Exception as e:
            print(f"Error fetching users: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_system_statistics(self):
        """Get system-wide statistics (for super admin)"""
        try:
            cursor = self.conn.cursor()
            
            stats = {}
            
            # Total households
            self._execute(cursor, 'SELECT COUNT(*) as count FROM households')
            stats['total_households'] = cursor.fetchone()['count']
            
            # Active households  
            is_active_value = True if self.use_postgres else 1
            self._execute(cursor, 'SELECT COUNT(*) as count FROM households WHERE is_active = ?', (is_active_value,))
            stats['active_households'] = cursor.fetchone()['count']
            
            # Total users (excluding super admin)
            self._execute(cursor, "SELECT COUNT(*) as count FROM users WHERE role != 'superadmin'")
            stats['total_users'] = cursor.fetchone()['count']
            
            # Total admins
            self._execute(cursor, "SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
            stats['total_admins'] = cursor.fetchone()['count']
            
            # Total members
            self._execute(cursor, "SELECT COUNT(*) as count FROM users WHERE role = 'member'")
            stats['total_members'] = cursor.fetchone()['count']
            
            return stats
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {}
    
    def promote_member_to_admin(self, user_id, household_id):
        """Promote a member to family admin (super admin only)"""
        try:
            cursor = self.conn.cursor()
            
            # Update user role to admin
            cursor.execute('''
                UPDATE users 
                SET role = 'admin', relationship = 'self'
                WHERE id = ? AND household_id = ?
            ''', (user_id, household_id))
            
            # Update household created_by if needed
            cursor.execute('SELECT created_by FROM households WHERE id = ?', (household_id,))
            result = cursor.fetchone()
            if result and not result['created_by']:
                cursor.execute('UPDATE households SET created_by = ? WHERE id = ?', (user_id, household_id))
            
            self.conn.commit()
            return (True, "User promoted to family admin successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error promoting user: {str(e)}")
            return (False, str(e))
    
    def add_member_to_family_super_admin(self, household_id, email, full_name, relationship):
        """Super admin adds member to any family"""
        try:
            cursor = self.conn.cursor()
            
            # Check if email exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return (False, None, "Email already exists")
            
            # Generate invite token
            invite_token = self.generate_invite_token()
            temp_password = secrets.token_urlsafe(16)
            password_hash = self._hash_password(temp_password)
            
            # Create member
            cursor.execute('''
                INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, invite_token, is_active)
                VALUES (?, ?, ?, ?, 'member', ?, ?, 1)
            ''', (household_id, email, password_hash, full_name, relationship, invite_token))
            
            member_id = cursor.lastrowid
            self.conn.commit()
            
            return (True, member_id, invite_token)
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding member: {str(e)}")
            return (False, None, str(e))
    
    
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
            self._execute(cursor, '''
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
            self._execute(cursor, '''
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
        """Get member-wise financial summary"""
        try:
            # Use appropriate parameter placeholder
            param_placeholder = '%s' if self.use_postgres else '?'
            query = f'''
                SELECT 
                    u.full_name as Member,
                    COALESCE(SUM(i.amount), 0) as Income,
                    COALESCE(SUM(e.amount), 0) as Expenses,
                    COALESCE(SUM(i.amount), 0) - COALESCE(SUM(e.amount), 0) as Savings
                FROM users u
                LEFT JOIN income i ON u.id = i.user_id
                LEFT JOIN expenses e ON u.id = e.user_id
                WHERE u.household_id = {param_placeholder}
                GROUP BY u.id, u.full_name
                ORDER BY u.full_name
            '''
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            df = pd.read_sql_query(query, conn_to_use, params=(household_id,))
            print(f"DEBUG: get_household_member_summary returned {len(df)} rows for household {household_id}")
            return df
        except Exception as e:
            print(f"Error getting member summary: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
