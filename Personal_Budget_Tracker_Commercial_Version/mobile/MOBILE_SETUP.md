# Family Budget Tracker - Mobile App Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Update API URL

Edit `src/config.js` and replace with your API URL:

```javascript
export const API_BASE_URL = 'https://your-api.onrender.com';
```

### 3. Run the App

```bash
# Start Expo
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios
```

## Features Implemented

### ✅ Screens Created

1. **LoginScreen** - Email/password authentication
2. **DashboardScreen** - Summary cards, quick actions  
3. **AddExpenseScreen** - Add new expenses with categories
4. **ExpensesListScreen** - View/edit/delete expenses
5. **IncomeListScreen** - Manage income entries
6. **AddIncomeScreen** - Add new income
7. **AllocationsListScreen** - Budget allocations
8. **AddAllocationScreen** - Create allocations

### ✅ All Web Features Included

- ✅ Income management (CRUD)
- ✅ Budget allocations (CRUD + copy previous month)
- ✅ Expense tracking with subcategories
- ✅ Dashboard with income vs expenses
- ✅ Period selection (year/month)
- ✅ Real-time calculations
- ✅ Logout functionality

## Project Structure

```
mobile/
├── App.js                          # Navigation setup
├── src/
│   ├── config.js                   # API URL & constants
│   ├── services/
│   │   └── api.js                  # All API calls
│   ├── screens/
│   │   ├── LoginScreen.js
│   │   ├── DashboardScreen.js
│   │   ├── AddExpenseScreen.js
│   │   ├── ExpensesListScreen.js
│   │   ├── IncomeListScreen.js
│   │   ├── AddIncomeScreen.js
│   │   ├── AllocationsListScreen.js
│   │   └── AddAllocationScreen.js
│   ├── components/
│   │   └── Loading.js
│   └── utils/
│       └── helpers.js              # Formatting functions
└── package.json
```

## Testing Checklist

- [ ] Test login wit valid credentials
- [ ] View dashboard summary
- [ ] Add new expense
- [ ] View expenses list
- [ ] Edit/delete expense
- [ ] Add income
- [ ] Create allocation
- [ ] Copy previous month allocations
- [ ] Logout and re-login

## Troubleshooting

### Cannot connect to API

- Check API URL in `src/config.js`
- Ensure API is deployed and running
- Test API health: `https://your-api.onrender.com/health`

### DateTimePicker not working

```bash
npx expo install @react-native-community/datetimepicker
```

### Picker not working

```bash
npx expo install @react-native-picker/picker
```

## Next Steps

1. Deploy API to Render
2. Update API_BASE_URL in config.js
3. Test all features
4. Build APK/IPA for distribution

## Notes

- Uses JWT token authentication
- All data syncs with web app (same database)
- Offline support can be added with AsyncStorage caching
- Push notifications can be added later

---

For full API documentation, see `API_DOCUMENTATION.md` in parent directory.
