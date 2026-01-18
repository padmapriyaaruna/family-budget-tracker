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
- System overview
- Web application explained
- Mobile application explained
- Backend API explained
- Database schema explained
- Key functions with analogies
- Complete data flows
- User scenarios

### ✅ web_app_functions_part1.md
**Status:** COMPLETE  
**Coverage:**
- `get_database()` - Database initialization
- `show_login_page()` - Authentication router
- `show_landing_page()` - 4-button landing page
- `show_master_login()` - Super admin login
- `show_admin_login()` - Family admin login  
- `show_member_login()` - Member login
- `show_password_setup()` - New member onboarding
- `show_admin_dashboard()` - Admin dashboard (3 tabs)

**Detail Level:**
- Line-by-line code explanation
- Parameter descriptions
- Return values
- Step-by-step execution flow
- Example data
- Security considerations
- Complete user journeys

### 🔄 Remaining Function Documentation (TO CREATE)

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
