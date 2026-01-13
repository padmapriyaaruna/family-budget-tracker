# Family Budget Tracker - Technical Blueprint

**Version:** v5.1  
**Last Updated:** 2026-01-02  
**Project Type:** Multi-User Web Application  
**Framework:** Streamlit  
**Database:** PostgreSQL (Production) / SQLite (Development)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Module Documentation](#module-documentation)
4. [Database Schema](#database-schema)
5. [User Flows](#user-flows)
6. [Dependencies](#dependencies)
7. [Configuration](#configuration)
8. [Deployment](#deployment)

---

## 1. Project Overview

### Purpose
Family Budget Tracker is a multi-user financial management system that allows families to track income, allocations, and expenses across multiple members with role-based access control.

### Key Features
- **Multi-Household Support**: Super admin manages multiple families
- **Role-Based Access**: Super Admin, Family Admin, and Family Member roles
- **Budget Management**: Period-based (year/month) income and allocation tracking
- **Expense Tracking**: Categorized and subcategorized expenses
- **AI Chatbot**: Gemini-powered chatbot for querying financial data
- **Data Visualization**: Charts and graphs for financial insights

### Technology Stack
- **Backend**: Python 3.x
- **Frontend**: Streamlit
- **Database**: PostgreSQL (production), SQLite (development)
- **AI**: Google Gemini API (gemini-1.5-flash)
- **Visualization**: Plotly
- **Deployment**: Streamlit Cloud, Render, Hugging Face Spaces

---

## 2. Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                 USER INTERFACE                       │
│              (Streamlit Web App)                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  family_expense_tracker.py                  │   │
│  │  - Authentication Pages                      │   │
│  │  - Dashboard Views                           │   │
│  │  - CRUD Operations                           │   │
│  └─────────────────────────────────────────────┘   │
└────────────┬──────────────────────────────┬─────────┘
             │                              │
             ▼                              ▼
┌───────────────────────┐    ┌──────────────────────────┐
│  DATABASE LAYER       │    │  AI CHATBOT ENGINE       │
│  multi_user_database  │    │  chatbot_engine.py       │
│  .py                  │    │  - LLM Client            │
│  - User Management    │    │  - Document Retriever    │
│  - Data Operations    │    │  - Text-to-SQL Engine    │
│  - Role-Based Access  │    └──────────────────────────┘
└───────────────────────┘
             │
             ▼
┌───────────────────────┐
│  DATABASE             │
│  PostgreSQL/SQLite    │
│  - households         │
│  - users              │
│  - income             │
│  - allocations        │
│  - expenses           │
└───────────────────────┘
```

### Component Breakdown

#### 1. **User Interface Layer**
- **File**: `family_expense_tracker.py` (2,480 lines)
- **Responsibilities**:
  - User authentication and session management
  - Dashboard rendering for all user roles
  - Form handling for CRUD operations
  - Data visualization
  - Chatbot integration

#### 2. **Database Layer**
- **File**: `multi_user_database.py` (1,582 lines)
- **Responsibilities**:
  - Database connection management
  - User authentication and authorization
  - Data isolation by household
  - CRUD operations for all entities
  - Role-based access control

#### 3. **AI Chatbot Layer**
- **File**: `chatbot_engine.py` (515 lines)
- **Responsibilities**:
  - Natural language processing
  - Intent classification
  - Text-to-SQL conversion
  - RAG document retrieval
  - Response generation

#### 4. **Configuration**
- **File**: `config.py` (32 lines)
- **Responsibilities**:
  - Application constants
  - API keys and credentials
  - Feature flags

---

## 3. Module Documentation

### 3.1 family_expense_tracker.py

**Main application file** - Streamlit UI and user interaction

#### Functions (26 total)

##### Authentication Functions

1. **`show_login_page()`**
   - **Purpose**: Main login router
   - **Parameters**: None
   - **Returns**: None
   - **Description**: Displays landing page or redirects to specific login screen
   
2. **`show_landing_page()`**
   - **Purpose**: Display 4-button navigation (Master, Admin, Member, Password Setup)
   - **Parameters**: None
   - **Returns**: None
   - **UI Elements**: 4 buttons for role selection
   
3. **`show_master_login()`**
   - **Purpose**: Super admin password-only login
   - **Parameters**: None
   - **Returns**: None
   - **Authentication**: Password-only, defaults to 'superadmin' user
   
4. **`show_admin_login()`**
   - **Purpose**: Family admin email/password login
   - **Parameters**: None
   - **Returns**: None
   - **Authentication**: Email + password validation
   
5. **`show_member_login()`**
   - **Purpose**: Family member email/password login
   - **Parameters**: None
   - **Returns**: None
   - **Authentication**: Email + password validation
   
6. **`show_password_setup()`**
   - **Purpose**: New member password setup using invite token
   - **Parameters**: None
   - **Returns**: None
   - **Process**: Token validation → password creation → account activation

##### Dashboard Functions

7. **`show_admin_dashboard()`**
   - **Purpose**: Family admin main dashboard
   - **Parameters**: None (uses session state)
   - **Features**:
     - Personal expense tracking
     - Family overview
     - Member management
   - **Tabs**: 3 tabs (My Expenses, Family Overview, Manage Members)
   
8. **`show_member_dashboard()`**
   - **Purpose**: Family member main dashboard
   - **Parameters**: None (uses session state)
   - **Features**: Personal expense tracking only
   - **Delegates to**: `show_member_expense_tracking()`
   
9. **`show_super_admin_dashboard()`**
   - **Purpose**: Super admin system management
   - **Parameters**: None
   - **Features**:
     - System overview statistics
     - Household management
     - User management
     - Member role management
   - **Tabs**: 4 tabs (Overview, Families, Members, All Users)

##### Core Tracking Functions

10. **`show_member_expense_tracking(user_id)`**
    - **Purpose**: Shared expense tracking UI
    - **Parameters**: `user_id` (int)
    - **Returns**: None
    - **Features**:
      - Income management
      - Budget allocations
      - Expense tracking
      - Financial review dashboard
    - **Tabs**: 4 tabs using st.radio() (Income, Allocations, Expenses, Review)
    - **Session State**: `active_tab` for tab preservation

##### Helper Functions

11. **`get_database()`**
    - **Purpose**: Initialize database connection
    - **Parameters**: None
    - **Returns**: `MultiUserDB` instance
    - **Checks**: DATABASE_URL environment variable
    
12. **`get_user_available_periods(db, user_ids)`**
    - **Purpose**: Get available year/month combinations for users
    - **Parameters**: 
      - `db`: Database instance
      - `user_ids`: List[int]
    - **Returns**: List of (year, month) tuples
    - **Use Case**: Filter dropdown population

13. **`update_budget_year()` and `update_budget_month()`**
    - **Purpose**: Update session state for budget period
    - **Parameters**: None (callbacks)
    - **Returns**: None
    - **Session State**: Updates `budget_year` and `budget_month`

14. **`main()`**
    - **Purpose**: Main application entry point
    - **Flow**:
      1. Check authentication status
      2. Route to login or dashboard
      3. Render chatbot widget
    - **Session State Check**: `logged_in`, `user`

##### Nested Functions

15-26. **Various nested helper functions** within main dashboard functions for:
- Period selection
- Data filtering
- Chart generation
- Form validation

---

### 3.2 multi_user_database.py

**Database abstraction layer** - All database operations

#### Class: MultiUserDB

##### Core Methods (58 total)

**Initialization & Connection**

1. **`__init__(self, db_path=None)`**
   - **Purpose**: Initialize database connection
   - **Parameters**: `db_path` (str, optional)
   - **Auto-detects**: PostgreSQL via DATABASE_URL or SQLite
   - **Initializes**: Tables and migrations
   
2. **`_ensure_connection(self)`**
   - **Purpose**: Check and reconnect if needed
   - **Returns**: None
   - **Error Handling**: Automatic reconnection
   
3. **`_execute(self, cursor, query, params=None)`**
   - **Purpose**: Execute query with correct parameter syntax
   - **Handles**: %s (PostgreSQL) vs ? (SQLite)
   - **Returns**: None

**Table Management**

4. **`_initialize_tables(self)`**
   - **Purpose**: Create all tables if not exist
   - **Tables Created**: households, users, income, allocations, expenses
   - **Migrations**: Runs automatic migrations
   
5. **`_migrate_add_period_columns(self)`**
   - **Purpose**: Add year/month columns to allocations
   - **Version**: Added in v2.0
   
6. **`_migrate_add_subcategory_column(self)`**
   - **Purpose**: Add subcategory column to expenses
   - **Version**: Added in v2.1

**User Authentication**

7. **`_hash_password(self, password)`**
   - **Algorithm**: SHA256
   - **Returns**: Hashed password (str)
   
8. **`_create_super_admin(self)`**
   - **Default Credentials**: 'superadmin' with configurable password
   - **Auto-creates**: Default super admin account
   
9. **`create_admin_user(self, email, password, full_name, household_name)`**
   - **Purpose**: Create new family admin and household
   - **Returns**: (success: bool, message: str)
   - **Creates**: Household + Admin user
   
10. **`authenticate_user(self, email, password)`**
    - **Purpose**: Validate credentials and return user info
    - **Returns**: User dict or None
    - **Checks**: Password hash, active status, household status

**Member Management**

11. **`generate_invite_token(self)`**
    - **Purpose**: Generate unique 32-character token
    - **Algorithm**: secrets.token_hex(16)
    - **Returns**: str
    
12. **`create_member(self, household_id, email, full_name, relationship, created_by_admin_id)`**
    - **Purpose**: Create new family member with invite token
    - **Returns**: (success: bool, invite_token: str or None)
    - **Initial State**: Invite pending, no password
    
13. **`accept_invite(self, invite_token, new_password)`**
    - **Purpose**: Activate member account with password
    - **Returns**: (success: bool, message: str)
    - **Updates**: Password, clears token, activates account
    
14. **`get_household_members(self, household_id)`**
    - **Purpose**: Get all members in a family
    - **Returns**: List[Dict]
    - **Includes**: All user fields
    
15. **`get_user_by_id(self, user_id)`**
    - **Purpose**: Get single user details
    - **Returns**: Dict or None
    
16. **`deactivate_member(self, member_id)`**
    - **Purpose**: Soft delete (set is_active=0)
    - **Returns**: bool
    
17. **`delete_member(self, member_id)`**
    - **Purpose**: Hard delete member and all data
    - **Cascades**: Deletes income, allocations, expenses
    - **Security**: Invalidates invite token

**Household Management (Super Admin)**

18. **`get_all_households(self)`**
    - **Purpose**: Get all families in system
    - **Returns**: List[Dict] with household info
    - **Includes**: Name, admin count, member count, status
    
19. **`create_household_with_admin(self, household_name, admin_email, admin_name)`**
    - **Purpose**: Create family with invite token for admin
    - **Returns**: (success: bool, invite_token: str or None)
    - **Process**: Create household → Create admin (pending) → Generate token
    
20. **`toggle_household_status(self, household_id)`**
    - **Purpose**: Enable/disable a family
    - **Returns**: bool
    - **Effect**: Affects all family members' access
    
21. **`delete_household(self, household_id)`**
    - **Purpose**: Completely remove household and all data
    - **Cascades**: Users, income, allocations, expenses
    - **Returns**: bool

**User Management (Super Admin)**

22. **`get_all_users_super_admin(self)`**
    - **Purpose**: Get all users across all households
    - **Returns**: List[Dict]
    - **Includes**: Household name via JOIN
    
23. **`get_system_statistics(self)`**
    - **Purpose**: System-wide metrics
    - **Returns**: Dict with counts
    - **Metrics**: Total households, users, active users, income, allocations, expenses
    
24. **`promote_member_to_admin(self, user_id, household_id)`**
    - **Purpose**: Elevate member to family admin
    - **Returns**: bool
    - **Validation**: Must be same household
    
25. **`demote_admin_to_member(self, user_id, household_id)`**
    - **Purpose**: Downgrade admin to member
    - **Returns**: bool
    - **Rule**: Must maintain at least 1 admin per household
    
26. **`count_household_admins(self, household_id)`**
    - **Purpose**: Count admins in family
    - **Returns**: int
    
27. **`reset_user_password(self, user_id)`**
    - **Purpose**: Generate new invite token for password reset
    - **Returns**: (success: bool, invite_token: str or None)
    - **Clears**: Existing password

**Income Operations**

28. **`add_income(self, user_id, date, source, amount)`**
    - **Purpose**: Record income entry
    - **Returns**: bool
    - **Validation**: user_id exists
    
29. **`get_income(self, user_id, year=None, month=None)`**
    - **Purpose**: Retrieve income records
    - **Parameters**: Optional period filter
    - **Returns**: List[Dict]
    
30. **`update_income(self, income_id, date, source, amount)`**
    - **Purpose**: Modify existing income
    - **Returns**: bool
    
31. **`delete_income(self, income_id)`**
    - **Purpose**: Remove income record
    - **Returns**: bool

**Allocation Operations**

32. **`add_allocation(self, user_id, category, allocated_amount, year, month)`**
    - **Purpose**: Create budget allocation
    - **Returns**: bool
    - **Initial Values**: spent_amount=0, balance=allocated_amount
    
33. **`get_all_allocations(self, user_id, year=None, month=None)`**
    - **Purpose**: Retrieve allocations
    - **Returns**: List[Dict]
    - **Sorting**: By category
    
34. **`get_categories(self, user_id, year=None, month=None)`**
    - **Purpose**: Get distinct categories
    - **Returns**: List[str]
    - **Use Case**: Dropdown population
    
35. **`get_allocation_spent_amount(self, user_id, category, year, month)`**
    - **Purpose**: Calculate actual spent from expenses
    - **Returns**: float
    - **Formula**: SUM(expenses.amount) WHERE category = category
    
36. **`update_allocation(self, allocation_id, category, allocated_amount, year, month)`**
    - **Purpose**: Modify allocation
    - **Returns**: bool
    - **Recalculates**: balance = allocated - spent
    
37. **`update_allocation_spent_amount(self, user_id, category, year, month)`**
    - **Purpose**: Sync spent_amount with actual expenses
    - **Returns**: bool
    - **Automatic**: Called on expense add/update/delete
    
38. **`delete_allocation(self, allocation_id)`**
    - **Purpose**: Remove allocation
    - **Returns**: bool
    
39. **`copy_previous_month_allocations(self, user_id, from_year, from_month, to_year, to_month)`**
    - **Purpose**: Duplicate allocations to new period
    - **Returns**: (success: bool, count: int)
    - **Resets**: spent_amount=0, balance=allocated_amount

**Expense Operations**

40. **`add_expense(self, user_id, date, category, subcategory, amount, comment)`**
    - **Purpose**: Record expense
    - **Returns**: bool
    - **Side Effect**: Updates allocation spent_amount
    
41. **`get_expenses(self, user_id, year=None, month=None)`**
    - **Purpose**: Retrieve expenses
    - **Returns**: List[Dict]
    - **Sorting**: By date DESC
    
42. **`update_expense(self, expense_id, date, category, subcategory, amount, comment)`**
    - **Purpose**: Modify expense
    - **Returns**: bool
    - **Side Effect**: Updates allocation spent_amount
    
43. **`delete_expense(self, expense_id)`**
    - **Purpose**: Remove expense
    - **Returns**: bool
    - **Side Effect**: Updates allocation spent_amount

**Analytics & Reporting**

44. **`get_family_total_income(self, household_id, year=None, month=None)`**
    - **Purpose**: Sum income across all family members
    - **Returns**: float
    
45. **`get_family_total_expenses(self, household_id, year=None, month=None)`**
    - **Purpose**: Sum expenses across all family members
    - **Returns**: float
    
46. **`get_category_expenses(self, user_id, category, year=None, month=None)`**
    - **Purpose**: Get expenses for specific category
    - **Returns**: List[Dict]
    
47. **`execute_chatbot_query(self, sql_query, user_id, family_id, role)`**
    - **Purpose**: Execute AI-generated SQL with safety checks
    - **Returns**: List[Tuple]
    - **Security**: Validates SELECT only, enforces household_id filter

**Utility Methods**

48-58. Additional helper methods for:
- Date parsing
- Data validation
- Transaction management
- Error handling

---

### 3.3 chatbot_engine.py

**AI Chatbot System** - Natural language processing and query handling

#### Class: LLMClient

**Purpose**: Wrapper for Google Gemini API

1. **`__init__(self, api_key=None)`**
   - **API**: Google Gemini (gemini-2.0-flash-exp)
   - **Fallback**: Checks GEMINI_API_KEY or GOOGLE_API_KEY env vars
   
2. **`generate_response(self, prompt, system_instruction="")`**
   - **Purpose**: Single-shot response generation
   - **Returns**: str
   - **Temperature**: 0.7
   
3. **`start_chat(self, system_instruction="")`**
   - **Purpose**: Initialize chat session
   - **Maintains**: Conversation history
   
4. **`send_message(self, message)`**
   - **Purpose**: Continue chat session
   - **Returns**: str

#### Class: DocumentRetriever

**Purpose**: RAG system for documentation retrieval

1. **`__init__(self, docs_directory)`**
   - **Loads**: All .md files from directory
   - **Indexes**: File names and content
   
2. **`_load_documents(self)`**
   - **Format**: {filename: content}
   - **Encoding**: UTF-8
   
3. **`retrieve_relevant_docs(self, query, max_docs=3)`**
   - **Algorithm**: Simple keyword matching
   - **Scoring**: Count of keyword matches
   - **Returns**: Top N relevant documents

#### Class: TextToSQLEngine

**Purpose**: Convert natural language to safe SQL

1. **`__init__(self, llm_client)`**
   - **Dependencies**: LLMClient instance
   - **Schema**: Loads database schema definition
   
2. **`_get_schema_definition(self)`**
   - **Returns**: Complete database schema documentation
   - **Includes**:
     - Table definitions
     - Subcategory mappings
     - Query examples
     - Month name to number mappings
   
3. **`generate_sql(self, query, user_id, family_id, role)`**
   - **Process**:
     1. Build prompt with schema + context
     2. Generate SQL via LLM
     3. Clean markdown code blocks
     4. Validate safety
   - **Returns**: (sql_query, explanation)
   
4. **`_is_safe_query(self, sql, user_id, family_id, role)`**
   - **Validation**:
     - SELECT only (no INSERT/UPDATE/DELETE/DROP)
     - household_id filter present
     - Role-based user_id restriction
   - **Returns**: (is_safe: bool, debug_msg: str)

#### Class: ChatbotEngine

**Purpose**: Main orchestrator for chatbot interactions

1. **`__init__(self, docs_directory, api_key=None)`**
   - **Initializes**: LLM, DocumentRetriever, TextToSQLEngine
   - **Components**: All three sub-systems
   
2. **`_build_system_instruction(self, user_id, family_id, role, full_name)`**
   - **Purpose**: Create personalized system prompt
   - **Includes**: User context, role, capabilities
   - **Returns**: str
   
3. **`_classify_intent(self, query)`**
   - **Purpose**: Determine if query is about data or general help
   - **Keywords**: expense, income, allocation, spent, budget, etc.
   - **Returns**: "data" or "general"
   
4. **`process_query(self, query, user_id, family_id, role, full_name, db_connection)`**
   - **Main Entry Point**
   - **Flow**:
     1. Build system instruction
     2. Classify intent
     3. Route to data or general handler
     4. Return response
   - **Returns**: str (AI response)
   
5. **`_handle_data_query(self, query, user_id, family_id, role, system_instruction, db_connection)`**
   - **Process**:
     1. Generate SQL via TextToSQLEngine
     2. Execute SQL via database
     3. Format results for LLM
     4. Generate natural language response
   - **Returns**: str
   
6. **`_handle_general_query(self, query, system_instruction)`**
   - **Process**:
     1. Retrieve relevant documentation
     2. Build prompt with context
     3. Generate response via LLM
   - **Returns**: str

---

### 3.4 config.py

**Configuration Constants**

```python
DATABASE_PATH = "expense_tracker.db"  # SQLite fallback
CURRENCY_SYMBOL = "₹"
DATE_FORMAT = "%Y-%m-%d"
CHATBOT_ENABLED = True
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
CHATBOT_MODEL = "gemini-1.5-flash"
MAX_CHAT_HISTORY = 10
CHATBOT_DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
```

---

## 4. Database Schema

### Tables

#### 4.1 households
```sql
CREATE TABLE households (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
**Purpose**: Represents families/groups  
**Relationships**: 1:N with users

#### 4.2 users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    relationship TEXT,
    invite_token TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id)
)
```
**Purpose**: User accounts with role-based access  
**Roles**: 'superadmin', 'admin', 'member'  
**Special**: Super admin has household_id=0

#### 4.3 income
```sql
CREATE TABLE income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    source TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```
**Purpose**: Income tracking per user  
**Date Format**: YYYY-MM-DD

#### 4.4 allocations
```sql
CREATE TABLE allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    allocated_amount REAL NOT NULL,
    spent_amount REAL DEFAULT 0,
    balance REAL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```
**Purpose**: Budget allocations per category per period  
**Period**: (year, month) combination  
**Auto-calculated**: balance = allocated_amount - spent_amount

#### 4.5 expenses
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    amount REAL NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```
**Purpose**: Daily expense tracking  
**Subcategories**: Investment, Food - Online, Food - Hotel, Grocery - Online, Grocery - Offline, School Fee, Extra-Curricular, Co-Curricular, House Rent, Maintenance, Vehicle, Gadgets, Others

### Entity Relationships

```
households (1) ----< (N) users
users (1) ----< (N) income
users (1) ----< (N) allocations
users (1) ----< (N) expenses
```

---

## 5. User Flows

### 5.1 Super Admin Flow

1. **Login**: Password-only authentication
2. **Dashboard**: System overview with statistics
3. **Household Management**:
   - Create household → Generate admin invite token
   - Enable/disable household
   - Delete household (cascades all data)
4. **User Management**:
   - View all users
   - Promote member → admin
   - Demote admin → member
   - Reset user password

### 5.2 Family Admin Flow

1. **Login**: Email + password authentication
2. **Dashboard**: 3 tabs
   - **My Expenses**: Personal tracking (Income, Allocations, Expenses, Review)
   - **Family Overview**: Aggregated family data
   - **Manage Members**: Add/deactivate/delete members
3. **Member Management**:
   - Create member → Generate invite token → Share with member
   - View member list
   - Delete members

### 5.3 Family Member Flow

1. **Login**: Email + password (after accepting invite)
2. **Dashboard**: Personal tracking only
   - Income management
   - Budget allocations
   - Expense tracking
   - Financial review

### 5.4 Chatbot Flow

1. **User**: Asks question in natural language
2. **Intent Classification**: "data" vs "general"
3. **Data Query Path**:
   - Natural language → SQL (via TextTo SQLEngine)
   - SQL execution (with safety validation)
   - Results → Natural language response
4. **General Query Path**:
   - Retrieve relevant documentation (via RAG)
   - Generate response with context

---

## 6. Dependencies

### Python Packages (requirements.txt)

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.14.0
google-generativeai>=0.3.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
```

### External Services

1. **Google Gemini API**
   - Model: gemini-2.0-flash-exp
   - Purpose: AI chatbot responses
   - Authentication: API key via environment variable

2. **PostgreSQL Database**
   - Production: Via DATABASE_URL environment variable
   - Connection: psycopg2-binary driver
   - Pooler support: Supabase/Neon compatible

3. **Streamlit Cloud**
   - Deployment platform
   - Environment variables: GEMINI_API_KEY, DATABASE_URL

---

## 7. Configuration

### Environment Variables

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Production | `postgresql://user:pass@host:5432/db` |
| `GEMINI_API_KEY` | Google API key for chatbot | If chatbot enabled | `AIza...` |
| `GOOGLE_API_KEY` | Alternative API key name | Fallback | `AIza...` |

### Streamlit Secrets

Store in `.streamlit/secrets.toml`:

```toml
[general]
GEMINI_API_KEY = "your-api-key"
DATABASE_URL = "postgresql://..."
```

---

## 8. Deployment

### Supported Platforms

1. **Streamlit Cloud**
   - Main: `streamlit_app.py` → imports `family_expense_tracker.py`
   - Secrets: Via dashboard settings
   
2. **Render**
   - Web Service configuration
   - Environment variables in dashboard
   
3. **Hugging Face Spaces**
   - Dockerfile included
   - Secrets via Space settings

### Deployment Checklist

- [ ] Set DATABASE_URL environment variable
- [ ] Set GEMINI_API_KEY environment variable
- [ ] Verify PostgreSQL database is accessible
- [ ] Run database migrations (automatic on first run)
- [ ] Test super admin login (default password)
- [ ] Create test household and members

---

## 9. Key Design Patterns

### 1. Role-Based Access Control (RBAC)

```python
# Data isolation by household
if role == 'member':
    WHERE user_id = {user_id}
elif role == 'admin':
    WHERE household_id = {family_id}
elif role == 'superadmin':
    # No restriction
```

### 2. Session State Management

```python
# Tab preservation across reruns
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

selected_tab = st.radio(..., index=st.session_state.active_tab)
st.session_state.active_tab = tab_options.index(selected_tab)
```

### 3. Database Abstraction

```python
# Automatic PostgreSQL/SQLite detection
USE_POSTGRES = os.getenv('DATABASE_URL') is not None

# Unified query execution
self._execute(cursor, query, params)
```

### 4. AI Safety Validation

```python
# SQL safety checks
1. SELECT only (no mutations)
2. household_id filter mandatory
3. user_id restriction for members
4. No dangerous keywords (DROP, DELETE, etc.)
```

---

## 10. Future Enhancements

- [ ] Export to PDF/Excel
- [ ] Recurring allocations
- [ ] Budget alerts and notifications
- [ ] Multi-currency support
- [ ] Mobile app (React Native)
- [ ] Receipt photo upload
- [ ] Bank integration
- [ ] Predictive budgeting with AI

---

## Document Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-02 | Initial comprehensive blueprint |

---

**Contact**: For questions or contributions, see project README.md
