# Documentation Index

Welcome to the Family Budget Tracker detailed documentation!

## 📁 Documentation Structure

```
docs/
├── COMPREHENSIVE_GUIDE.md          ← Beginner-friendly overview
└── functions/                      ← Detailed function documentation
    ├── web_app_functions_part1.md  ← Authentication & Dashboard (COMPLETE)
    ├── web_app_functions_part2.md  ← Expense Tracking (TO CREATE)
    ├── web_app_functions_part3.md  ← Super Admin (TO CREATE)
    ├── mobile_app_functions.md     ← Mobile screens & API (TO CREATE)
    ├── backend_api_functions.md    ← Backend endpoints (TO CREATE)
    └── database_functions.md       ← Database methods (TO CREATE)
```

## 📚 Available Documentation

### ✅ COMPREHENSIVE_GUIDE.md
**Status:** COMPLETE (600+ lines)  
**Audience:** Complete beginners  
**Coverage:**
- System overview with analogies
- Web application explained (all features)
- Mobile application explained (all screens)
- Backend API explained
- Database schema explained
- Key functions with examples
- Complete data flows (including v6.1 edit allocation)
- User scenarios
- Technical glossary

### ✅ functions/web_app_functions_part1.md
**Status:** COMPLETE  
**Coverage:** 8 authentication and dashboard functions
- `get_database()` - Database initialization
- `show_login_page()` - Authentication router
- `show_landing_page()` - 4-button landing page  
- `show_master_login()` - Super admin login
- `show_admin_login()` - Family admin login
- `show_member_login()` - Member login
- `show_password_setup()` - New member onboarding
- `show_admin_dashboard()` - Admin dashboard (3 tabs)

### ✅ functions/mobile_app_screens_part1.md
**Status:** COMPLETE  
**Coverage:** Overview, navigation, authentication, dashboard
- Mobile app architecture
- Navigation & state management (App.js)
- LoginScreen - 4-role authentication
- DashboardScreen - Home screen with summary cards

### ✅ functions/mobile_app_screens_part2.md  
**Status:** COMPLETE (Most Detailed!)  
**Coverage:** AddAllocationScreen with full v6.1 coverage
- Component structure
- State management
- Data loading
- **Budget validation logic** (line-by-line)
- **v6.1 fixes explained** (edit mode, API parameters)
- Save/update logic
- Complete user journeys
- Before/after v6.1 comparisons

### ✅ functions/mobile_app_screens_part3.md
**Status:** COMPLETE  
**Coverage:** List screens and API service
- AllocationsListScreen (with v6.1 edit button)
- AddExpenseScreen
- AddIncomeScreen
- ExpensesListScreen
- IncomeListScreen
- API service (api.js) - All functions
- Request interceptor
- Error handling patterns

### ✅ functions/backend_api_complete.md
**Status:** COMPLETE  
**Coverage:** All API endpoints with v6.1 fixes
- FastAPI configuration
- JWT authentication system
- Pydantic models
- All authentication endpoints
- All dashboard endpoints
- All income endpoints
- All allocation endpoints (v6.1 update_allocation fix)
- All expense endpoints
- Request/response formats
- Error handling
- Complete request flow examples
- Security features

### ✅ functions/database_layer_complete.md
**Status:** COMPLETE  
**Coverage:** All 58 database methods
- Database schema (5 tables)
- Dual database support (PostgreSQL/SQLite)
- All authentication methods
- All member management methods
- All household management methods
- All income operations
- **All allocation operations** (v6.1 update_allocation fix)
- All expense operations  
- All analytics methods
- Connection management
- Data isolation patterns
- SQL queries for each method

## 🔄 Remaining Function Documentation (TO CREATE)

#### web_app_functions_part2.md
- `show_member_dashboard()` - Member interface
- `show_member_expense_tracking()` - Core tracking UI (2000+ lines!)
  - Income management tab
  - Allocations tab  
  - Expenses tab
  - Review/Dashboard tab
  - All nested helper functions
- `get_user_available_periods()` - Period filtering

#### web_app_functions_part3.md
- `show_super_admin_dashboard()` - System management (560+ lines)
  - Overview tab
  - Families tab
  - Members tab
  - All Users tab
  - Login as Family feature

#### mobile_app_functions.md
- **LoginScreen.js** - Mobile authentication
- **DashboardScreen.js** - Mobile home screen
- **AddIncomeScreen.js** - Add/edit income
- **AddAllocationScreen.js** - Add/edit allocations (with new v6.1 features)
- **AddExpenseScreen.js** - Add/edit expenses
- **IncomeListScreen.js** - Income list view
- **AllocationsListScreen.js** - Allocations list view
- **ExpensesListScreen.js** - Expenses list view
- **api.js** - API service functions

#### backend_api_functions.md
- All `/api/auth/` endpoints
- All `/api/dashboard/` endpoints
- All `/api/income/` endpoints
- All `/api/allocations/` endpoints
- All `/api/expenses/` endpoints
- All `/api/admin/` endpoints
- JWT authentication flow
- Request validation
- Error handling

#### database_functions.md
- `MultiUserDB.__init__()` - Initialization
- `authenticate_user()` - Login validation
- `create_member()` - Member creation
- `accept_invite()` - Password setup
- All income CRUD operations
- All allocation CRUD operations
- All expense CRUD operations
- `update_allocation_spent_amount()` - Auto-sync
- Super admin functions
- Transaction management

## 📊 Documentation Statistics

| Component | Functions | Lines of Code | Doc Status |
|-----------|-----------|---------------|------------|
| Web App | 26 | 2,802 | Part 1 done (8/26) |
| Mobile App | 15 screens | ~150,000 | Not started |
| Backend API | 30+ endpoints | 1,394 | Not started |
| Database | 58 methods | 1,582 | Not started |

**Total Estimated Documentation:** 5,000+ lines

## 🎯 How to Use This Documentation

### For Learning:
1. Start with **COMPREHENSIVE_GUIDE.md** (beginner-friendly)
2. Move to specific function docs when you need details
3. Refer to code alongside documentation

### For Development:
1. Find the function you're working on
2. Read its detailed documentation
3. Understand parameters, returns, side effects
4. Follow examples and patterns

### For Debugging:
1. Identify which function is causing issues
2. Read its step-by-step execution flow
3. Check example data formats
4. Verify your inputs match expected format

## 🔍 Quick Function Lookup

### Authentication
- Login: `show_master_login()`, `show_admin_login()`, `show_member_login()`
- Onboarding: `show_password_setup()`

### Data Operations
- Income: `add_income()`, `get_income()`, `update_income()`, `delete_income()`
- Allocations: `add_allocation()`, `update_allocation()`, etc.
- Expenses: `add_expense()`, `update_expense()`, etc.

### Views
- Dashboards: `show_admin_dashboard()`, `show_member_dashboard()`, `show_super_admin_dashboard()`
- Tracking: `show_member_expense_tracking()`

## 📝 Documentation Standards

Each function is documented with:
1. **Location** - File and line numbers
2. **Purpose** - What it does in simple terms
3. **Signature** - Exact function declaration
4. **Parameters** - Each parameter explained
5. **Returns** - What it gives back
6. **Step-by-Step** - Line-by-line execution
7. **Examples** - Real data examples
8. **Dependencies** - What it uses
9. **Security** - Security considerations
10. **Diagrams** - Flow charts where helpful

## 🛠️ Contributing to Documentation

When adding new functions:
1. Follow the same format as existing docs
2. Include code snippets
3. Add real examples
4. Explain the "why" not just the "what"
5. Use analogies for complex concepts

## 📞 Questions?

If you need documentation for a specific function:
1. Check this index
2. Look in the appropriate file
3. If not documented yet, request it

---

**Last Updated:** January 18, 2026  
**Version:** v6.1  
**Documentation Progress:** 20% Complete
