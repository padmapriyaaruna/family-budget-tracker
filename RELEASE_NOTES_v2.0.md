# Version 2.0 Release Notes

**Release Date:** December 29, 2025  
**Tag:** v2.0  
**Status:** ✅ Stable

## 🎉 Major Features

### Excel-Like Inline Editing
- **Complete row-level editing** for Income, Allocations, and Expenses sections
- **Excel-like table format** matching Dashboard's "Allocation Status" appearance
- **Clean dataframe-based UI** with proper borders and compact rows
- **Professional appearance** with visible column separators

### Edit/Delete Workflow
- Select entries from dropdown below each table
- Edit forms appear in expandable sections
- Side-by-side Save/Delete buttons
- Clean, uncluttered interface

### Dashboard Enhancements
- **"Recalculate Spent Amounts" button** to sync allocation data from expenses
- Fixes data integrity issues without needing shell access

## 🔧 Technical Improvements

### Database Layer
- Fixed PostgreSQL compatibility in `get_income_with_ids()`
- Fixed PostgreSQL compatibility in `get_allocations_with_ids()`
- Fixed PostgreSQL compatibility in `get_expenses_with_ids()`
- Added `update_allocation()` method for ID-based updates
- Added `delete_allocation_by_id()` method

### Type Conversion Fixes
- Resolved Decimal to float conversion errors in:
  - `update_allocation_spent()`
  - `update_allocation_amount()`
  - `update_allocation()`
  - `update_expense()`
  - `delete_expense()`

### UI/UX Improvements
- Removed duplicate button key conflicts with unique prefixes
- Simplified CSS for clean column separators
- Replaced `st.columns()` with `st.dataframe()` for proper table appearance
- Consistent design across all three editing sections

## 📋 Sections Updated

### 1. Income Section
- **Columns:** Date | Source | Amount
- **Features:** Add, Edit, Delete income entries
- **Display:** Clean dataframe table

### 2. Allocations Section  
- **Columns:** Category | Allocated | Spent | Balance
- **Features:** Add, Edit, Delete allocations
- **Auto-calculation:** Balance = Allocated - Spent

### 3. Expenses Section
- **Columns:** Date | Category | Amount | Comment
- **Features:** Add, Edit, Delete expenses
- **Limitation:** Shows first 20 entries for performance

## 🐛 Bug Fixes

1. ✅ Fixed "No data displaying" issue - PostgreSQL parameter placeholder mismatch
2. ✅ Fixed "Failed to update expense" - Decimal type errors
3. ✅ Fixed duplicate element keys across sections
4. ✅ Fixed buttons overflowing borders - removed use_container_width
5. ✅ Fixed spent amounts showing zero - added recalculation utility

## 🔄 Migration from v1.0

No database schema changes required. Simply:
1. Pull latest code
2. Redeploy application
3. Click "Recalculate Spent Amounts" in Dashboard if needed

## 📦 Rollback Instructions

To rollback to v1.0:
```bash
git checkout v1.0
git push origin main --force
```

## 🚀 What's Next (Future Versions)

Potential features for v3.0:
- Bulk import/export functionality
- Advanced filtering and search
- Data visualization enhancements
- Mobile responsiveness improvements
- Expense categories with icons

---

**Developed by:** Antigravity AI  
**Repository:** https://github.com/padmapriyaaruna/family-budget-tracker  
**License:** MIT
