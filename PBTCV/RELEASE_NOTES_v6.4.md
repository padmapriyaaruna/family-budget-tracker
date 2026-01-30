# Release Notes - Version 6.4

**Release Date:** January 31, 2026  
**Version:** 6.4  
**Type:** Feature Enhancement & Bug Fixes

## 🎯 Overview

Version 6.4 brings significant improvements to the mobile app's dashboard experience, period management across screens, data validation, and missing API endpoints for member management.

---

## ✨ New Features

### 1. **Dynamic Savings Status Grades** 🏆
Enhanced the Dashboard savings card to show intelligent status labels based on savings percentage:

- **Excellent** - Savings ≥ 75% of income (Outstanding financial health)
- **Good** - Savings 50-74% of income (Strong savings habits)
- **Moderate** - Savings 25-49% of income (Room for improvement)
- **Low** - Savings 0-24% of income (Need to save more)
- **Deficit** - Negative savings (Spending exceeds income)

**Files Modified:**
- `BudgetTrackerMobile/src/screens/DashboardScreen.js`

**User Impact:** Users now get instant feedback on their financial health at a glance.

---

### 2. **Period Synchronization Across All Screens** 📅
Implemented global period state management using `BudgetPeriodContext`:

**Behavior:**
- When you select **Feb 2026** in Dashboard picker, ALL other screens (Expenses, Income, Allocations) automatically filter to show **only Feb 2026** data
- Period changes trigger automatic data refresh
- Consistent experience across entire app

**Screens Updated:**
- `DashboardScreen.js` - Sets global period
- `ExpensesListScreen.js` - Reads and responds to period changes
- `IncomeListScreen.js` - Reads and responds to period changes
- `AllocationsListScreen.js` - Reads and responds to period changes

**User Impact:** No more confusion - when you pick a month, ALL data reflects that month!

---

### 3. **Data Validation Disclaimers** ⚠️
Added intelligent validation to prevent incomplete data entry:

#### AddAllocationScreen
- **Check:** Validates income exists for selected period before allowing allocation creation
- **Alert:** "You must add income for {month}/{year} before creating allocations"
- **Action:** Auto-closes screen if no income found (edit mode exempt)

#### AddExpenseScreen
- **Check:** Validates allocations exist for selected period before allowing expense creation
- **Alert:** "You must add budget allocations for {month}/{year} before adding expenses"
- **Action:** Auto-closes screen if no allocations found (edit mode exempt)
- **Bonus:** Categories dropdown now filters by selected period

**Files Modified:**
- `BudgetTrackerMobile/src/screens/AddAllocationScreen.js`
- `BudgetTrackerMobile/src/screens/AddExpenseScreen.js`

**User Impact:** Enforces proper workflow - Income → Allocations → Expenses. No more orphaned data!

---

### 4. **Dashboard UI Improvements** 🎨

#### Period Picker Visibility
- Increased label font size from 12 to 14
- Changed label color from light gray to dark for better contrast
- Made labels bold
- Increased picker height from 40 to 50

**User Impact:** Month and year pickers are now much more readable.

#### Budget Used Card Cleanup
- **Removed:** Budget calculation text ("₹X / ₹Y") that cluttered the card
- **Shows:** Just the percentage and card title

**User Impact:** Cleaner, less cluttered dashboard cards.

---

## 🔧 Backend API Enhancements

### 5. **Add Member Endpoint** (NEW) 👥
Created missing endpoint for family admins to add household members via mobile app.

**Endpoint:** `POST /api/households/{household_id}/members`

**Features:**
- Permission check: Only family admins and super admins can add members
- Email validation: Prevents duplicate emails
- Auto-generates temporary password for new members
- Returns member details on success

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "relationship": "Son"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Member John Doe added successfully",
  "data": {
    "member_id": 45,
    "household_id": 12,
    "name": "John Doe",
    "email": "john@example.com",
    "relationship": "Son",
    "note": "A temporary password has been set. Member should be invited to set their own password."
  }
}
```

**Files Modified:**
- `api.py` (lines 102-107, 1571-1642)

**User Impact:** Family admins can now successfully add members from mobile app!

---

### 6. **Delete User Endpoint** (NEW) 🗑️
Created missing endpoint for super admins to delete family members.

**Endpoint:** `DELETE /api/admin/users/{user_id}`

**Features:**
- Permission check: Super admin only
- Cascade delete: Removes user's expenses, income, allocations, and savings
- User existence validation
- Returns success message with deleted user name

**Response:**
```json
{
  "status": "success",
  "message": "User Sarah Smith (ID: 44) and all associated data deleted successfully"
}
```

**Files Modified:**
- `api.py` (lines 1644-1701)

**User Impact:** Super admins can now successfully delete members from mobile app!

---

### 7. **Dashboard Budget Percentage Fix** 🐛
Fixed critical bug where Budget Used showed 0% despite having allocations.

**Root Cause:** Dashboard API was looking for `allocated_amount` and `spent_amount` fields, but database returns `"Allocated Amount"` and `"Spent Amount"` (Title Case with spaces).

**Solution:** Updated endpoint to check both field format variations.

**Files Modified:**
- `api.py` (lines 839-856)

**User Impact:** Budget percentage now displays correctly (e.g., "98.5%" instead of "0%")!

---

## 📱 Mobile App Files Modified

1. `BudgetTrackerMobile/src/screens/DashboardScreen.js`
   - Added `getSavingsStatus()` function
   - Integrated `useBudgetPeriod` context hook
   - Improved period picker styling
   - Removed budget calculation text

2. `BudgetTrackerMobile/src/screens/ExpensesListScreen.js`
   - Integrated `useBudgetPeriod` context hook
   - Auto-refresh on period change

3. `BudgetTrackerMobile/src/screens/IncomeListScreen.js`
   - Integrated `useBudgetPeriod` context hook
   - Auto-refresh on period change

4. `BudgetTrackerMobile/src/screens/AllocationsListScreen.js`
   - Integrated `useBudgetPeriod` context hook
   - Auto-refresh on period change

5. `BudgetTrackerMobile/src/screens/AddAllocationScreen.js`
   - Added income validation with disclaimer
   - Integrated period context

6. `BudgetTrackerMobile/src/screens/AddExpenseScreen.js`
   - Added allocation validation with disclaimer
   - Integrated period context
   - Period-filtered category dropdown

---

## 🌐 Backend Files Modified

1. `api.py`
   - Added `MemberRequest` Pydantic model (line 102-107)
   - Created `POST /api/households/{id}/members` endpoint (lines 1571-1642)
   - Created `DELETE /api/admin/users/{id}` endpoint (lines 1644-1701)
   - Fixed dashboard budget percentage calculation (lines 839-856)

---

## 🧪 Testing Checklist

### Period Synchronization
- [x] Select Feb 2026 in Dashboard
- [ ] Navigate to View Expenses → Should show only Feb 2026 expenses
- [ ] Navigate to View Income → Should show only Feb 2026 income
- [ ] Navigate to View Allocations → Should show only Feb 2026 allocations

### Validation Disclaimers
- [ ] Select empty period (e.g., March 2026 with no data)
- [ ] Try Add Allocation → Should show "No Income" alert and close
- [ ] Add Income for March 2026
- [ ] Try Add Allocation → Should work now
- [ ] Try Add Expense → Should show "No Allocations" alert
- [ ] Add Allocation for March 2026
- [ ] Try Add Expense → Should work now

### Add Member
- [ ] Login as Family Admin
- [ ] Navigate to Add Member
- [ ] Fill in name, email, relationship
- [ ] Submit → Should succeed (no more 403 error)

### Delete User
- [ ] Login as Super Admin
- [ ] View household members
- [ ] Delete a member → Should succeed (no more 404 error)

### Dashboard Improvements
- [ ] Open Dashboard
- [ ] Savings status shows grade (Excellent/Good/Moderate/Low/Deficit)
- [ ] Budget Used card shows only percentage (no calculation text)
- [ ] Budget percentage displays correctly (not 0%)
- [ ] Period picker labels are clearly visible

---

## 🔄 Migration Notes

### From v6.3 to v6.4

**No database migrations required** - All changes are code-level enhancements.

**Mobile App:**
- Clear app cache and restart for best experience
- Period selection now persists across screen navigation

**Backend:**
- New endpoints are backward compatible
- Existing mobile apps will work but won't have new member management features

---

## 📊 Impact Summary

| Feature | Before | After | Impact |
|---------|--------|-------|--------|
| Savings Status | Static "Surplus/Deficit" | Dynamic grade (5 levels) | Better financial insight |
| Period Sync | Each screen independent | Global synchronized state | Consistent UX |
| Data Entry Flow | Allowed incomplete entries | Validates prerequisites | Data integrity |
| Budget % Display | Always showed 0% | Correctly calculated | Accurate tracking |
| Add Member | 403 Forbidden error | Working endpoint | Feature complete |
| Delete User | 404 Not Found error | Working endpoint | Feature complete |
| Dashboard UI | Cluttered, hard to read | Clean, readable | Better UX |

---

## 🐛 Known Issues

None reported in this version.

---

## 🔜 Future Enhancements

- Password reset flow for new members
- Email invite system (vs manual token sharing)
- Export monthly reports to PDF
- Push notifications for budget alerts
- Biometric authentication

---

## 📝 Upgrade Instructions

### Mobile App
```bash
cd C:\AntiGravity_Projects\PBTCV\BudgetTrackerMobile
git pull origin main
npm install  # if dependencies changed
npx expo start --clear
```

### Backend (Render Auto-deploys)
- Push to main branch → Render auto-deploys
- Check deployment logs for any issues

---

## 👥 Contributors

- AntiGravity AI Team

---

## 📄 License

Personal Use License - Commercial Version

---

**For support or issues, contact the development team or create an issue on GitHub.**
