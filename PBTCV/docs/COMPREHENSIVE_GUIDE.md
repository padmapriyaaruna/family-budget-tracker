# Family Budget Tracker - Comprehensive Beginner's Guide

**Version:** v6.1  
**Last Updated:** January 18, 2026  
**For:** Complete beginners with no coding knowledge

---

## 📚 Table of Contents

1. [What Is This Application?](#what-is-this-application)
2. [How Does It Work? (The Big Picture)](#how-does-it-work-the-big-picture)
3. [Web Application Explained](#web-application-explained)
4. [Mobile Application Explained](#mobile-application-explained)
5. [Backend API Explained](#backend-api-explained)
6. [Database Explained](#database-explained)
7. [Key Functions Dictionary](#key-functions-dictionary)
8. [How Everything Connects](#how-everything-connects)
9. [Common User Scenarios](#common-user-scenarios)

---

## 1. What Is This Application?

Think of this as a **digital notebook** where families can track their money. Just like you'd write in a physical notebook:
- Money coming in (salary, gifts, etc.)
- Where you plan to spend it (rent, food, etc.)
- What you actually spent

But this is better because:
1. **Multiple people** (family members) can use it
2. **It calculates** everything automatically
3. **It shows charts** so you can see patterns
4. **It's accessible** from anywhere (web browser or phone)

### Who Can Use It?

There are three types of users:

1. **Super Admin** - Like the owner of the whole system
   - Can create families
   - Can manage everyone
   - Has complete control

2. **Family Admin** - Like the head of a household
   - Can see their family's money
   - Can add family members
   - Can track personal expenses

3. **Family Member** - Regular user
   - Can only see and track their own money
   - Cannot see other family members' details

---

## 2. How Does It Work? (The Big Picture)

### The Three Main Parts

Think of this application like a house with three floors:

```
┌─────────────────────────────────────────┐
│  🖥️  FLOOR 3: What You See              │
│  (Web Pages & Mobile App Screens)       │
│  - Login screens                         │
│  - Dashboards with tables and charts    │
│  - Forms to add income/expenses          │
└─────────────────┬───────────────────────┘
                  │ (Communication)
┌─────────────────┴───────────────────────┐
│  ⚙️  FLOOR 2: The Brain                 │
│  (Backend API - The Middleman)           │
│  - Receives your requests                │
│  - Checks if you're allowed              │
│  - Talks to the database                 │
└─────────────────┬───────────────────────┘
                  │ (Stores & retrieves data)
┌─────────────────┴───────────────────────┐
│  💾  FLOOR 1: The Storage               │
│  (Database - Where Everything Is Saved)  │
│  - All users' information                │
│  - All money records                     │
│  - Everything is organized in tables     │
└─────────────────────────────────────────┘
```

### Simple Example: Adding an Expense

Let's say you bought groceries for ₹5,000. Here's what happens:

1. **You (Floor 3):** Fill out a form on your phone:
   - Date: Today
   - Category: Grocery
   - Amount: 5000
   - Click "Save"

2. **The Brain (Floor 2):** 
   - Receives your request
   - Checks: "Is this person logged in?"
   - Checks: "Does this category exist in their budget?"
   - Sends to database: "Save this expense"
   - Updates the budget: "Subtract ₹5,000 from Grocery allocation"

3. **The Storage (Floor 1):**
   - Saves the new expense in the expenses table
   - Updates the allocations table

4. **Back to You:**
   - Success message appears
   - Your expense list updates automatically
   - Budget charts refresh to show new data

---

## 3. Web Application Explained

### What Is It?

The web application is what you see when you open the website in a browser (Chrome, Firefox, etc.). It's built using **Streamlit**, which is like a tool that makes creating websites easier.

### Main File: `family_expense_tracker.py`

This is the **main program** (think of it as the instruction manual for the website). It has 2,802 lines of instructions!

### What's Inside?

#### Think of it like a restaurant menu with different sections:

#### Section 1: Login Pages
**Purpose:** These are the "front door" to your application.

**Files/Functions:**
- `show_landing_page()` - The first page you see with 4 buttons
- `show_master_login()` - Super Admin login (password only)
- `show_admin_login()` - Family Admin login (email + password)
- `show_member_login()` - Family Member login (email + password)
- `show_password_setup()` - For new members to create their password

**What They Do:**
Like a security guard checking IDs. Each login page:
1. Shows a form where you type your credentials
2. Sends them to the database
3. If correct → Let you in
4. If wrong → Show error message

#### Section 2: Dashboard Pages
**Purpose:** Your "home base" after logging in.

**Three Different Dashboards (like three different restaurant menus):**

1. **Super Admin Dashboard** (`show_super_admin_dashboard()`)
   - **Analogy:** Like a CEO's control panel
   - **What you see:**
     - Statistics: How many families, users, total money
     - List of all families (can add/remove/disable)
     - List of all users across families
     - Tools to promote/demote users

2. **Family Admin Dashboard** (`show_admin_dashboard()`)
   - **Analogy:** Like a household manager's notebook
   - **What you see:**
     - **Tab 1 - My Expenses:** Your personal money tracking
     - **Tab 2 - Family Overview:** Combined family income/expenses
     - **Tab 3 - Manage Members:** Add/remove family members

3. **Member Dashboard** (`show_member_dashboard()`)
   - **Analogy:** Like your personal diary
   - **What you see:**
     - Only your own income, budget, and expenses
     - Cannot see other people's data

#### Section 3: The Tracking Screens
**Main Function:** `show_member_expense_tracking(user_id)`

This is the **heart** of the application. Think of it like four different notebooks:

**Notebook 1: Income Tab**
- Where you record money coming in
- **Add Income Form:**
  - Date: When did you get it?
  - Source: Where from? (Salary, bonus, gift, etc.)
  - Amount: How much?
- **Income Table:**
  - Shows all your income records
  - Can edit or delete each one

**Notebook 2: Allocations Tab**
- Where you plan your budget for the month
- **Add Allocation Form:**
  - Category: What for? (Rent, Food, Transport, etc.)
  - Amount: How much to allocate?
- **Allocations Table:**
  - Shows category, allocated amount, spent amount, balance
  - Progress bar: Visual of how much used
  - Can edit or delete allocations

**Notebook 3: Expenses Tab**
- Where you record actual spending
- **Add Expense Form:**
  - Date: When?
  - Category: What type? (must match your allocations)
  - Subcategory: More specific (Food - Online, Food - Hotel, etc.)
  - Amount: How much?
  - Comments: Any notes
- **Expenses Table:**
  - Shows all your spending
  - Sorted by date
  - Can edit or delete

**Notebook 4: Review Tab**
- Where you see the summary
- **Dashboard Shows:**
  - Total Income vs Total Expenses
  - Pie chart: Expenses by category
  - Bar chart: Income vs Expenses over time
  - Savings: Income - Expenses

---

## 4. Mobile Application Explained

### What Is It?

The mobile app is for your phone (Android/iOS). It's built using **React Native**, which lets you write code once and use it on both Android and Apple phones.

### File Structure

The mobile app is organized like a filing cabinet:

```
BudgetTrackerMobile/
├── src/
│   ├── screens/      ← The pages you see
│   ├── services/     ← Code that talks to the server
│   └── config.js     ← Settings
└── App.js           ← The main controller
```

### Main Screens (Think of them as different rooms)

#### Room 1: Login Screen (`LoginScreen.js`)
**Purpose:** The entrance to your app

**What It Does:**
1. Shows 4 buttons (just like the web):
   - Master Login
   - Family Admin Login
   - Family Member Login
   - Password Setup
2. Each button opens a different login form
3. After successful login, takes you to the dashboard

#### Room 2: Dashboard Screen (`DashboardScreen.js`)
**Purpose:** Your home screen after login

**What It Shows:**
- Summary cards:
  - Total Income
  - Total Expenses
  - Total Allocated
  - Savings
- Quick action buttons:
  - Add Expense
  - Add Income  
  - Add Allocation
- Navigation buttons to detailed screens

#### Room 3: Add/Edit Screens

**Three Main Add Screens:**

1. **AddIncomeScreen.js** - Add money coming in
   - Date picker
   - Source text input
   - Amount number input
   - Save button

2. **AddAllocationScreen.js** - Plan your budget
   - Category text input
   - Amount number input
   - Save/Update button
   - **Special:** Works for both adding NEW and editing EXISTING allocations
   - When editing: Fields are pre-filled with current values

3. **AddExpenseScreen.js** - Record spending
   - Date picker
   - Category dropdown (from your allocations)
   - Subcategory dropdown
   - Amount number input
   - Comments text area
   - Save button

#### Room 4: List Screens

**Three List Screens:**

1. **IncomeListScreen.js**
   - Shows all income in a scrollable list
   - Each item shows: Date, Source, Amount
   - Can tap to edit

2. **AllocationsListScreen.js**
   - Shows all budget allocations
   - Each card shows:
     - Category name
     - Allocated amount
     - Spent amount
     - Balance
     - Progress bar
     - **Edit button** - Opens AddAllocationScreen with data
     - **Delete button** - Removes allocation

3. **ExpensesListScreen.js**
   - Shows all expenses
   - Each item shows: Date, Category, Amount, Comments
   - Can tap to edit or delete

### How Mobile Talks to the Server

**File:** `src/services/api.js`

This is like a telephone operator. When you click "Save" on your phone:

1. **Your Phone:** "I want to save this expense"
2. **api.js (Operator):** "Let me package this request nicely"
   - Adds your login token (proves who you are)
   - Formats the data correctly
   - Sends it to the server
3. **Server:** Processes the request
4. **api.js:** Receives response, gives it back to your phone
5. **Your Phone:** Shows success message or error

**Key Functions in api.js:**

```javascript
// Income functions
addIncome(data)           // Saves new income
getIncome(userId)         // Gets all income
updateIncome(id, data)    // Updates existing income
deleteIncome(id)          // Removes income

// Allocation functions
addAllocation(data)       // Saves new allocation
getAllocations(userId)    // Gets all allocations
updateAllocation(id, data) // Updates allocation ← Used when editing
deleteAllocation(id)      // Removes allocation

// Expense functions
addExpense(data)          // Saves new expense
getExpenses(userId)       // Gets all expenses
updateExpense(id, data)   // Updates expense
deleteExpense(id)         // Removes expense
```

---

## 5. Backend API Explained

### What Is It?

The Backend API is the "middleman" or "translator" between your app (web/mobile) and the database. It's built using **FastAPI** (a Python framework).

**Main File:** `api.py` (1,394 lines)

### Why Do We Need It?

**Without API:**
```
Your Phone → Tries to talk directly to Database → ERROR!
(Different languages, security issues, chaos!)
```

**With API:**
```
Your Phone → Speaks to API in simple requests → API translates → Database
                                             ← API formats response ← Database
```

### What Does It Do?

Think of the API as a **restaurant waiter**:

1. **Takes Your Order** (Receives requests from web/mobile)
   - "I want to add an expense"
   - "Show me my income"
   - "Delete this allocation"

2. **Checks Your Order** (Validates)
   - "Are you logged in?"
   - "Do you have permission?"
   - "Is the data format correct?"

3. **Gives Order to Kitchen** (Talks to database)
   - "Save this expense in the expenses table"
   - "Get all income for user ID 28"

4. **Brings Back Your Food** (Returns response)
   - Success: "Expense saved!"
   - Error: "Category doesn't exist!"

### Key API Endpoints

Think of endpoints as different counters in a government office:

#### Counter 1: Authentication (`/api/auth/`)
- `/api/auth/login` - Log in with email/password
- `/api/auth/accept-invite` - New member creates password

#### Counter 2: Dashboard (`/api/dashboard/`)
- `/api/dashboard/{user_id}` - Get summary (income vs expenses)

#### Counter 3: Income (`/api/income/`)
- `GET /api/income/{user_id}` - List all income
- `POST /api/income` - Add new income
- `PUT /api/income/{id}` - Update income
- `DELETE /api/income/{id}` - Delete income

#### Counter 4: Allocations (`/api/allocations/`)
- `GET /api/allocations/{user_id}` - List all allocations
- `POST /api/allocations` - Add new allocation
- `PUT /api/allocations/{id}` - Update allocation
- `DELETE /api/allocations/{id}` - Delete allocation

#### Counter 5: Expenses (`/api/expenses/`)
- `GET /api/expenses/{user_id}` - List all expenses
- `POST /api/expenses` - Add new expense
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense

### Security: The Bouncer

Every API request goes through security checks:

1. **JWT Token Check**
   - Like a VIP pass that proves you're logged in
   - Created when you log in
   - Must be included in every request
   - Expires after 24 hours (you need to log in again)

2. **Role Check**
   - Super Admin can do everything
   - Family Admin can manage their family
   - Members can only manage their own data

3. **Data Isolation**
   - You can only see your family's data
   - Automatic filters ensure this

---

## 6. Database Explained

### What Is a Database?

Think of it as a **giant Excel spreadsheet** with multiple sheets, but much more powerful.

### Our Database: PostgreSQL

We use **PostgreSQL** (a type of database) in production (when deployed online). For local testing, we use **SQLite** (simpler version).

### The Five Main Tables (Sheets)

#### Table 1: `households`
**Purpose:** Stores family information

**Analogy:** Like the address book of families

**Columns (like Excel columns):**
- `id` - Unique family number (auto-generated)
- `name` - Family name (e.g., "Sharma Family")
- `is_active` - Is this family currently active? (Yes/No)
- `created_at` - When was this family added?

**Example Data:**
```
id  | name           | is_active | created_at
----|----------------|-----------|-------------------
1   | Sharma Family  | Yes       | 2026-01-01 10:30:00
2   | Kumar Family   | Yes       | 2026-01-05 14:20:00
3   | Patel Family   | No        | 2026-01-10 09:15:00
```

#### Table 2: `users`
**Purpose:** Stores all user accounts

**Analogy:** Like an employee directory

**Columns:**
- `id` - Unique user number
- `household_id` - Which family? (links to households table)
- `email` - Login email
- `password_hash` - Encrypted password (not the actual password!)
- `full_name` - Person's name
- `role` - Super Admin, Admin, or Member
- `relationship` - Self, Spouse, Child, etc.
- `is_active` - Can this person log in?
- `invite_token` - Temporary code for password setup
- `created_at` - When was account created?

**Example Data:**
```
id | household_id | email              | full_name | role   | relationship
---|--------------|-------------------|-----------|--------|-------------
1  | 1            | raj@gmail.com     | Raj       | admin  | self
2  | 1            | priya@gmail.com   | Priya     | member | spouse
3  | 1            | aarav@gmail.com   | Aarav     | member | child
```

**Special Case:** Super Admin has `household_id = 0` (not part of any family)

#### Table 3: `income`
**Purpose:** Records all money coming in

**Analogy:** Like a pay stub collection

**Columns:**
- `id` - Unique income record number
- `user_id` - Who received it? (links to users table)
- `date` - When? (YYYY-MM-DD format)
- `source` - From where? (Salary, Bonus, Gift, etc.)
- `amount` - How much?
- `created_at` - When was this record added?

**Example Data:**
```
id | user_id | date       | source  | amount
---|---------|------------|---------|--------
1  | 1       | 2026-01-01 | Salary  | 50000
2  | 1       | 2026-01-15 | Bonus   | 10000
3  | 2       | 2026-01-01 | Salary  | 30000
```

#### Table 4: `allocations`
**Purpose:** Budget planning for each category

**Analogy:** Like monthly budget envelopes

**Columns:**
- `id` - Unique allocation number
- `user_id` - Whose budget? (links to users table)
- `category` - What category? (Rent, Food, etc.)
- `allocated_amount` - How much planned?
- `spent_amount` - How much actually spent? (auto-calculated)
- `balance` - Remaining (auto-calculated: allocated - spent)
- `year` - Which year?
- `month` - Which month?

**Example Data:**
```
id | user_id | category  | allocated  | spent  | balance | year | month
---|---------|-----------|------------|--------|---------|------|------
1  | 1       | Rent      | 25000      | 25000  | 0       | 2026 | 1
2  | 1       | Food      | 15000      | 12000  | 3000    | 2026 | 1
3  | 1       | Transport | 5000       | 3500   | 1500    | 2026 | 1
```

**Important:** Each person has their own allocations for each month.

#### Table 5: `expenses`
**Purpose:** Records all spending

**Analogy:** Like receipts in your wallet

**Columns:**
- `id` - Unique expense number
- `user_id` - Who spent it? (links to users table)
- `date` - When?
- `category` - What category? (must match an allocation)
- `subcategory` - More specific detail
- `amount` - How much?
- `comment` - Any notes
- `created_at` - When was this recorded?

**Example Data:**
```
id | user_id | date       | category | subcategory    | amount | comment
---|---------|------------|----------|----------------|--------|------------------
1  | 1       | 2026-01-05 | Food     | Grocery-Online | 3000   | Weekly groceries
2  | 1       | 2026-01-10 | Food     | Food-Hotel     | 1500   | Dinner with family
3  | 1       | 2026-01-03 | Rent     | House Rent     | 25000  | January rent
```

### How Tables Connect

**Think of it like a family tree:**

```
households (Family)
    ↓
    ├── users (Family members)
    │    ↓
    │    ├── income (Their income)
    │    ├── allocations (Their budget)
    │    └── expenses (Their spending)
```

**Example:**
1. "Sharma Family" (household id = 1)
2. Has member "Raj" (user id = 1, household_id = 1)
3. Raj has income records (user_id = 1)
4. Raj has allocations (user_id = 1)
5. Raj has expenses (user_id = 1)

---

## 7. Key Functions Dictionary

### What Is a Function?

A **function** is like a recipe. You give it ingredients (inputs), it follows steps, and gives you the dish (output).

### Authentication Functions

#### `authenticate_user(email, password)`
**What it does:** Checks if login is correct

**Simple explanation:**
1. Takes your email and password
2. Looks in the users table
3. Checks if password matches (using encryption)
4. If yes: Returns your user information
5. If no: Returns nothing (you can't log in)

**Analogy:** Like a guard checking your ID card at the gate.

#### `generate_invite_token()`
**What it does:** Creates a random code for new members

**Simple explanation:**
1. Generates a 32-character random string (like: `a3f9c2d8e4b1...`)
2. This is like a one-time password
3. New member uses this to create their account
4. After use, it becomes invalid

**Analogy:** Like a temporary guest pass to a building.

### Income Functions

#### `add_income(user_id, date, source, amount)`
**What it does:** Saves a new income record

**Inputs:**
- `user_id`: Who is this for?
- `date`: When was it received?
- `source`: Where from?
- `amount`: How much?

**Steps:**
1. Checks if user_id exists
2. Inserts new row in income table
3. Returns success/failure

**Example:**
```
add_income(1, "2026-01-15", "Salary", 50000)
→ Saves: User 1 received salary of ₹50,000 on Jan 15, 2026
```

#### `get_income(user_id, year=None, month=None)`
**What it does:** Retrieves income records

**Inputs:**
- `user_id`: Whose income?
- `year` (optional): Filter by year
- `month` (optional): Filter by month

**Returns:** List of income records

**Example:**
```
get_income(1, 2026, 1)
→ Returns: All income for user 1 in January 2026
```

### Allocation Functions

#### `add_allocation(user_id, category, allocated_amount, year, month)`
**What it does:** Creates a budget plan for a category

**Inputs:**
- `user_id`: Whose budget?
- `category`: What category?
- `allocated_amount`: How much to allocate?
- `year`: Which year?
- `month`: Which month?

**Steps:**
1. Creates new row in allocations table
2. Sets spent_amount = 0 (nothing spent yet)
3. Sets balance = allocated_amount (full amount available)

**Example:**
```
add_allocation(1, "Food", 15000, 2026, 1)
→ Creates: Food budget of ₹15,000 for January 2026
```

#### `update_allocation(allocation_id, user_id, category, allocated_amount, year, month)`
**What it does:** Changes an existing budget allocation

**Inputs:**
- `allocation_id`: Which allocation to update?
- `user_id`: Whose budget? (for security check)
- `category`: New category name
- `allocated_amount`: New amount
- `year`: Year
- `month`: Month

**Steps:**
1. Finds the allocation by ID
2. Checks if user owns it (security)
3. Updates the allocated_amount
4. Recalculates balance (allocated_amount - spent_amount)

**Example:**
```
update_allocation(2, 1, "Food", 18000, 2026, 1)
→ Changes: Food allocation from ₹15,000 to ₹18,000
```

**Real-world scenario:**
You originally planned ₹15,000 for food but realize you need ₹18,000. You edit the allocation. The system automatically recalculates the balance.

#### `update_allocation_spent_amount(user_id, category, year, month)`
**What it does:** Syncs spent amount with actual expenses

**When it runs:** Automatically after adding/updating/deleting an expense

**Steps:**
1. Finds all expenses in that category for that month
2. Calculates total: SUM(amount)
3. Updates allocation.spent_amount
4. Updates allocation.balance

**Why it's important:** Keeps your budget up-to-date automatically!

**Example:**
You have Food allocation of ₹15,000:
1. You add expense: Groceries ₹3,000
   → System updates: spent = ₹3,000, balance = ₹12,000
2. You add expense: Restaurant ₹1,500
   → System updates: spent = ₹4,500, balance = ₹10,500

### Expense Functions

#### `add_expense(user_id, date, category, subcategory, amount, comment)`
**What it does:** Records a spending transaction

**Inputs:**
- `user_id`: Who spent it?
- `date`: When?
- `category`: Which budget category?
- `subcategory`: What specific type?
- `amount`: How much?
- `comment`: Any notes

**Steps:**
1. Validates: Does this category exist in user's allocations?
2. Saves expense in expenses table
3. Calls `update_allocation_spent_amount()` to update budget
4. Returns success

**Example:**
```
add_expense(1, "2026-01-15", "Food", "Grocery-Online", 3000, "Weekly shopping")
→ Saves expense AND updates Food allocation's spent amount
```

### Super Admin Functions

#### `create_household_with_admin(household_name, admin_email, admin_name)`
**What it does:** Creates a new family and its first admin

**Steps:**
1. Creates new row in households table
2. Creates new user (admin role) for that household
3. Generates invite token for admin
4. Returns the invite token

**Example:**
```
create_household_with_admin("Kumar Family", "raj@kumar.com", "Raj Kumar")
→ Creates household
→ Creates admin account (pending, needs password)
→ Returns invite token: "a3f9c2d8e4b1..."
```

**What happens next:**
1. Super admin shares invite token with Raj
2. Raj goes to Password Setup page
3. Raj enters token and creates password
4. Raj can now log in as Family Admin

#### `promote_member_to_admin(user_id, household_id)`
**What it does:** Upgrades a member to admin

**Validation:**
- Must be in the same household
- User must exist and be active

**Steps:**
1. Checks validation
2. Updates user.role from 'member' to 'admin'
3. Returns success

**Impact:** This person can now manage family members and see family overview.

---

## 8. How Everything Connects

### Complete Flow: Adding an Expense (Step-by-Step)

Let's trace what happens when you add a grocery expense of ₹3,000:

#### Step 1: You (Mobile App)
```
1. Open mobile app
2. Tap "Add Expense" button
3. Fill form:
   - Date: 2026-01-15
   - Category: Food
   - Subcategory: Grocery-Online
   - Amount: 3000
   - Comment: "Weekly groceries"
4. Tap "Save"
```

#### Step 2: Mobile App Code (`AddExpenseScreen.js`)
```
1. Validates: Are all required fields filled?
2. Calls api.addExpense() function:
   api.addExpense({
     user_id: 1,
     date: "2026-01-15",
     category: "Food",
     subcategory: "Grocery-Online",
     amount: 3000,
     comment: "Weekly groceries"
   })
```

#### Step 3: API Service (`api.js`)
```
1. Takes your data
2. Adds authentication token (proves who you are)
3. Sends HTTP POST request to:
   POST https://your-api.com/api/expenses
   Headers: { Authorization: "Bearer your-token-here" }
   Body: { user_id: 1, date: "2026-01-15", ... }
```

#### Step 4: Backend API (`api.py`)
```
1. Receives request
2. Validates token:
   - Is token valid?
   - Is it expired?
   → Extracts user info from token
3. Validates permissions:
   - Does user_id in request match logged-in user?
   - Or is this person an admin?
4. Validates business logic:
   - Does "Food" category exist in user's allocations?
5. Calls database function:
   db.add_expense(1, "2026-01-15", "Food", "Grocery-Online", 3000, "Weekly groceries")
```

#### Step 5: Database Layer (`multi_user_database.py`)
```
1. add_expense() function:
   - Inserts new row in expenses table:
     INSERT INTO expenses (user_id, date, category, subcategory, amount, comment)
     VALUES (1, '2026-01-15', 'Food', 'Grocery-Online', 3000, 'Weekly groceries')
   
2. Automatically triggers update_allocation_spent_amount():
   a. Finds Food allocation for user 1, January 2026
   b. Calculates: spent = SUM of all Food expenses in January
      → Previously: ₹0
      → Now: ₹3,000
   c. Updates allocation:
      UPDATE allocations
      SET spent_amount = 3000,
          balance = allocated_amount - 3000
      WHERE user_id = 1 AND category = 'Food' AND year = 2026 AND month = 1
      
      Before: allocated = 15000, spent = 0, balance = 15000
      After:  allocated = 15000, spent = 3000, balance = 12000
```

#### Step 6: Database (`PostgreSQL`)
```
1. Executes SQL commands
2. Saves data to disk
3. Returns success confirmation
```

#### Step 7: Response Back Up the Chain
```
Database → Returns: "Success"
  ↓
Database Layer → Returns: true
  ↓
Backend API → Returns: { status: "success", message: "Expense added successfully" }
  ↓
API Service (`api.js`) → Returns: success response
  ↓
Mobile Screen (`AddExpenseScreen.js`) → Shows: "Success! Expense added."
  ↓
You → See success message, screen closes, expense list automatically refreshes
```

### What Happened in Summary

1. ✅ New expense record created in database
2. ✅ Food allocation's spent_amount updated (₹0 → ₹3,000)
3. ✅ Food allocation's balance updated (₹15,000 → ₹12,000)
4. ✅ When you open Allocations screen:
   - Food shows: Allocated ₹15,000, Spent ₹3,000, Balance ₹12,000
   - Progress bar shows 20% used
5. ✅ When you open Expenses screen:
   - Your new grocery expense appears in the list
6. ✅ When you open Review/Dashboard:
   - Total expenses increased by ₹3,000
   - Charts updated automatically

---

## 9. Common User Scenarios

### Scenario 1: New Family Getting Started

**Super Admin's Actions:**
1. Logs in to Super Admin dashboard
2. Clicks "Create New Household"
3. Fills form:
   - Household Name: "Sharma Family"
   - Admin Email: raj@sharma.com
   - Admin Name: Raj Sharma
4. System generates invite token: `xyz123abc456`
5. Super Admin shares this token with Raj

**Raj's Actions (New Family Admin):**
1. Opens app, clicks "Password Setup"
2. Enters token: `xyz123abc456`
3. Creates password
4. Now can log in as Family Admin
5. Goes to "Manage Members" tab
6. Adds wife Priya:
   - Email: priya@sharma.com
   - Name: Priya Sharma
   - Relationship: Spouse
7. System generates token for Priya
8. Raj shares token with Priya
9. Priya sets up her password
10. Both can now track their expenses!

### Scenario 2: Monthly Budget Planning

**Raj's Process (Start of Month):**

1. **Check Income:**
   - Income Tab → Add Income
   - Date: 2026-02-01
   - Source: Salary
   - Amount: ₹50,000

2. **Plan Budget (Allocations Tab):**
   - Add Allocation: Rent → ₹25,000
   - Add Allocation: Food → ₹15,000
   - Add Allocation: Transport → ₹5,000
   - Add Allocation: Utilities → ₹3,000
   - Add Allocation: Savings → ₹2,000
   - Total: ₹50,000 (matches income!)

3. **Track Spending (Throughout Month):**
   
   Day 1:
   - Expense: Rent, House Rent, ₹25,000
   → Rent allocation: ₹25,000 spent, ₹0 balance
   
   Day 5:
   - Expense: Food, Grocery-Online, ₹3,000
   → Food allocation: ₹3,000 spent, ₹12,000 balance
   
   Day 10:
   - Expense: Food, Food-Hotel, ₹1,500
   → Food allocation: ₹4,500 spent, ₹10,500 balance
   
   Day 15:
   - Checks allocations, sees Food is 30% used
   - Still has ₹10,500 left for food this month ✅

4. **Month-End Review:**
   - Review Tab shows:
     - Income: ₹50,000
     - Expenses: ₹28,500
     - Savings: ₹21,500
   - Charts show spending patterns
   - Can plan next month better!

### Scenario 3: Editing an Allocation

**Problem:** Priya realizes she needs more money for food

**Solution:**
1. Opens Allocations Tab
2. Sees Food card:
   - Allocated: ₹15,000
   - Spent: ₹8,000
   - Balance: ₹7,000
3. Taps "Edit" button
4. Changes amount from ₹15,000 to ₹18,000
5. Taps "Update"
6. System automatically recalculates:
   - New Allocated: ₹18,000
   - Spent: ₹8,000 (unchanged)
   - New Balance: ₹10,000 (automatically updated!)
7. Now has ₹3,000 more for food ✅

**What Happened Behind Scenes:**
1. Mobile app called `updateAllocation(id, data)`
2. API validated the request
3. Database updated the allocation
4. Balance recalculated: 18000 - 8000 = 10000
5. Response sent back
6. Mobile screen refreshed with new data

### Scenario 4: Family Admin Checking Family Overview

**Raj wants to see total family expenses:**

1. Logs in as Family Admin
2. Goes to "Family Overview" tab
3. Selects month: January 2026
4. Selects members: "All Members"
5. System shows:
   - **Family Total Income:** ₹80,000
     - Raj: ₹50,000
     - Priya: ₹30,000
   - **Family Total Expenses:** ₹55,000
     - Raj: ₹35,000
     - Priya: ₹20,000
   - **Family Savings:** ₹25,000
6. Charts show:
   - Who spent what
   - Which categories cost most
   - Trends over time

**How It Works:**
```
1. Frontend calls: api.getDashboard(household_id, year, month)
2. Backend queries database:
   - Get all users in household
   - Sum income for all those users
   - Sum expenses for all those users
3. Returns aggregated data
4. Frontend displays in charts
```

---

## 10. Data Flow Diagrams

### Edit Allocation Flow (New in v6.1!)

```
┌─────────────────────────────────────────────────────┐
│ USER: Taps Edit on Rent Allocation                  │
│ (Wants to change ₹25,000 to ₹25,001)                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ AllocationsListScreen.js                            │
│ 1. Extract allocation data from the card:           │
│    { id: 15, Category: "Rent",                      │
│      "Allocated Amount": 25000, ... }               │
│ 2. Navigate to AddAllocationScreen                  │
│    Pass: allocation data                            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ App.js (Navigation Handler)                         │
│ 1. Receives navigation request                      │
│ 2. Stores allocation data in screenParams           │
│ 3. Renders AddAllocationScreen                      │
│    Pass: route.params = { ...screenParams, ... }    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ AddAllocationScreen.js                              │
│ 1. Detects edit mode: allocation = route.params     │
│ 2. Pre-fills form:                                  │
│    - Category: "Rent"                               │
│    - Amount: "25000"                                │
│ 3. User changes amount to: 25001                    │
│ 4. User taps "Update Allocation"                    │
│ 5. Validates: amount > 0 ✓                          │
│ 6. Checks budget availability:                      │
│    - Total Income: ₹140,000                         │
│    - Other Allocations: ₹115,000                    │
│    - Current Rent (exclude): ₹25,000                │
│    - Available: 140000 - 115000 = ₹25,000           │
│    - New Amount: ₹25,001                            │
│    - Available for edit: 25000 + 25000 = ₹50,000    │
│    - 25001 < 50000 ✓ OK!                            │
│ 7. Calls: updateAllocation(15, {                    │
│      user_id: 28,                                   │
│      category: "Rent",                              │
│      allocated_amount: 25001,                       │
│      year: 2026,                                    │
│      month: 1                                       │
│    })                                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ api.js (API Service)                                │
│ 1. Adds auth token to request                       │
│ 2. Sends: PUT /api/allocations/15                   │
│    Body: {user_id: 28, category: "Rent", ...}       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ api.py (Backend API)                                │
│ 1. Validates JWT token ✓                            │
│ 2. Extracts user from token                         │
│ 3. Validates request data ✓                         │
│ 4. Calls: db.update_allocation(                     │
│      15,  # allocation_id                           │
│      28,  # user_id (NEW! Was missing before)       │
│      "Rent",  # category                            │
│      25001,   # allocated_amount                    │
│      2026,    # year                                │
│      1        # month                               │
│    )                                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ multi_user_database.py                              │
│ 1. Finds allocation by ID: 15                       │
│ 2. Verifies user owns it (user_id = 28) ✓           │
│ 3. Gets current spent_amount: ₹25,000               │
│ 4. Updates database:                                │
│    UPDATE allocations                               │
│    SET allocated_amount = 25001,                    │
│        balance = 25001 - 25000 = 1                  │
│    WHERE id = 15                                    │
│ 5. Returns: success = true                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ RESPONSE BACK TO USER                               │
│                                                     │
│ API → Mobile: { status: "success" }                 │
│ Mobile Shows: "Budget allocation updated!" ✅        │
│ Screen closes → Returns to Allocations List         │
│ List auto-refreshes → Shows new amount: ₹25,001     │
└─────────────────────────────────────────────────────┘
```

---

## 11. Glossary of Technical Terms

### For Complete Beginners

**API (Application Programming Interface)**
- Simple: The waiter between your app and the database
- Technical: Set of rules for different software to talk to each other

**Authentication**
- Simple: Proving who you are (login)
- Like: Showing ID card at security gate

**Authorization**
- Simple: Checking what you're allowed to do
- Like: ID card shows you can access floor 5 but not floor 10

**Backend**
- Simple: The "behind the scenes" part users don't see
- Does: Processing, calculations, database operations

**Database**
- Simple: Organized storage for all your data
- Like: Filing cabinet with labeled drawers and folders

**Frontend**
- Simple: What you see and interact with
- Includes: Buttons, forms, screens, charts

**JWT (JSON Web Token)**
- Simple: Digital pass that proves you're logged in
- Contains: Your user ID, role, expiration time
- Encrypted: Cannot be faked

**React Native**
- Simple: Technology to build mobile apps
- Benefit: Write code once, works on Android and iOS

**SQL (Structured Query Language)**
- Simple: Language to talk to databases
- Like: Asking questions in a specific format
- Example: "SELECT * FROM users WHERE id = 1" means "Show me user with ID 1"

**Streamlit**
- Simple: Python tool to create web apps easily
- Benefit: No need to write HTML/CSS/JavaScript
- Just: Write Python, get a website

---

## 12. Version History

### v6.1 (Current) - January 18, 2026
**Feature:** Edit Allocation Functionality in Mobile App

**What's New:**
- Edit button on allocation cards
- Can modify existing allocations
- Budget validation during edit
- Proper error messages

**Files Changed:**
- `BudgetTrackerMobile/src/screens/AllocationsListScreen.js`
- `BudgetTrackerMobile/src/screens/AddAllocationScreen.js`
- `BudgetTrackerMobile/App.js`
- `api.py`

### v6.0 - January 2026
**Feature:** Mobile App Improvements
- Fixed allocation deletion
- Added comprehensive error handling

### v5.0 - December 2025
**Features:**
- Savings/Liquidity tracking
- Super Admin "Login as Family"
- Enhanced family overview

### Earlier Versions
- v4.0: Multi-household support
- v3.0: AI Chatbot integration
- v2.0: Period-based allocations
- v1.0: Basic tracking features

---

## 13. Troubleshooting Guide

### Common Issues and Solutions

**Issue 1: "Failed to update allocation"**
**Cause:** Missing required fields in API request
**Solution:** Ensure user_id, year, month are included in update request

**Issue 2: "Over-allocation warning" when editing**
**Cause:** Budget validation was double-counting current allocation
**Solution:** Fixed in v6.1 - now excludes current allocation from total

**Issue 3:** Edit button not visible
**Cause:** Changes not in the correct mobile directory
**Solution:** Verify edits are in `BudgetTrackerMobile/` not `mobile/`

---

## Contact & Support

**For Technical Issues:**
- Check logs in your deployment platform (Render, etc.)
- Review error messages carefully
- Check this guide for explanations

**For Feature Requests:**
- Document your desired feature
- Consider backward compatibility
- Test thoroughly before deploying

---

**End of Comprehensive Guide**

*This document is maintained as part of the Family Budget Tracker project. Last updated with v6.1 features.*
