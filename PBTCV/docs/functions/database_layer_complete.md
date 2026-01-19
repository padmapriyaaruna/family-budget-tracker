# Database Layer - Complete Documentation

**File:** `multi_user_database.py`  
**Lines:** 2,341  
**Class:** MultiUserDB  
**Purpose:** All database operations with PostgreSQL/SQLite support

---

## Overview

**What It Is:**
The database layer handles ALL data storage and retrieval for the application.

**Dual Database Support:**
- **Production:** PostgreSQL (Render deployment)
- **Development:** SQLite (local file)

**Key Features:**
- 58 public methods
- Automatic connection management
- Role-based data isolation
- Password hashing
- Invite token system

---

## Database Schema

### Tables

**1. households** - Family groups
```sql
id, name, created_by, is_active, created_at
```

**2. users** - All user accounts
```sql
id, household_id, email, password_hash, full_name, role, 
relationship, is_active, invite_token, created_at
```

**3. income** - Income records
```sql
id, user_id, date, source,amount, created_at, updated_at
```

**4. allocations** - Budget allocations
```sql
id, user_id, category, year, month, allocated_amount, 
spent_amount, balance, created_at, updated_at
```

**5. expenses** - Expenses
```sql
id, user_id, year, month, date, category, subcategory, 
amount, comment, created_at, updated_at
```

---

## Core Methods

### Authentication

**`authenticate_user(email, password)`**
- Hashes password with SHA-256
- Queries users table
- Returns (success: bool, user_data: dict)

**`_hash_password(password)`**
- SHA-256 hashing
- Returns hexadecimal string

**`generate_invite_token()`**
- Creates random URL-safe token
- 32 bytes = 43 characters

**`accept_invite(invite_token, new_password)`**
- Finds user by token
- Sets new password
- Clears invite token

---

## Allocation Methods ✨ (v6.1 Key Methods)

### `add_allocation(user_id, category, allocated_amount, year, month)`

**Creates new budget allocation**

```sql
INSERT INTO allocations 
(user_id, category, allocated_amount, spent_amount, balance, year, month)
VALUES (?, ?, ?, 0, ?, ?, ?)
```

### `update_allocation(allocation_id, user_id, category, allocated_amount, year, month)` ✨

**v6.1 Fix: Now includes all required parameters**

```python
def update_allocation(self, allocation_id, user_id, category, allocated_amount, year, month):
    cursor = self.conn.cursor()
    
    # Calculate current spent amount
    spent = self.get_allocation_spent_amount(user_id, category, year, month)
    balance = allocated_amount - spent
    
    # Update allocation
    self._execute(cursor, '''
        UPDATE allocations 
        SET category = ?, allocated_amount = ?, balance = ?, year = ?, month = ?
        WHERE id = ? AND user_id = ?
    ''', (category, allocated_amount, balance, year, month, allocation_id, user_id))
    
    self.conn.commit()
    return cursor.rowcount > 0
```

**Why v6.1 Fix Matters:**
- Before: Only updated category & amount
- After: Updates year, month, verifies user ownership
- Prevents unauthorized edits

### `update_allocation_spent_amount(user_id, category, year, month)` 

**Auto-syncs spent amount with actual expenses**

```python
def update_allocation_spent_amount(self, user_id, category, year, month):
    # Get total expenses for this category
    cursor = self.conn.cursor()
    self._execute(cursor, '''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE user_id = ? AND category = ? AND year = ? AND month = ?
    ''', (user_id, category, year, month))
    
    result = cursor.fetchone()
    spent = float(result['total'])
    
    # Update allocation
    self._execute(cursor, '''
        UPDATE allocations
        SET spent_amount = ?,
            balance = allocated_amount - ?
        WHERE user_id = ? AND category = ? AND year = ? AND month = ?
    ''', (spent, spent, user_id, category, year, month))
    
    self.conn.commit()
```

**When Called:**
- After adding expense
- After updating expense
- After deleting expense
- Manual recalculation

---

## Expense Methods

### `add_expense(user_id, date, category, subcategory, amount, comment, year, month)`

```python
def add_expense(self, user_id, date, category, subcategory, amount, comment, year, month):
    cursor = self.conn.cursor()
    
    # Insert expense
    self._execute(cursor, '''
        INSERT INTO expenses 
        (user_id, date, category, subcategory, amount, comment, year, month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, category, subcategory, amount, comment, year, month))
    
    self.conn.commit()
    
    # Auto-update allocation spent amount
    self.update_allocation_spent_amount(user_id, category, year, month)
    
    return True
```

**Automatic Cascade:**
1. Expense added
2. `update_allocation_spent_amount()` called automatically
3. Allocation updated
4. Balance recalculated

---

## Income Methods

### `add_income(user_id, date, source, amount)`

```sql
INSERT INTO income (user_id, date, source, amount)
VALUES (?, ?, ?, ?)
```

### `get_income(user_id, year=None, month=None)`

```python
def get_income(self, user_id, year=None, month=None):
    query = 'SELECT * FROM income WHERE user_id = ?'
    params = [user_id]
    
    if year:
        query += ' AND CAST(strftime("%Y", date) AS INTEGER) = ?'
        params.append(year)
    if month:
        query += ' AND CAST(strftime("%m", date) AS INTEGER) = ?'
        params.append(month)
    
    query += ' ORDER BY date DESC'
    
    df = pd.read_sql_query(query, self.conn, params=params)
    return df
```

---

## Super Admin Methods

### `get_all_households()`

**Returns all families with member counts**

```sql
SELECT h.id, h.name, h.is_active, h.created_at,
       u.full_name as admin_name, u.email as admin_email,
       COUNT(DISTINCT m.id) as member_count
FROM households h
LEFT JOIN users u ON h.created_by = u.id
LEFT JOIN users m ON m.household_id = h.id
GROUP BY h.id, h.name, h.is_active, h.created_at, u.full_name, u.email
ORDER BY h.created_at DESC
```

### `create_household_with_admin(household_name, admin_email, admin_name)`

**Creates family + admin with invite token**

```python
def create_household_with_admin(self, household_name, admin_email, admin_name):
    # 1. Create household
    # 2. Generate invite token
    # 3. Create admin user (with token)
    # 4. Return token for setup
    return (success, household_id, invite_token, message)
```

---

## Connection Management

### `_ensure_connection()`

**Checks and reconnects if needed**

```python
def _ensure_connection(self):
    if self.use_postgres:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
        except:
            print("Connection lost, reconnecting...")
            self.conn = psycopg2.connect(DATABASE_URL)
            print("✅ Reconnected")
```

### `_execute(cursor, query, params=None)`

**Executes queries with auto parameter conversion**

```python
def _execute(self, cursor, query, params=None):
    if self.use_postgres:
        query = query.replace('?', '%s')  # Convert placeholders
    
    try:
        cursor.execute(query, params)
    except ConnectionError:
        self._reconnect()
        cursor.execute(query, params)
    
    return cursor
```

**Why This Matters:**
- SQLite uses `?` placeholders
- PostgreSQL uses `%s` placeholders
- This function handles both automatically

---

## Data Isolation

**All queries filter by user_id:**

```python
# Members see only their data
query = 'SELECT * FROM expenses WHERE user_id = ?'

# Admins see household data
query = '''
    SELECT * FROM expenses 
    WHERE user_id IN (SELECT id FROM users WHERE household_id = ?)
'''

# Super admin sees everything
query = 'SELECT * FROM expenses'
```

---

## Complete Method List (58 Total)

### Authentication (6)
- `_hash_password()`
- `_create_super_admin()`
- `create_admin_user()`
- `authenticate_user()`
- `generate_invite_token()`
- `accept_invite()`

### Member Management (6)
- `create_member()`
- `get_household_members()`
- `get_user_by_id()`
- `deactivate_member()`
- `delete_member()`

### Household Management (6)
- `get_all_households()`
- `create_household_with_admin()`
- `toggle_household_status()`
- `delete_household()`
- `get_household_members_for_admin()`
- `get_system_statistics()`

### User Management (4)
- `get_all_users_super_admin()`
- `promote_member_to_admin()`
- `demote_admin_to_member()`
- `count_household_admins()`

### Income Operations (5)
- `add_income()`
- `get_income()`
- `get_all_income()`
- `update_income()`
- `delete_income()`

### Allocation Operations (9) ✨
- `add_allocation()`
- `get_all_allocations()`
- `get_categories()`
- `get_allocation_spent_amount()`
- `update_allocation()` ← v6.1 fixed
- `update_allocation_spent_amount()` ← key method
- `delete_allocation()`
- `delete_allocation_by_id()`
- `copy_previous_month_allocations()`

### Expense Operations (6)
- `add_expense()`
- `get_expenses()`
- `get_all_expenses()`
- `update_expense()`
- `delete_expense()`
- `get_category_expenses()`

### Analytics & Reports (8)
- `get_family_total_income()`
- `get_family_total_expenses()`
- `get_expense_breakdown_by_category()`
- `get_monthly_summary()`
- `get_savingsyears()`
- `get_monthly_liquidity_by_member_simple()`
- `execute_chatbot_query()`

### Utilities (8)
- `_initialize_tables()`
- `_ensure_connection()`
- `_execute()`
- `_migrate_add_period_columns()`
- `_migrate_add_subcategory_column()`
- `close()`

---

*Database Documentation Complete*
