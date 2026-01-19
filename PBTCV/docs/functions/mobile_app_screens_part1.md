# Mobile Application Screens - Detailed Documentation (Part 1)

**Directory:** `BudgetTrackerMobile/src/screens/`  
**Framework:** React Native  
**Language:** JavaScript  
**Total Screens:** 15

This document provides comprehensive, line-by-line documentation for mobile screens.

---

## Table of Contents - Part 1

1. [Mobile App Overview](#mobile-app-overview)
2. [Navigation & State Management](#navigation--state-management)
3. [Authentication Screens](#authentication-screens)
4. [Dashboard Screen](#dashboard-screen)

---

## Mobile App Overview

### Technology Stack

**Framework:** React Native  
**Purpose:** Cross-platform mobile app (Android & iOS)  
**Key Libraries:**
- `react-native` - Core framework
- `@react-native-async-storage/async-storage` - Local data storage
- `axios` - HTTP requests to backend API

### App Architecture

```
BudgetTrackerMobile/
├── src/
│   ├── screens/        ← All screen components (15 files)
│   ├── services/       ← API communication (api.js)
│   ├── components/     ← Reusable components
│   ├── config.js       ← Configuration constants
│   └── utils/          ← Helper functions
└── App.js             ← Main app controller & navigation
```

### State Management

**What is State?**
State is like the app's memory. It remembers:
- Is user logged in?
- Which screen to show?
- What data to display?

---

## Navigation & State Management

### App.js - The Main Controller

**Location:** `BudgetTrackerMobile/App.js`  
**Lines:** ~156  

#### Key Concepts

**App.js is like a TV Remote:**
- Controls which "channel" (screen) you see
- Stores what "volume" (settings) you have
- Remembers your "favorites" (user data)

#### State Variables

```javascript
const [currentScreen, setCurrentScreen] = useState('Login');
const [user, setUser] = useState(null);
const [screenParams, setScreenParams] = useState(null);
```

**Detailed Explanation:**

1. **currentScreen** - Which screen is displayed
   - Type: String
   - Values: 'Login', 'Dashboard', 'AddIncome', etc.
   
2. **user** - Logged user information
   - Type: Object or null
   - Contains: {id, email, full_name, role, household_id}
   - null = not logged in

3. **screenParams** - Data passed between screens
   - Type: Object or null
   - Example: Allocation data for editing

---

## Authentication Screens

### LoginScreen.js

**Location:** `BudgetTrackerMobile/src/screens/LoginScreen.js`  
**Lines:** ~390  

#### What This Screen Does

1. Shows 4 role selection buttons
2. User selects role
3. Shows login form
4. Validates input
5. Calls backend API
6. Navigates to dashboard

#### State Management

```javascript
const [loginType, setLoginType] = useState('landing');
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [loading, setLoading] = useState(false);
```

#### Login Handler

```javascript
const handleLogin = async () => {
    try {
        // 1. Validation
        if (!password) {
            Alert.alert('Error', 'Please enter password');
            return;
        }

        // 2. Set loading
        setLoading(true);

        // 3. Call API
        const response = await login(credentials);

        // 4. Save token
        await AsyncStorage.setItem('token', response.token);
        await AsyncStorage.setItem('user', JSON.stringify(response.user));

        // 5. Navigate
        onNavigate('Dashboard', response.user);

    } catch (error) {
        Alert.alert('Error', error.message);
    } finally {
        setLoading(false);
    }
};
```

---

## Dashboard Screen

### DashboardScreen.js

**Location:** `BudgetTrackerMobile/src/screens/DashboardScreen.js`  
**Lines:** ~320  

#### Components

1. Welcome header
2. Four summary cards
3. Quick action buttons
4. Navigation buttons

#### Data Loading

```javascript
useEffect(() => {
    loadDashboardData();
}, []);

const loadDashboardData = async () => {
    const user = await AsyncStorage.getItem('user');
    const data = await getDashboard(user.id, year, month);
    setDashboardData(data);
};
```

#### Summary Cards

Shows:
- Total Income: `₹{income.total}`
- Total Expenses: `₹{expenses.total}`
- Total Allocated: `₹{allocations.allocated}`
- Savings: `₹{income - expenses}`

---

*Continued in Part 2...*
