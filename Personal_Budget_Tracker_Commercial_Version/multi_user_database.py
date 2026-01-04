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
    
    def _ensure_connection(self):
        """Ensure database connection is alive, reconnect if needed"""
        if self.use_postgres:
            try:
                cursor = self.conn.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
            except:
                print("Connection lost, reconnecting...")
                import psycopg2
                from psycopg2.extras import RealDictCursor
                self.conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
                self.conn.autocommit = False
                print("✅ Reconnected to PostgreSQL")
    
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
        
        # Allocations table (with user_id and period support)
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
        
        # Savings table (with user_id)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS savings (
                id {id_type},
                user_id INTEGER NOT NULL,
                date {text_type} NOT NULL,
                category {text_type} NOT NULL,
                amount {'NUMERIC' if self.use_postgres else 'REAL'} NOT NULL,
                notes {text_type},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        
        # Run migrations to add period columns
        self._migrate_add_period_columns()
        
        # Run migration to add subcategory column
        self._migrate_add_subcategory_column()
        
        # Create super admin if it doesn't exist
        self._create_super_admin()
    
    def _migrate_add_period_columns(self):
        """Migrate existing tables to add year/month columns for period-based budgeting"""
        try:
            cursor = self.conn.cursor()
            from datetime import datetime
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # Check and add columns to allocations table
            if self.use_postgres:
                # PostgreSQL: Check if columns exist
                self._execute(cursor, """
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'allocations' AND column_name IN ('year', 'month')
                """)
                existing_cols = [row['column_name'] for row in cursor.fetchall()]
                
                if 'year' not in existing_cols:
                    print("🔄 Adding year column to allocations table...")
                    self._execute(cursor, f'ALTER TABLE allocations ADD COLUMN year INTEGER DEFAULT {current_year}')
                    self._execute(cursor, f'UPDATE allocations SET year = {current_year} WHERE year IS NULL')
                    self._execute(cursor, 'ALTER TABLE allocations ALTER COLUMN year SET NOT NULL')
                
                if 'month' not in existing_cols:
                    print("🔄 Adding month column to allocations table...")
                    self._execute(cursor, f'ALTER TABLE allocations ADD COLUMN month INTEGER DEFAULT {current_month}')
                    self._execute(cursor, f'UPDATE allocations SET month = {current_month} WHERE month IS NULL')
                    self._execute(cursor, 'ALTER TABLE allocations ALTER COLUMN month SET NOT NULL')
                
                # Update constraint if columns were added
                if 'year' not in existing_cols or 'month' not in existing_cols:
                    print("🔄 Updating allocations UNIQUE constraint for period-based budgeting...")
                    # Drop old constraint and create new one
                    try:
                        self._execute(cursor, 'ALTER TABLE allocations DROP CONSTRAINT IF EXISTS allocations_user_id_category_key')
                        self._execute(cursor, 'ALTER TABLE allocations DROP CONSTRAINT IF EXISTS allocations_user_id_category_year_month_key')
                    except:
                        pass  # Constraint might not exist
                    self._execute(cursor, 'ALTER TABLE allocations ADD CONSTRAINT allocations_user_id_category_year_month_key UNIQUE(user_id, category, year, month)')
            else:
                # SQLite: Check if columns exist
                cursor.execute("PRAGMA table_info(allocations)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'year' not in columns or 'month' not in columns:
                    print("🔄 Migrating allocations table to add period columns...")
                    # SQLite doesn't support dropping constraints, so we need to recreate the table
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS allocations_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            category TEXT NOT NULL,
                            year INTEGER NOT NULL,
                            month INTEGER NOT NULL,
                            allocated_amount REAL NOT NULL,
                            spent_amount REAL DEFAULT 0,
                            balance REAL NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id),
                            UNIQUE(user_id, category, year, month)
                        )
                    ''')
                    
                    # Copy data with default year/month
                    cursor.execute(f'''
                        INSERT INTO allocations_new (id, user_id, category, year, month, allocated_amount, spent_amount, balance, created_at, updated_at)
                        SELECT id, user_id, category, {current_year}, {current_month}, allocated_amount, spent_amount, balance, created_at, updated_at
                        FROM allocations
                    ''')
                    
                    # Replace old table
                    cursor.execute('DROP TABLE allocations')
                    cursor.execute('ALTER TABLE allocations_new RENAME TO allocations')
                    print("✅ Migrated allocations table successfully")
            
            # Check and add columns to expenses table
            if self.use_postgres:
                self._execute(cursor, """
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'expenses' AND column_name IN ('year', 'month')
                """)
                existing_cols = [row['column_name'] for row in cursor.fetchall()]
                
                if 'year' not in existing_cols:
                    print("🔄 Adding year column to expenses table...")
                    self._execute(cursor, f'ALTER TABLE expenses ADD COLUMN year INTEGER DEFAULT {current_year}')
                    self._execute(cursor, f'UPDATE expenses SET year = {current_year} WHERE year IS NULL')
                    self._execute(cursor, 'ALTER TABLE expenses ALTER COLUMN year SET NOT NULL')
                
                if 'month' not in existing_cols:
                    print("🔄 Adding month column to expenses table...")
                    self._execute(cursor, f'ALTER TABLE expenses ADD COLUMN month INTEGER DEFAULT {current_month}')
                    self._execute(cursor, f'UPDATE expenses SET month = {current_month} WHERE month IS NULL')
                    self._execute(cursor, 'ALTER TABLE expenses ALTER COLUMN month SET NOT NULL')
            else:
                # SQLite: Check if columns exist
                cursor.execute("PRAGMA table_info(expenses)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'year' not in columns or 'month' not in columns:
                    print("🔄 Migrating expenses table to add period columns...")
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS expenses_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            year INTEGER NOT NULL,
                            month INTEGER NOT NULL,
                            date TEXT NOT NULL,
                            category TEXT NOT NULL,
                            amount REAL NOT NULL,
                            comment TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        )
                    ''')
                    
                    # Copy data with default year/month
                    cursor.execute(f'''
                        INSERT INTO expenses_new (id, user_id, year, month, date, category, amount, comment, created_at, updated_at)
                        SELECT id, user_id, {current_year}, {current_month}, date, category, amount, comment, created_at, updated_at
                        FROM expenses
                    ''')
                    
                    # Replace old table
                    cursor.execute('DROP TABLE expenses')
                    cursor.execute('ALTER TABLE expenses_new RENAME TO expenses')
                    print("✅ Migrated expenses table successfully")
            
            self.conn.commit()
            print("✅ Period columns migration completed successfully")
            
        except Exception as e:
            print(f"⚠️ Migration error (might be already migrated): {str(e)}")
            self.conn.rollback()
    
    def _migrate_add_subcategory_column(self):
        """Add subcategory column to expenses table if it doesn't exist"""
        try:
            cursor = self.conn.cursor()
            
            if self.use_postgres:
                # PostgreSQL: Check if column exists
                self._execute(cursor, """
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'expenses' AND column_name = 'subcategory'
                """)
                existing_cols = [row['column_name'] for row in cursor.fetchall()]
                
                if 'subcategory' not in existing_cols:
                    print("🔄 Adding subcategory column to expenses table...")
                    self._execute(cursor, 'ALTER TABLE expenses ADD COLUMN subcategory TEXT')
                    print("✅ Added subcategory column to expenses table")
            else:
                # SQLite: Check if column exists
                cursor.execute("PRAGMA table_info(expenses)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'subcategory' not in columns:
                    print("🔄 Adding subcategory column to expenses table...")
                    cursor.execute('ALTER TABLE expenses ADD COLUMN subcategory TEXT')
                    print("✅ Added subcategory column to expenses table")
            
            self.conn.commit()
            print("✅ Subcategory column migration completed successfully")
            
        except Exception as e:
            print(f"⚠️ Subcategory migration error (might be already migrated): {str(e)}")
            self.conn.rollback()
    
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
            # Ensure connection is alive
            self._ensure_connection()
            
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
                if 'email' in error_msg.lower():
                    return (False, "DUPLICATE_EMAIL", None)
                return (False, "DUPLICATE_ENTRY", None)
            else:
                # Other error - log it
                import traceback
                traceback.print_exc()
                return (False, "ERROR", None)
    
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
            self._execute(cursor, '''
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
            self._execute(cursor, 'DELETE FROM expenses WHERE user_id = ?', (member_id,))
            self._execute(cursor, 'DELETE FROM allocations WHERE user_id = ?', (member_id,))
            self._execute(cursor, 'DELETE FROM income WHERE user_id = ?', (member_id,))
            self._execute(cursor, 'DELETE FROM monthly_settlements WHERE user_id = ?', (member_id,))
            
            # Finally, delete the user account (this also invalidates the invite token)
            self._execute(cursor, 'DELETE FROM users WHERE id = ? AND role != ?', (member_id, 'admin'))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting member: {str(e)}")
            import traceback
            traceback.print_exc()
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
    
    def create_household_with_admin(self, household_name, admin_email, admin_name):
        """Super admin creates a new household with a family admin (using invite token)"""
        try:
            cursor = self.conn.cursor()
            
            # Check if email already exists
            self._execute(cursor, 'SELECT id FROM users WHERE email = ?', (admin_email,))
            if cursor.fetchone():
                return (False, None, None, "Email already exists")
            
            # Create household - use RETURNING for PostgreSQL
            is_active_value = True if self.use_postgres else 1
            if self.use_postgres:
                self._execute(cursor, 'INSERT INTO households (name, is_active) VALUES (?, ?) RETURNING id', (household_name, is_active_value))
                household_id = cursor.fetchone()['id']
            else:
                self._execute(cursor, 'INSERT INTO households (name, is_active) VALUES (?, ?)', (household_name, is_active_value))
                household_id = cursor.lastrowid
           
            # Generate invite token for admin
            invite_token = self.generate_invite_token()
            
            # Generate temporary password (will be replaced when admin uses invite token)
            temp_password = secrets.token_urlsafe(16)
            password_hash = self._hash_password(temp_password)
            
            # Create admin user with invite token - use RETURNING for PostgreSQL
            if self.use_postgres:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, is_active, invite_token)
                    VALUES (?, ?, ?, ?, 'admin', 'self', ?, ?)
                    RETURNING id
                ''', (household_id, admin_email, password_hash, admin_name, is_active_value, invite_token))
                admin_id = cursor.fetchone()['id']
            else:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, is_active, invite_token)
                    VALUES (?, ?, ?, ?, 'admin', 'self', ?, ?)
                ''', (household_id, admin_email, password_hash, admin_name, is_active_value, invite_token))
                admin_id = cursor.lastrowid
            
            # Update household created_by
            self._execute(cursor, 'UPDATE households SET created_by = ? WHERE id = ?', (admin_id, household_id))
            
            self.conn.commit()
            return (True, household_id, invite_token, f"Household '{household_name}' created successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating household: {str(e)}")
            return (False, None, None, str(e))
    
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
            self._execute(cursor, '''
                UPDATE users 
                SET role = 'admin', relationship = 'self'
                WHERE id = ? AND household_id = ?
            ''', (user_id, household_id))
            
            # Update household created_by if needed
            self._execute(cursor, 'SELECT created_by FROM households WHERE id = ?', (household_id,))
            result = cursor.fetchone()
            if result and not result['created_by']:
                self._execute(cursor, 'UPDATE households SET created_by = ? WHERE id = ?', (user_id, household_id))
            
            self.conn.commit()
            return (True, "User promoted to family admin successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error promoting user: {str(e)}")
            return (False, str(e))
    
    def demote_admin_to_member(self, user_id, household_id):
        """Demote an admin to member role (enforces at-least-one-admin rule)"""
        try:
            cursor = self.conn.cursor()
            
            # Count current admins in household
            is_active_value = True if self.use_postgres else 1
            self._execute(cursor, 
                "SELECT COUNT(*) as count FROM users WHERE household_id = ? AND role = 'admin' AND is_active = ?",
                (household_id, is_active_value))
            result = cursor.fetchone()
            admin_count = result['count'] if result else 0
            
            # Prevent demotion if only one admin
            if admin_count <= 1:
                return (False, "Cannot demote the only admin. Promote another member first.")
            
            # Demote to member
            self._execute(cursor, 
                "UPDATE users SET role = 'member' WHERE id = ? AND household_id = ?",
                (user_id, household_id))
            
            self.conn.commit()
            return (True, "Admin demoted to member successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error demoting admin: {str(e)}")
            return (False, str(e))
    
    def count_household_admins(self, household_id):
        """Count active admins in a household"""
        try:
            cursor = self.conn.cursor()
            is_active_value = True if self.use_postgres else 1
            self._execute(cursor,
                "SELECT COUNT(*) as count FROM users WHERE household_id = ? AND role = 'admin' AND is_active = ?",
                (household_id, is_active_value))
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting admins: {str(e)}")
            return 0
    
    def reset_user_password(self, user_id):
        """Reset user password and generate new invite token (for admins to force password reset)"""
        try:
            cursor = self.conn.cursor()
            
            # Generate new invite token
            new_token = self.generate_invite_token()
            
            # Generate temp password (user must use token to set real password)
            temp_password = secrets.token_urlsafe(16)
            password_hash = self._hash_password(temp_password)
            
            # Update user with new token and temp password (invalidates old password)
            self._execute(cursor, '''
                UPDATE users 
                SET password_hash = ?, invite_token = ?
                WHERE id = ?
            ''', (password_hash, new_token, user_id))
            
            self.conn.commit()
            return (True, new_token, "Password reset successfully")
        except Exception as e:
            self.conn.rollback()
            print(f"Error resetting password: {str(e)}")
            return (False, None, str(e))
    
    def add_member_to_family_super_admin(self, household_id, email, full_name, relationship):
        """Super admin adds a new member to a family"""
        try:
            cursor = self.conn.cursor()
            
            # Check if email already exists
            self._execute(cursor, 'SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return (False, None, "Email already exists")
            
            # Generate temporary password and invite token
            temp_password = secrets.token_urlsafe(16)
            password_hash = self._hash_password(temp_password)
            invite_token = self.generate_invite_token()
            
            # Create member with appropriate method for database type
            is_active_value = True if self.use_postgres else 1
            if self.use_postgres:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, invite_token, is_active)
                    VALUES (?, ?, ?, ?, 'member', ?, ?, ?)
                    RETURNING id
                ''', (household_id, email, password_hash, full_name, relationship, invite_token, is_active_value))
                member_id = cursor.fetchone()['id']
            else:
                self._execute(cursor, '''
                    INSERT INTO users (household_id, email, password_hash, full_name, role, relationship, invite_token, is_active)
                    VALUES (?, ?, ?, ?, 'member', ?, ?, ?)
                ''', (household_id, email, password_hash, full_name, relationship, invite_token, is_active_value))
                member_id = cursor.lastrowid
            
            self.conn.commit()
            return (True, member_id, invite_token)
        except Exception as e:
            print(f"Error adding member to family: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return (False, None, str(e))
    
    
    # ==================== INCOME OPERATIONS (USER-SCOPED) ====================
    
    def add_income(self, user_id, date, source, amount):
        """Add a new income entry for a user"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor,
                'INSERT INTO income (user_id, date, source, amount) VALUES (?, ?, ?, ?)',
                (user_id, date, source, float(amount))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding income: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
    
    def get_all_income(self, user_id):
        """Get all income entries for a user"""
        try:
            query = 'SELECT date as "Date", source as "Source", amount as "Amount" FROM income WHERE user_id = ? ORDER BY date DESC'
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            if self.use_postgres and self.engine:
                # For PostgreSQL, replace ? with parameter placeholder
                query = 'SELECT date as "Date", source as "Source", amount as "Amount" FROM income WHERE user_id = %s ORDER BY date DESC'
            df = pd.read_sql_query(query, conn_to_use, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching income: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=["Date", "Source", "Amount"])
    
    def get_income_with_ids(self, user_id):
        """Get all income entries with IDs for editing"""
        try:
            query = 'SELECT id, date, source, amount FROM income WHERE user_id = ? ORDER BY date DESC'
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            if self.use_postgres and self.engine:
                # For PostgreSQL, replace ? with parameter placeholder
                query = 'SELECT id, date, source, amount FROM income WHERE user_id = %s ORDER BY date DESC'
            df = pd.read_sql_query(query, conn_to_use, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching income with IDs: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=["id", "date", "source", "amount"])

    
    def update_income(self, income_id, user_id, date, source, amount):
        """Update an existing income entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor,
                'UPDATE income SET date = ?, source = ?, amount = ? WHERE id = ? AND user_id = ?',
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
            self._execute(cursor, 'DELETE FROM income WHERE id = ? AND user_id = ?', (income_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting income: {str(e)}")
            return False
    
    def get_total_income(self, user_id, year, month):
        """Get total income amount for a specific user and period"""
        try:
            cursor = self.conn.cursor()
            # Income dates are stored as strings in format YYYY-MM-DD
            # Filter by year and month using LIKE pattern matching
            year_month_pattern = f"{year}-{month:02d}-%"
            self._execute(cursor, '''
                SELECT SUM(amount) as total
                FROM income
                WHERE user_id = ? AND date LIKE ?
            ''', (user_id, year_month_pattern))
            result = cursor.fetchone()
            return float(result['total']) if result and result['total'] else 0.0
        except Exception as e:
            print(f"Error getting total income: {str(e)}")
            return 0.0
    
    # ==================== ALLOCATION OPERATIONS (USER-SCOPED) ====================
    
    def add_allocation(self, user_id, category, allocated_amount, year, month):
        """Add a new allocation for a category with period"""
        try:
            cursor = self.conn.cursor()
            balance = allocated_amount
            self._execute(cursor,
                'INSERT INTO allocations (user_id, category, year, month, allocated_amount, spent_amount, balance) VALUES (?, ?, ?, ?, ?, 0, ?)',
                (user_id, category, year, month, float(allocated_amount), float(balance))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding allocation: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
    
    def get_all_allocations(self, user_id, year=None, month=None):
        """Get all allocations for a user, optionally filtered by period"""
        try:
            if year and month:
                query = '''
                    SELECT 
                        category as "Category", 
                        allocated_amount as "Allocated Amount", 
                        spent_amount as "Spent Amount", 
                        balance as "Balance" 
                    FROM allocations 
                    WHERE user_id = ? AND year = ? AND month = ?
                    ORDER BY category
                '''
                params = (user_id, year, month)
            else:
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
                params = (user_id,)
            
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            if self.use_postgres and self.engine:
                query = query.replace('?', '%s')
            df = pd.read_sql_query(query, conn_to_use, params=params)
            return df
        except Exception as e:
            print(f"Error fetching allocations: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=["Category", "Allocated Amount", "Spent Amount", "Balance"])
    
    def get_categories(self, user_id, year=None, month=None):
        """Get list of all allocation categories for a user, optionally filtered by period"""
        try:
            cursor = self.conn.cursor()
            if year and month:
                self._execute(cursor, 'SELECT DISTINCT category FROM allocations WHERE user_id = ? AND year = ? AND month = ? ORDER BY category', (user_id, year, month))
            else:
                self._execute(cursor, 'SELECT DISTINCT category FROM allocations WHERE user_id = ? ORDER BY category', (user_id,))
            rows = cursor.fetchall()
            return [row['category'] for row in rows]
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return []
    
    def get_past_allocations(self, user_id, exclude_year, exclude_month):
        """Get distinct allocation categories from past 6 months (excluding current period)"""
        try:
            from datetime import datetime, timedelta
            cursor = self.conn.cursor()
            
            # Calculate date 6 months ago
            current_date = datetime(exclude_year, exclude_month, 1)
            six_months_ago = current_date - timedelta(days=180)
            
            # Get allocations from past 6 months, excluding current period
            self._execute(cursor, '''
                SELECT DISTINCT category, allocated_amount, year, month
                FROM allocations
                WHERE user_id = ?
                  AND NOT (year = ? AND month = ?)
                  AND ((year > ?) OR (year = ? AND month >= ?))
                ORDER BY year DESC, month DESC, category
            ''', (user_id, 
                  exclude_year, exclude_month,
                  six_months_ago.year, six_months_ago.year, six_months_ago.month))
            
            results = cursor.fetchall()
            
            # Get unique categories (most recent occurrence)
            seen_categories = set()
            unique_allocations = []
            for row in results:
                if row['category'] not in seen_categories:
                    unique_allocations.append({
                        'category': row['category'],
                        'amount': float(row['allocated_amount'])
                    })
                    seen_categories.add(row['category'])
            
            return unique_allocations
        except Exception as e:
            print(f"Error getting past allocations: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_allocations_with_ids(self, user_id, year=None, month=None):
        """Get all allocations with IDs for editing, optionally filtered by period"""
        try:
            if year and month:
                query = 'SELECT id, category, year, month, allocated_amount, spent_amount, balance FROM allocations WHERE user_id = ? AND year = ? AND month = ? ORDER BY category'
                params = (user_id, year, month)
            else:
                query = 'SELECT id, category, year, month, allocated_amount, spent_amount, balance FROM allocations WHERE user_id = ? ORDER BY category'
                params = (user_id,)
            
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            if self.use_postgres and self.engine:
                query = query.replace('?', '%s')
            df = pd.read_sql_query(query, conn_to_use, params=params)
            return df
        except Exception as e:
            print(f"Error fetching allocations with IDs: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=["id", "category", "year", "month", "allocated_amount", "spent_amount", "balance"])

    
    def update_allocation(self, allocation_id, user_id, category, allocated_amount, year, month):
        """Update an allocation entry by ID with period"""
        try:
            cursor = self.conn.cursor()
            
            # Get current spent amount
            self._execute(cursor,
                'SELECT spent_amount FROM allocations WHERE id = ? AND user_id = ?',
                (allocation_id, user_id)
            )
            result = cursor.fetchone()
            if not result:
                return False
                
            spent_amount = float(result['spent_amount'])
            new_balance = float(allocated_amount) - spent_amount
            
            # Update the allocation with year/month
            self._execute(cursor,
                'UPDATE allocations SET category = ?, year = ?, month = ?, allocated_amount = ?, balance = ? WHERE id = ? AND user_id = ?',
                (category, year, month, float(allocated_amount), new_balance, allocation_id, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating allocation: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
    
    def update_allocation_spent(self, user_id, category, expense_amount):
        """Update spent amount and balance for a category when expense is added"""
        try:
            cursor = self.conn.cursor()
            
            self._execute(cursor,
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            row = cursor.fetchone()
            
            if not row:
                print(f"Category '{category}' not found")
                return False
            
            allocated = float(row['allocated_amount'])
            current_spent = float(row['spent_amount'])
            
            new_spent = current_spent + float(expense_amount)
            new_balance = allocated - new_spent
            
            self._execute(cursor,
                'UPDATE allocations SET spent_amount = ?, balance = ? WHERE user_id = ? AND category = ?',
                (new_spent, new_balance, user_id, category)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating allocation: {str(e)}")
            import traceback
            traceback.print_exc()
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
            
            current_spent = float(row['spent_amount'])
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
    
    def delete_allocation_by_id(self, allocation_id, user_id):
        """Delete an allocation by ID"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, 'DELETE FROM allocations WHERE id = ? AND user_id = ?', (allocation_id, user_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting allocation: {str(e)}")
            return False
    
    # ==================== EXPENSE OPERATIONS (USER-SCOPED) ====================
    
    def add_expense(self, user_id, date, category, amount, comment, subcategory=None):
        """Add a new expense and auto-update allocation"""
        try:
            cursor = self.conn.cursor()
            
            self._execute(cursor,
                'INSERT INTO expenses (user_id, date, category, amount, comment, subcategory) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, date, category, float(amount), comment, subcategory)
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
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            if self.use_postgres and self.engine:
                query = query.replace('?', '%s')
            df = pd.read_sql_query(query, conn_to_use, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching expenses: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Comment"])
    
    def get_total_expenses(self, user_id):
        """Calculate total expenses for a user"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, 'SELECT SUM(amount) as total FROM expenses WHERE user_id = ?', (user_id,))
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
            query = 'SELECT id, date, category, amount, subcategory, comment FROM expenses WHERE user_id = ? ORDER BY date DESC'
            # Use engine for pandas queries if PostgreSQL
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            if self.use_postgres and self.engine:
                # For PostgreSQL, replace ? with parameter placeholder
                query = 'SELECT id, date, category, amount, subcategory, comment FROM expenses WHERE user_id = %s ORDER BY date DESC'
            df = pd.read_sql_query(query, conn_to_use, params=(user_id,))
            return df
        except Exception as e:
            print(f"Error fetching expenses with IDs: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=["id", "date", "category", "amount", "subcategory", "comment"])

    
    def update_expense(self, expense_id, user_id, date, category, amount, old_category, old_amount, comment, subcategory=None):
        """Update an existing expense and adjust allocations"""
        # This method has complex logic with allocation updates - needs comprehensive fixing
        # For now, adding traceback to help debug
        try:
            cursor = self.conn.cursor()
            
            # Get old allocation
            self._execute(cursor,
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, old_category)
            )
            old_row = cursor.fetchone()
            if old_row:
                old_allocated = float(old_row['allocated_amount'])
                old_spent = float(old_row['spent_amount'])
                new_old_spent = old_spent - float(old_amount)
                new_old_balance = old_allocated - new_old_spent
                self._execute(cursor,
                    'UPDATE allocations SET spent_amount = ?, balance = ? WHERE user_id = ? AND category = ?',
                    (new_old_spent, new_old_balance, user_id, old_category)
                )
            
            # Get new allocation  
            self._execute(cursor,
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            new_row = cursor.fetchone()
            if new_row:
                new_allocated = float(new_row['allocated_amount'])
                new_spent = float(new_row['spent_amount'])
                new_new_spent = new_spent + float(amount)
                new_new_balance = new_allocated - new_new_spent
                self._execute(cursor,
                    'UPDATE allocations SET spent_amount = ?, balance = ? WHERE user_id = ? AND category = ?',
                    (new_new_spent, new_new_balance, user_id, category)
                )
            
            # Update expense
            self._execute(cursor,
                'UPDATE expenses SET date = ?, category = ?, amount = ?, comment = ?, subcategory = ? WHERE id = ? AND user_id = ?',
                (date, category, float(amount), comment, subcategory, expense_id, user_id)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating expense: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
    
    def delete_expense(self, expense_id, user_id, category, amount):
        """Delete an expense and update allocation"""
        try:
            cursor = self.conn.cursor()
            
            self._execute(cursor,
                'SELECT allocated_amount, spent_amount FROM allocations WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            row = cursor.fetchone()
            if row:
                allocated = float(row['allocated_amount'])
                spent = float(row['spent_amount'])
                new_spent = spent - float(amount)
                new_balance = allocated - new_spent
                self._execute(cursor,
                    'UPDATE allocations SET spent_amount = ?, balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND category = ?',
                    (new_spent, new_balance, user_id, category)
                )
            
            self._execute(cursor, 'DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
            
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
    
    
    def execute_chatbot_query(self, sql_query: str, user_id: int, family_id: int, role: str):
        """
        Execute a safe, read-only query for the chatbot
        
        Args:
            sql_query: SQL query to execute (must be SELECT only)
            user_id: Current user's ID
            family_id: User's household ID
            role: User's role ('member', 'admin', 'superadmin')
        
        Returns:
            List of result rows or error message
        """
        try:
            # Security validations
            sql_upper = sql_query.upper().strip()
            
            # Must be SELECT only
            if not sql_upper.startswith("SELECT"):
                return {"error": "Only SELECT queries are allowed"}
            
            # Block dangerous keywords
            dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "EXECUTE", "--"]
            if any(keyword in sql_upper for keyword in dangerous_keywords):
                return {"error": "Query contains forbidden operations"}
            
            # Execute query
            self._ensure_connection()
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            
            # Fetch results
            results = cursor.fetchall()
            
            # Convert to list of dicts
            if self.use_postgres:
                # RealDictCursor already returns dicts
                return [dict(row) for row in results]
            else:
                # SQLite Row factory
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"❌ Chatbot query error: {e}")
            return {"error": f"Query execution failed: {str(e)}"}
    
    # ==================== SAVINGS MANAGEMENT ====================
    
    def add_saving(self, user_id, date, category, amount, notes):
        """Add a new saving entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, '''
                INSERT INTO savings (user_id, date, category, amount, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, date, category, amount, notes))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding saving: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_all_savings(self, user_id, year=None, month=None):
        """Get all savings for a user, optionally filtered by period"""
        try:
            param_placeholder = '%s' if self.use_postgres else '?'
            
            if year and month:
                # Filter by specific month
                query = f'''
                    SELECT date, category, amount, notes
                    FROM savings
                    WHERE user_id = {param_placeholder}
                    AND strftime('%Y', date) = {param_placeholder}
                    AND strftime('%m', date) = {param_placeholder}
                    ORDER BY date DESC
                '''
                params = (user_id, str(year), f'{month:02d}')
            else:
                # Get all savings
                query = f'''
                    SELECT date, category, amount, notes
                    FROM savings
                    WHERE user_id = {param_placeholder}
                    ORDER BY date DESC
                '''
                params = (user_id,)
            
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            df = pd.read_sql_query(query, conn_to_use, params=params)
            
            # Format columns for display
            if not df.empty:
                df['Date'] = df['date']
                df['Category'] = df['category']
                df['Amount'] = df['amount'].apply(lambda x: float(x))
                df['Notes'] = df['notes'].fillna('')
                df = df[['Date', 'Category', 'Amount', 'Notes']]
            
            return df
        except Exception as e:
            print(f"Error fetching savings: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_savings_with_ids(self, user_id, year=None, month=None):
        """Get savings with IDs for editing"""
        try:
            param_placeholder = '%s' if self.use_postgres else '?'
            
            if year and month:
                query = f'''
                    SELECT id, date, category, amount, notes
                    FROM savings
                    WHERE user_id = {param_placeholder}
                    AND strftime('%Y', date) = {param_placeholder}
                    AND strftime('%m', date) = {param_placeholder}
                    ORDER BY date DESC
                '''
                params = (user_id, str(year), f'{month:02d}')
            else:
                query = f'''
                    SELECT id, date, category, amount, notes
                    FROM savings
                    WHERE user_id = {param_placeholder}
                    ORDER BY date DESC
                '''
                params = (user_id,)
            
            conn_to_use = self.engine if (self.use_postgres and self.engine) else self.conn
            df = pd.read_sql_query(query, conn_to_use, params=params)
            return df
        except Exception as e:
            print(f"Error fetching savings with IDs: {str(e)}")
            return pd.DataFrame()
    
    def update_saving(self, saving_id, date, category, amount, notes):
        """Update an existing saving entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, '''
                UPDATE savings
                SET date = ?, category = ?, amount = ?, notes = ?
                WHERE id = ?
            ''', (date, category, amount, notes, saving_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating saving: {str(e)}")
            self.conn.rollback()
            return False
    
    def delete_saving(self, saving_id):
        """Delete a saving entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, 'DELETE FROM savings WHERE id = ?', (saving_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting saving: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_total_savings(self, user_id, year=None, month=None):
        """Get total savings amount for a user, optionally filtered by period"""
        try:
            cursor = self.conn.cursor()
            param_placeholder = '%s' if self.use_postgres else '?'
            
            if year and month:
                query = f'''
                    SELECT SUM(amount) as total
                    FROM savings
                    WHERE user_id = {param_placeholder}
                    AND strftime('%Y', date) = {param_placeholder}
                    AND strftime('%m', date) = {param_placeholder}
                '''
                self._execute(cursor, query, (user_id, str(year), f'{month:02d}'))
            else:
                query = f'''
                    SELECT SUM(amount) as total
                    FROM savings
                    WHERE user_id = {param_placeholder}
                '''
                self._execute(cursor, query, (user_id,))
            
            result = cursor.fetchone()
            return float(result['total']) if result and result['total'] else 0.0
        except Exception as e:
            print(f"Error calculating total savings: {str(e)}")
            return 0.0
    
    # ==================== INCOME MANAGEMENT (Mobile API Support) ====================
    
    def add_income(self, user_id, date, source, amount):
        """Add a new income entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, '''
                INSERT INTO income (user_id, date, source, amount)
                VALUES (?, ?, ?, ?)
            ''', (user_id, date, source, amount))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding income: {str(e)}")
            self.conn.rollback()
            return False
    
    def delete_income(self, income_id):
        """Delete an income entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, 'DELETE FROM income WHERE id = ?', (income_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting income: {str(e)}")
            self.conn.rollback()
            return False
    
    # ==================== EXPENSE MANAGEMENT (Mobile API Support) ====================
    
    def add_expense(self, user_id, date, category, amount, comment=None, subcategory=None):
        """Add a new expense entry"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, '''
                INSERT INTO expenses (user_id, date, category, subcategory, amount, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, date, category, subcategory, amount, comment))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def update_expense(self, expense_id, user_id_or_date=None, date_or_category=None, 
                      category_or_subcategory=None, amount=None, old_category_or_comment=None,
                      old_amount=None, comment=None, subcategory=None):
        """Update an existing expense entry (supports both old and new signatures)"""
        try:
            cursor = self.conn.cursor()
            
            # Detect which signature is being used
            if old_amount is not None:
                # Website signature: (expense_id, user_id, new_date, new_category, new_amount, 
                #                     old_category, old_amount, new_comment, new_subcategory)
                date = date_or_category
                category = category_or_subcategory
                # amount is already correct
                comment = comment or old_category_or_comment  # Use new_comment if provided
                subcategory = subcategory
            else:
                # Mobile API signature: (expense_id, date, category, subcategory, amount, comment)
                date = user_id_or_date
                category = date_or_category
                subcategory = category_or_subcategory
                # amount is already correct
                comment = old_category_or_comment
            
            self._execute(cursor, '''
                UPDATE expenses
                SET date = ?, category = ?, subcategory = ?, amount = ?, comment = ?
                WHERE id = ?
            ''', (date, category, subcategory, amount, comment, expense_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def delete_expense(self, expense_id, user_id=None, category=None, amount=None):
        """Delete an expense entry (supports both old and new signatures)"""
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, 'DELETE FROM expenses WHERE id = ?', (expense_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting expense: {str(e)}")
            self.conn.rollback()
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
