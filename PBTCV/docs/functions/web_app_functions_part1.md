# Web Application Functions - Detailed Documentation

**File:** `family_expense_tracker.py`  
**Total Lines:** 2,802  
**Language:** Python  
**Framework:** Streamlit

This document provides line-by-line, parameter-by-parameter documentation for every function in the web application.

---

## Table of Contents

1. [Setup & Configuration Functions](#setup--configuration-functions)
2. [Authentication Functions](#authentication-functions)
3. [Dashboard Functions](#dashboard-functions)
4. [Data Management Functions](#data-management-functions)
5. [Helper & Utility Functions](#helper--utility-functions)

---

## Setup & Configuration Functions

### `get_database()`

**Location:** Line 84-86  
**Purpose:** Initialize and return database connection  
**Type:** Factory function  

#### Function Signature
```python
def get_database():
    """Initialize database connection"""
```

#### Parameters
- **None**

#### Returns
- **Type:** `MultiUserDB` object
- **Description:** A fully initialized database instance with active connection

#### What It Does (Step-by-Step)

1. **Checks Environment Variable:**
   ```python
   db_url = os.getenv('DATABASE_URL')
   ```
   - Looks for `DATABASE_URL` in system environment
   - If found: Uses PostgreSQL (production)
   - If not found: Uses SQLite (local development)

2. **Creates Database Instance:**
   ```python
   return MultiUserDB()
   ```
   - Calls `MultiUserDB` constructor
   - Constructor automatically detects database type
   - Initializes tables if they don't exist
   - Runs any pending migrations

3. **Error Handling:**
   - If connection fails: Raises exception
   - Exception caught by main application
   - User sees error message and app stops

#### Example Usage
```python
# Called once at application startup
db = get_database()

# Later used throughout the app
users = db.get_all_users()
income = db.get_income(user_id=1)
```

#### Dependencies
- `os.getenv()` - To read environment variables
- `MultiUserDB` class from `multi_user_database.py`
- `DATABASE_URL` environment variable (optional)

#### Why It's Important
- **Single Point of Access:** Creates one database connection for entire app
- **Environment Flexibility:** Automatically adapts to development/production
- **Error Centralization:** If database fails, entire app stops gracefully

---

## Authentication Functions

### 1. `show_login_page()`

**Location:** Line 109-126  
**Purpose:** Main router for authentication flow  
**Type:** Navigation controller  

#### Function Signature
```python
def show_login_page():
    """Display landing page with role-based navigation or specific login screen"""
```

#### Parameters
- **None** (Uses `st.session_state`)

#### Returns
- **None** (Renders UI directly)

#### Session State Variables Used
- `st.session_state.login_page` - Current login screen to show

#### What It Does (Step-by-Step)

1. **Checks Session State:**
   ```python
   if 'login_page' not in st.session_state:
       st.session_state.login_page = 'landing'
   ```
   - First time: Sets default to 'landing'
   - Subsequent visits: Uses existing value

2. **Routes to Appropriate Screen:**
   ```python
   if st.session_state.login_page == 'landing':
       show_landing_page()
   elif st.session_state.login_page == 'master':
       show_master_login()
   elif st.session_state.login_page == 'admin':
       show_admin_login()
   elif st.session_state.login_page == 'member':
       show_member_login()
   elif st.session_state.login_page == 'password_setup':
       show_password_setup()
   ```
   - Each condition checks the current login page
   - Calls the corresponding function
   - Only one screen shown at a time

#### Flow Diagram
```
User Opens App
      ↓
show_login_page() called
      ↓
Check session_state.login_page
      ↓
landing → show_landing_page() → 4 buttons displayed
      ↓ (User clicks "Master")
      ↓
session_state.login_page = 'master'
      ↓
App re-renders
      ↓
show_login_page() called again
      ↓
Now shows: show_master_login()
```

#### Example Session State Changes
```python
# Initial state
st.session_state.login_page = 'landing'  # Shows landing page

# User clicks "Family Admin" button
st.session_state.login_page = 'admin'    # Triggers re-render

# Next render cycle
show_login_page()                         # Now calls show_admin_login()
```

---

### 2. `show_landing_page()`

**Location:** Line 129-236  
**Purpose:** Display main landing page with 4 role-selection buttons  
**Type:** UI rendering function  

#### Function Signature
```python
def show_landing_page():
    """Display main landing page with 4 navigation buttons"""
```

#### Parameters
- **None**

#### Returns
- **None** (Renders UI)

#### UI Components Created

1. **Header Section:**
   ```python
   st.markdown("<h1 style='text-align: center; color: #2E86AB;'>👨‍👩‍👧‍👦 Family Budget Tracker</h1>", 
               unsafe_allow_html=True)
   st.markdown("<h3 style='text-align: center; color: #666;'>Track Your Family Finances Together</h3>", 
               unsafe_allow_html=True)
   ```
   - Creates centered, styled heading
   - Uses HTML for custom styling
   - Colors: `#2E86AB` (blue) for title, `#666` (gray) for subtitle

2. **Welcome Message:**
   ```python
   st.markdown("""
   <div style='text-align: center; padding: 20px; background-color: #f0f8ff; 
                border-radius: 10px; margin: 20px 0;'>
       <p style='font-size: 18px; color: #333;'>
           Welcome! Please select your role to continue:
       </p>
   </div>
   """, unsafe_allow_html=True)
   ```
   - Light blue background (`#f0f8ff`)
   - Rounded corners (10px radius)
   - Centered text

3. **Four Navigation Buttons:**

   **Button 1: Master Login**
   ```python
   col1, col2, col3, col4 = st.columns(4)
   with col1:
       if st.button("🔑 Master", key="master_btn", use_container_width=True):
           st.session_state.login_page = 'master'
           st.rerun()
   ```
   - Icon: 🔑 (key)
   - Full width in its column
   - On click: Sets session state and reruns app
   
   **Button 2: Family Admin**
   ```python
   with col2:
       if st.button("👨‍💼 Family Admin", key="admin_btn", use_container_width=True):
           st.session_state.login_page = 'admin'
           st.rerun()
   ```
   - Icon: 👨‍💼 (business person)
   - Routes to admin login
   
   **Button 3: Family Member**
   ```python
   with col3:
       if st.button("👤 Family Member", key="member_btn", use_container_width=True):
           st.session_state.login_page = 'member'
           st.rerun()
   ```
   - Icon: 👤 (person)
   - Routes to member login
   
   **Button 4: Password Setup**
   ```python
   with col4:
       if st.button("🔐 Member Password Setup", key="setup_btn", use_container_width=True):
           st.session_state.login_page = 'password_setup'
           st.rerun()
   ```
   - Icon: 🔐 (locked with key)
   - For new member onboarding

4. **Information Cards:**
   ```python
   st.markdown("---")
   st.subheader("📋 Quick Guide")
   ```
   Creates sections explaining each role:
   
   - **Master:** For super administrators
   - **Family Admin:** For household heads
   - **Family Member:** For household members
   - **Password Setup:** For new member activation

#### User Flow Example
```
1. User opens app
   → show_landing_page() displays

2. User sees 4 buttons

3. User clicks "Family Admin"
   → Button code executes:
     st.session_state.login_page = 'admin'
     st.rerun()

4. App restarts
   → show_login_page() checks session_state
   → Sees 'admin'
   → Calls show_admin_login()

5. User sees admin login form
```

#### Why `st.rerun()` Is Needed
- Streamlit apps run top-to-bottom
- Setting session_state doesn't immediately change UI
- `st.rerun()` restarts the app script
- New run picks up updated session_state
- Shows correct login screen

---

### 3. `show_master_login()`

**Location:** Line 240-272  
**Purpose:** Super admin password-only login  
**Type:** Authentication form  

#### Function Signature
```python
def show_master_login():
    """Display Master login (password-only for superadmin)"""
```

#### Parameters
- **None**

#### Returns
- **None** (Renders UI and handles authentication)

#### What Makes It Special
- **Password-only:** No email/username required
- **Hardcoded username:** Always uses 'superadmin'
- **Highest privileges:** Full system access

#### Form Elements

1. **Header:**
   ```python
   st.markdown("<div class='login-container'>", unsafe_allow_html=True)
   st.markdown("<h2 style='text-align: center;'>🔑 Master Login</h2>", unsafe_allow_html=True)
   ```
   - Centered heading
   - Key icon (🔑) indicates master access

2. **Back Button:**
   ```python
   if st.button("← Back to Role Selection"):
       st.session_state.login_page = 'landing'
       st.rerun()
   ```
   - Allow user to go back
   - Resets to landing page
   - Uses arrow (←) for visual clarity

3. **Password Input:**
   ```python
   password = st.text_input("Master Password", type="password", key="master_pass")
   ```
   - `type="password"`: Masks characters (shows ••••)
   - `key="master_pass"`: Unique identifier for Streamlit
   - Returns: User-entered password as string

4. **Login Button:**
   ```python
   if st.button("Login as Master", type="primary", use_container_width=True):
       if not password:
           st.error("⚠️ Please enter your password")
       else:
           # Authentication logic here
   ```
   - `type="primary"`: Makes button prominent (blue)
   - `use_container_width=True`: Full-width button
   - Validation: Checks if password field is empty

#### Authentication Process (Detailed)

**Step 1: Validate Input**
```python
if not password:
    st.error("⚠️ Please enter your password")
    return
```
- Checks if password field is empty
- Shows error if empty
- Stops execution with `return`

**Step 2: Call Database Authentication**
```python
user = db.authenticate_user('superadmin', password)
```
- Hardcoded username: `'superadmin'`
- User-entered password
- Returns: User dict if success, None if fail

**What `authenticate_user`Does:**
1. Hashes the entered password
2. Queries database for user 'superadmin'
3. Compares hashed passwords
4. Checks if user is active
5. Returns user data or None

**Step 3: Handle Result**
```python
if user and user['role'] in ['super', 'superadmin']:
    # Success path
    st.session_state.logged_in = True
    st.session_state.user = user
    st.success("✅ Login successful!")
    time.sleep(1)  # Show success message briefly
    st.rerun()
else:
    # Failure path
    st.error("❌ Invalid credentials or insufficient privileges")
```

**Success:**
1. Sets `logged_in = True` (global flag)
2. Stores user data in session
3. Shows success message (✅)
4. Waits 1 second
5. Reruns app → Shows super admin dashboard

**Failure:**
1. Shows error message (❌)
2. User stays on login screen
3. Can try again

#### Security Considerations

**Password Hashing:**
```python
# In database.py
def _hash_password(self, password):
    return hashlib.sha256(password.encode()).hexdigest()
```
- Never stores plain text password
- Uses SHA-256 algorithm
- One-way encryption (cannot reverse)

**Role Verification:**
```python
if user and user['role'] in ['super', 'superadmin']:
```
- Doesn't just check password
- Also verifies role is super admin
- Prevents privilege escalation

**Session Security:**
- Session state stored server-side
- Unique per browser session
- Cleared when browser closes

#### Example Interaction
```
User: *Opens app*
      *Clicks "Master" button*
      → show_master_login() displays

User: *Enters password: "mysecretpassword"*
      *Clicks "Login as Master"*
      
App:  password = "mysecretpassword"
      user = db.authenticate_user('superadmin', "mysecretpassword")
      
Database:
      1. SELECT * FROM users WHERE email = 'superadmin'
      2. Found user with hash: "a665a..."
      3. Hash entered password: "a665a..."
      4. Compare: Match! ✓
      5. Check role: 'superadmin' ✓
      6. Check active: True ✓
      7. Return user data
      
App:  user = {id: 0, email: 'superadmin', role: 'superadmin', ...}
      Set session_state.logged_in = True
      Set session_state.user = user
      Show: "✅ Login successful!"
      Wait 1 second
      st.rerun()
      
Next Render:
      main() checks logged_in = True
      Calls show_super_admin_dashboard()
      User sees super admin interface
```

---

### 4. `show_admin_login()`

**Location:** Line 275-307  
**Purpose:** Family admin login with email and password  
**Type:** Authentication form  

#### Function Signature
```python
def show_admin_login():
    """Display Family Admin login"""
```

#### Parameters
- **None**

#### Returns
- **None**

#### Differences from Master Login

| Feature | Master Login | Admin Login |
|---------|--------------|-------------|
| Username | Hardcoded ('superadmin') | User enters email |
| Access Level | Full system | Single household |
| User Count | 1 (super admin) | Many (1+ per household) |
| Can Create | Households | Family members |

#### Form Elements

1. **Header and Navigation:**
   ```python
   st.markdown("<h2 style='text-align: center;'>👨‍💼 Family Admin Login</h2>", 
               unsafe_allow_html=True)
   if st.button("← Back to Role Selection"):
       st.session_state.login_page = 'landing'
       st.rerun()
   ```

2. **Email Input:**
   ```python
   email = st.text_input("Email Address", 
                         placeholder="admin@example.com",
                         key="admin_email")
   ```
   - `placeholder`: Shows example format
   - `key`: Unique identifier
   - Returns: Email string (not validated yet)

3. **Password Input:**
   ```python
   password = st.text_input("Password", 
                            type="password",
                            key="admin_pass")
   ```
   - Same as master login
   - Masked input (type="password")

#### Authentication Logic

**Validation:**
```python
if not email or not password:
    st.error("⚠️ Please enter both email and password")
```
- Both fields required
- Shows single error for any missing field

**Database Call:**
```python
user = db.authenticate_user(email, password)
```
- Uses actual email (not hardcoded)
- Password hashing happens in database layer

**Role Check:**
```python
if user and user['role'] == 'admin':
    # Success
else:
    st.error("❌ Invalid credentials or not a family admin account")
```
- Verifies role is 'admin' (not 'member' or 'superadmin')
- Specific error message for clarity

**Session Setup:**
```python
st.session_state.logged_in = True
st.session_state.user = user
st.session_state.household_id = user['household_id']
```
- Stores household_id for data filtering
- user dict contains full user info

#### Example User Record
```python
user = {
    'id': 15,
    'household_id': 3,
    'email': 'raj@sharma.com',
    'full_name': 'Raj Sharma',
    'role': 'admin',
    'relationship': 'self',
    'is_active': True
}
```

---

### 5. `show_member_login()`

**Location:** Line 310-342  
**Purpose:** Family member login  
**Type:** Authentication form  

#### Function Signature
```python
def show_member_login():
    """Display Family Member login"""
```

#### Nearly Identical to Admin Login

**Only Difference:**
```python
# Admin login checks:
if user and user['role'] == 'admin':

# Member login checks:
if user and user['role'] == 'member':
```

#### Why Separate Functions?

1. **UI Clarity:**
   - Different heading: "👤 Family Member Login"
   - Different messaging
   - Sets user expectations

2. **Future Extensibility:**
   - Can add member-specific features
   - Different help text
   - Custom validation rules

3. **Security:**
   - Clear separation of concerns
   - Role verification at login stage
   - Prevents confused deputy problem

---

### 6. `show_password_setup()`

**Location:** Line 345-380  
**Purpose:** New member password creation using invite token  
**Type:** Onboarding form  

#### Function Signature
```python
def show_password_setup():
    """Display password setup for new members"""
```

#### Parameters
- **None**

#### Returns
- **None**

#### When Is This Used?

**Scenario:**
1. Family admin creates new member
2. System generates invite token (e.g., "a3f9c2d8...")
3. Admin shares token with new member
4. New member comes to this screen
5. Enters token + creates password
6. Account activated!

#### Form Elements

1. **Invite Token Input:**
   ```python
   invite_token = st.text_input("Invite Token",
                                placeholder="Enter the token provided by your admin",
                                key="invite_token")
   ```
   - Long random string (32 characters)
   - Case-sensitive
   - One-time use

2. **Password Input:**
   ```python
   password = st.text_input("Create Password",
                           type="password",
                           help="Minimum 6 characters",
                           key="new_password")
   ```
   - `help`: Shows tooltip
   - Type: password (masked)

3. **Password Confirmation:**
   ```python
   confirm_password = st.text_input("Confirm Password",
                                    type="password",
                                    key="confirm_password")
   ```
   - Must match first password
   - Prevents typos

#### Validation Steps

**Step 1: Check All Fields**
```python
if not invite_token or not password or not confirm_password:
    st.error("⚠️ Please fill in all fields")
```

**Step 2: Password Length**
```python
if len(password) < 6:
    st.error("⚠️ Password must be at least 6 characters")
```
- Minimum security requirement
- Can be made more complex later

**Step 3: Password Match**
```python
if password != confirm_password:
    st.error("⚠️ Passwords do not match")
```
- Character-by-character comparison
- Case-sensitive

**Step 4: Accept Invite**
```python
success, message = db.accept_invite(invite_token, password)
```

#### What `accept_invite()` Does (Database Side)

```python
def accept_invite(self, invite_token, new_password):
    # 1. Find user with this invite token
    cursor.execute('SELECT * FROM users WHERE invite_token = ?', 
                  (invite_token,))
    user = cursor.fetchone()
    
    if not user:
        return False, "Invalid invite token"
    
    # 2. Hash the new password
    hashed = self._hash_password(new_password)
    
    # 3. Update user record
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?,
            invite_token = NULL,
            is_active = 1
        WHERE id = ?
    ''', (hashed, user['id']))
    
    # 4. Commit and return
    self.conn.commit()
    return True, "Password set successfully"
```

**Key Actions:**
1. Finds user by token
2. Hashes password (secure storage)
3. Clears invite token (one-time use)
4. Activates account (is_active = 1)
5. Returns success/failure

#### Success Flow
```python
if success:
    st.success(f"✅ {message}")
    st.info("You can now log in using your email and password")
    time.sleep(2)
    st.session_state.login_page = 'member'  # or 'admin'
    st.rerun()
```
1. Shows success message
2. Shows info message
3. Waits 2 seconds
4. Redirects to login
5. User can now log in!

#### Complete User Journey

```
Day 1: Admin Creates Member
Admin: "Add Member" → Enters email: priya@family.com
System: Generates token: "abc123xyz..."
Admin: Shares token with Priya

Day 2: Priya Sets Up Account
Priya: Opens app → "Member Password Setup"
Priya: Enters token: "abc123xyz..."
Priya: Creates password: "secret123"
Priya: Confirms: "secret123"
Priya: Clicks "Set Password"

System: db.accept_invite("abc123xyz...", "secret123")

Database:
  1. SELECT * FROM users WHERE invite_token = 'abc123xyz...'
     → Found: priya@family.com
  
  2. Hash password: "secret123" → "5e884898..."
  
  3. UPDATE users SET
       password_hash = '5e884898...',
       invite_token = NULL,
       is_active = 1
     WHERE email = 'priya@family.com'

System: Success! Shows message
        Waits 2 seconds
        Redirects to member login

Day 3+: Priya Logs In Normally
Priya: Member Login → Enter email & password
Priya: Can now track expenses!
```

---

## Dashboard Functions

### 7. `show_admin_dashboard()`

**Location:** Line 438-889  
**Purpose:** Main interface for family admin  
**Type:** Multi-tab dashboard  
**Complexity:** HIGH (451 lines, 3 tabs, multiple nested functions)

#### Function Signature
```python
def show_admin_dashboard():
    """Display family admin dashboard"""
```

#### Parameters
- **None** (Uses `st.session_state.user`)

#### Returns
- **None**

#### Session Variables Used
```python
user = st.session_state.user
household_id = user['household_id']
user_id = user['id']
```

#### Dashboard Structure

**Three Main Tabs:**
1. My Expenses (Personal tracking)
2. Family Overview (Household summary)
3. Manage Members (Member administration)

#### Tab Navigation
```python
tab = st.radio(
    "Navigation",
    ["My Expenses", "Family Overview", "Manage Members"],
    horizontal=True,
    key="admin_tab_selection"
)

if tab == "My Expenses":
    show_member_expense_tracking(user_id)
elif tab == "Family Overview":
    # Family overview code
elif tab == "Manage Members":
    # Member management code
```

### Tab 1: My Expenses

**Simple Delegation:**
```python
show_member_expense_tracking(user_id)
```
- Reuses the same personal tracking UI as members
- Shows: Income, Allocations, Expenses, Review
- Documented in detail in next section

### Tab 2: Family Overview

**Purpose:** See combined family financial data

**Period Selector:**
```python
col_year, col_month = st.columns(2)
with col_year:
    year = st.selectbox("Year", sorted(available_years, reverse=True))
with col_month:
    month = st.selectbox("Month", range(1, 13), 
                        format_func=lambda x: calendar.month_name[x])
```
- Two dropdowns side by side
- Years from database (dynamic)
- Months 1-12 with names (January, February...)

**Member Filter:**
```python
# Get all household members
household_members = db.get_household_members(household_id)
member_names = ['All Members'] + [m['full_name'] for m in household_members]

selected_member = st.selectbox("Filter by Member", member_names)
```
- Starts with "All Members"
- Lists all family members
- Admin can filter by specific person

**Data Aggregation Logic:**

If "All Members" selected:
```python
user_ids = [m['id'] for m in household_members]
total_income = db.get_family_total_income(household_id, year, month)
total_expenses = db.get_family_total_expenses(household_id, year, month)
```

If specific member selected:
```python
selected_user = next(m for m in household_members 
                    if m['full_name'] == selected_member)
user_ids = [selected_user['id']]
# Get data for this user only
```

**Display Metrics:**
```python
col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₹{total_income:,.2f}")
col2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
col3.metric("Savings", f"₹{total_income - total_expenses:,.2f}")
```
- Three cards showing key numbers
- Formatted with comma separators
- Currency symbol (₹)

**Charts:**

1. **Expense Breakdown (Pie Chart):**
```python
# Aggregate expenses by category
expenses_by_category = {}
for user_id in user_ids:
    expenses = db.get_expenses(user_id, year, month)
    for exp in expenses:
        category = exp['category']
        amount = exp['amount']
        expenses_by_category[category] = expenses_by_category.get(category, 0) + amount

# Create pie chart
fig = px.pie(
    values=list(expenses_by_category.values()),
    names=list(expenses_by_category.keys()),
    title=f"Expenses by Category - {calendar.month_name[month]} {year}"
)
st.plotly_chart(fig)
```

2. **Income vs Expenses (Bar Chart):**
```python
fig = go.Figure(data=[
    go.Bar(name='Income', x=['Total'], y=[total_income]),
    go.Bar(name='Expenses', x=['Total'], y=[total_expenses])
])
st.plotly_chart(fig)
```

### Tab 3: Manage Members

**Add New Member Form:**
```python
with st.expander("➕ Add New Member", expanded=False):
    new_email = st.text_input("Email")
    new_name = st.text_input("Full Name")
    relationship = st.selectbox("Relationship", 
                               ["Spouse", "Child", "Parent", "Other"])
    
    if st.button("Add Member"):
        success, invite_token = db.create_member(
            household_id, new_email, new_name, relationship, user_id
        )
        if success:
            st.success(f"✅ Member added!")
            st.code(f"Invite Token: {invite_token}")
            st.info("Share this token with the new member")
```

**Member List Table:**
```python
members = db.get_household_members(household_id)

# Create dataframe
df = pd.DataFrame(members)
df = df[['full_name', 'email', 'relationship', 'is_active']]
df.columns = ['Name', 'Email', 'Relationship', 'Active']

st.dataframe(df, use_container_width=True)
```

**Delete Member:**
```python
member_to_delete = st.selectbox("Select Member to Delete", 
                               [m['full_name'] for m in members if m['id'] != user_id])

if st.button("Delete Member", type="secondary"):
    confirm = st.warning("This will delete ALL data for this member!")
    if st.checkbox("I understand, delete this member"):
        member_id = next(m['id'] for m in members if m['full_name'] == member_to_delete)
        success, message = db.delete_member(member_id)
        if success:
            st.success("✅ Member deleted")
            st.rerun()
```
- Excludes self from deletion list (can't delete yourself)
- Requires checkbox confirmation
- Warning about data loss
- Cascading delete in database

---

## Continued in Next File...

This is Part 1 of the Web App Functions documentation. The file is extensive - shall I continue with the remaining functions (`show_member_dashboard`, `show_member_expense_tracking`, etc.)?

**Estimated Total:** This will be a 2000+ line documentation file covering all 26 functions in detail.
