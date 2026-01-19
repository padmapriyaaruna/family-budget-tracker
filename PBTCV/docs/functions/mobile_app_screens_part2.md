# Mobile Application Screens - Detailed Documentation (Part 2)

## AddAllocationScreen.js - Add/Edit Budget Allocations

**Location:** `BudgetTrackerMobile/src/screens/AddAllocationScreen.js`  
**Lines:** 320  
**Purpose:** Add new or edit existing budget allocations  
**Complexity:** HIGH  
**Version:** v6.1 (includes edit functionality)

---

## Overview

This screen serves **TWO purposes:**

1. **Add Mode**: Create a new budget allocation
2. **Edit Mode** ✨ (New in v6.1): Modify existing allocation

**User Flow:**

**Add Mode:**
```
User: Dashboard → Tap "Add Allocation"
→ See empty form
→ Enter category and amount
→ Tap Save
→ Budget validation runs
→ Allocation saved
```

**Edit Mode:**
```
User: Allocations List → Tap "Edit" on a card
→ See pre-filled form
→ Modify amount
→ Tap Update
→ Budget validation (excluding current allocation)
→ Allocation updated
```

---

## Imports & Dependencies

```javascript
// Line 1-14
import React, { useState, useEffect } from 'react';
import {
    View, Text, TextInput, TouchableOpacity,
    StyleSheet, ScrollView, Alert
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { addAllocation, updateAllocation } from '../services/api';
import { COLORS } from '../config';
import { getCurrentPeriod } from '../utils/helpers';
```

**Key Imports:**

1. **React Native Components**
   - `Alert`: Show popup messages
   - `TextInput`: Form fields
   - `TouchableOpacity`: Buttons

2. **AsyncStorage**
   - Access saved user data
   - Get user ID

3. **API Functions**
   - `addAllocation`: POST new allocation
   - `updateAllocation`: PUT existing allocation ✨ v6.1

4. **Utilities**
   - `getCurrentPeriod()`: Get current year/month
   - `COLORS`: App color scheme

---

## Component Function & Props

```javascript
// Line 16
const AddAllocationScreen = ({ navigation, route }) => {
```

**Props Explained:**

1. **navigation**
   - React Navigation object
   - Methods: `goBack()`, `navigate()`
   - Passed automatically by navigator

2. **route**
   - Contains parameters passed from previous screen
   - `route.params.allocation` - Allocation data (for edit mode)
   - `route.params.onSuccess` - Callback after save

---

## State Variables

### Initial Setup

```javascript
// Line 17-29
const onSuccess = route?.params?.onSuccess;
const allocation = route?.params?.allocation;
const isEditMode = !!allocation;

const [userId, setUserId] = useState(null);
const [category, setCategory] = useState(
    allocation?.Category || allocation?.category || ''
);
const [amount, setAmount] = useState(
    allocation?.['Allocated Amount']?.toString() ||
    allocation?.allocated_amount?.toString() ||
    ''
);
const [loading, setLoading] = useState(false);
const period = getCurrentPeriod();
```

### Detailed Breakdown

**1. Route Parameters**
```javascript
const allocation = route?.params?.allocation;
```
- **In Add Mode**: undefined (no allocation passed)
- **In Edit Mode**: 
  ```javascript
  {
      index: 15,
      Category: "Rent",
      "Allocated Amount": 25000,
      "Spent Amount": 25000,
      Balance: 0
  }
  ```

**2. Edit Mode Detection**
```javascript
const isEditMode = !!allocation;
```
- **!!** Double negation trick
- Converts any value to boolean
- Examples:
  ```javascript
  !!undefined → false
  !!null → false
  !!{object} → true
  ```

**3. Category State**
```javascript
const [category, setCategory] = useState(
    allocation?.Category || allocation?.category || ''
);
```

**Why Two Field Names?**
```javascript
allocation?.Category        // API returns capitalized (from backend)
allocation?.category        // Lowercase field name
|| ''                      // Fallback to empty string
```

**Logic Flow:**
```
Edit Mode:
  allocation = {Category: "Rent"}
  → allocation?.Category = "Rent"
  → category initial value = "Rent" ✓
  → Form pre-filled!

Add Mode:
  allocation = undefined
  → allocation?.Category = undefined
  → allocation?.category = undefined  
  → '' (empty string)
  → category initial value = "" ✓
  → Form empty!
```

**4. Amount State**
```javascript
const [amount, setAmount] = useState(
    allocation?.['Allocated Amount']?.toString() ||
    allocation?.allocated_amount?.toString() ||
    ''
);
```

**Why** `.toString()`?
```javascript
// TextInput requires string value
amount = 25000           // Number - wrong! ❌
amount = "25000"         // String - correct! ✓

// Converting:
(25000).toString()       // "25000"
```

**Why Square Brackets?**
```javascript
allocation['Allocated Amount']     // Property with space
allocation.Allocated Amount        // Syntax error! ❌
```

---

## Data Loading

### useEffect Hook

```javascript
// Line 31-33
useEffect(() => {
    loadUserId();
}, []);
```

**Runs once when component mounts**
**Purpose:** Load user ID from storage

### loadUserId Function

```javascript
// Line 35-41
const loadUserId = async () => {
    const userData = await AsyncStorage.getItem('userData');
    if (userData) {
        const user = JSON.parse(userData);
        setUserId(user.id);
    }
};
```

**Step-by-Step:**

1. **Get Data from Storage**
   ```javascript
   const userData = await AsyncStorage.getItem('userData');
   ```
   - Key: 'userData'
   - Returns: String or null

2. **Check if Exists**
   ```javascript
   if (userData) {
   ```
   - If null: Do nothing
   - If string: Continue

3. **Parse JSON**
   ```javascript
   const user = JSON.parse(userData);
   ```
   - Converts string to object
   - Example:
     ```javascript
     userData = '{"id":28,"name":"Vinnodh"}'
     user = {id: 28, name: "Vinnodh"}
     ```

4. **Store ID**
   ```javascript
   setUserId(user.id);
   ```
   - Extracts ID
   - Now available for API calls

---

## Budget Validation Logic ✨ (v6.1 Key Feature)

### handleSave Function

**Location:** Line 44-129  
**Purpose:** Validate budget before saving  
**Complexity:** HIGH  

This is the **most important** function in this screen!

```javascript
const handleSave = async () => {
    // Step 1: Basic Validation
    if (!category || !amount || amount <= 0) {
        Alert.alert('Error', 'Please fill all required fields');
        return;
    }

    setLoading(true);
    try {
        // Step 2: Fetch Current Data
        const { getDashboard, getAllocations } = require('../services/api');
        const dashboardData = await getDashboard(userId, period.year, period.month);
        const allocationsData = await getAllocations(userId, period.year, period.month);

        // Step 3: Calculate Total Income
        const totalIncome = dashboardData.income?.total || 0;

        // Step 4: Calculate Currently Allocated
        const allocationsList = allocationsData.data || [];
        let currentAllocated = allocationsList.reduce(
            (sum, a) => sum + (a.allocated_amount || a['Allocated Amount'] || 0), 
            0
        );

        // Step 5: Adjust for Edit Mode ✨ v6.1 FIX
        if (isEditMode) {
            const currentAllocationAmount = 
                allocation?.['Allocated Amount'] || 
                allocation?.allocated_amount || 0;
            currentAllocated -= currentAllocationAmount;
        }

        // Step 6: Calculate Available Budget
        const availableBudget = totalIncome - currentAllocated;
        const newAmount = parseFloat(amount);

        // Step 7: Check if Over Budget
        if (newAmount > availableBudget) {
            // Show warning dialog
            Alert.alert(...);
            return;
        }

        // Step 8: Proceed if Within Budget
        await proceedWithAllocation();

    } catch (error) {
        console.error('Error checking budget:', error);
        await proceedWithAllocation();  // Fallback
    }
};
```

### Step-by-Step Analysis

**Step 1: Basic Validation**
```javascript
if (!category || !amount || amount <= 0) {
    Alert.alert('Error', 'Please fill all required fields');
    return;
}
```

**Checks:**
- `!category` - Is empty?
- `!amount` - Is empty?
- `amount <= 0` - Is zero or negative?

**If any fail:** Show error, stop execution

**Step 2: Fetch Current Data**
```javascript
const dashboardData = await getDashboard(userId, period.year, period.month);
const allocationsData = await getAllocations(userId, period.year, period.month);
```

**Two API calls in parallel would look like:**
```javascript
const [dashboardData, allocationsData] = await Promise.all([
    getDashboard(...),
    getAllocations(...)
]);
```
But here they run sequentially:
```javascript
Call 1: getDashboard → wait → got data
Call 2: getAllocations → wait → got data
Continue...
```

**What We Get:**

dashboardData:
```json
{
    "income": {"total": 140000, "count": 1},
    "expenses": {"total": 137558, "count": 34},
    "allocations": {"allocated": 115000, "spent": 112558, "balance": 2447}
}
```

allocationsData:
```json
{
    "status": "success",
    "data": [
        {"id": 15, "Category": "Rent", "Allocated Amount": 25000},
        {"id": 16, "Category": "Food", "Allocated Amount": 15000},
        ...
    ]
}
```

**Step 3: Get Total Income**
```javascript
const totalIncome = dashboardData.income?.total || 0;
```

Result: `totalIncome = 140000`

**Step 4: Calculate Total Allocated**
```javascript
const allocationsList = allocationsData.data || [];
let currentAllocated = allocationsList.reduce(
    (sum, a) => sum + (a.allocated_amount || a['Allocated Amount'] || 0), 
    0
);
```

**What is** `.reduce()`?

Think of it as a **running total**:

```javascript
allocationsList = [
    {Category: "Rent", "Allocated Amount": 25000},
    {Category: "Food", "Allocated Amount": 15000},
    {Category: "Transport", "Allocated Amount": 5000}
]

reduce works like:
sum = 0 (starting value)
1st item: sum = 0 + 25000 = 25000
2nd item: sum = 25000 + 15000 = 40000
3rd item: sum = 40000 + 5000 = 45000
Result: currentAllocated = 45000
```

**Step 5: Adjust for Edit Mode** ✨ **v6.1 Critical Fix**

```javascript
if (isEditMode) {
    const currentAllocationAmount = 
        allocation?.['Allocated Amount'] || 
        allocation?.allocated_amount || 0;
    currentAllocated -= currentAllocationAmount;
}
```

**Why This is Crucial:**

**Scenario:** Editing Rent from ₹25,000 to ₹25,001

**WITHOUT this fix (WRONG):**
```
Total Income: 140,000
All Allocations: 115,000 (includes Rent: 25,000)
Available: 140,000 - 115,000 = 25,000
New Amount: 25,001
Check: 25,001 > 25,000? YES
→ Shows warning ❌ (WRONG!)
```

**WITH this fix (CORRECT):**
```
Total Income: 140,000
All Allocations: 115,000
Current Rent: 25,000
Adjusted: 115,000 - 25,000 = 90,000
Available: 140,000 - 90,000 = 50,000
New Amount: 25,001
Check: 25,001 > 50,000? NO
→ No warning ✓ (CORRECT!)
```

**The Math:**
```javascript
currentAllocated = 115000
currentAllocationAmount = 25000
currentAllocated -= currentAllocationAmount
// currentAllocated = 115000 - 25000 = 90000
```

**Step 6: Calculate Available Budget**
```javascript
const availableBudget = totalIncome - currentAllocated;
const newAmount = parseFloat(amount);
```

**parseFloat()** converts string to number:
```javascript
amount = "25001"        // String from TextInput
parseFloat("25001")     // 25001 (number)
```

**Step 7: Over-Budget Check**
```javascript
if (newAmount > available Budget) {
    const overAmount = newAmount - availableBudget;
    
    Alert.alert(
        '⚠️ Budget Exceeded Warning',
        `You are trying to allocate ₹${newAmount.toLocaleString()} for "${category}".\n\n` +
        `• Available budget: ₹${availableBudget.toLocaleString()}\n` +
        `• Over-allocation: ₹${overAmount.toLocaleString()}\n\n` +
        `You may go into debt for this month. Do you want to proceed?`,
        [
            {
                text: 'Cancel',
                style: 'cancel',
                onPress: () => setLoading(false)
            },
            {
                text: 'OK, Proceed',
                onPress: () => proceedWithAllocation()
            }
        ]
    );
    return;
}
```

**Alert.alert Parameters:**

1. **Title**: '⚠️ Budget Exceeded Warning'
2. **Message**: Multi-line explanation
3. **Buttons**: Array of button objects

**Button Object:**
```javascript
{
    text: 'Cancel',          // Button label
    style: 'cancel',         // iOS button style
    onPress: () => {...}     // What happens when pressed
}
```

**User Interaction Flow:**
```
1. See warning
2. Read details
3. Choose:
   → Cancel: setLoading(false), stay on form
   → OK: proceedWithAllocation(), save anyway
```

---

## Save/Update Logic

### proceedWithAllocation Function

**Location:** Line 131-201  
**Purpose:** Actually save or update the allocation  

```javascript
const proceedWithAllocation = async () => {
    setLoading(true);
    try {
        if (isEditMode) {
            // UPDATE PATH
            const allocationId = allocation.index !== undefined 
                ? allocation.index 
                : (allocation.id || allocation.ID);
                
            await updateAllocation(allocationId, {
                user_id: userId,
                category,
                allocated_amount: parseFloat(amount),
                year: period.year,
                month: period.month,
            });
            
            Alert.alert('Success', 'Budget allocation updated successfully', [
                {
                    text: 'OK',
                    onPress: () => {
                        if (onSuccess) onSuccess();
                        navigation.goBack();
                    }
                },
            ]);
        } else {
            // ADD PATH
            await addAllocation({
                user_id: userId,
                category,
                allocated_amount: parseFloat(amount),
                year: period.year,
                month: period.month,
            });
            
            Alert.alert('Success', 'Budget allocation added successfully', [...]);
        }
    } catch (error) {
        console.error(`Error ${isEditMode ? 'updating' : 'adding'} allocation:`, error);
        
        let errorMessage = `Failed to ${isEditMode ? 'update' : 'add'} allocation`;
        if (error.response?.data?.detail) {
            errorMessage += `: ${error.response.data.detail}`;
        }
        
        Alert.alert('Error', errorMessage);
    } finally {
        setLoading(false);
    }
};
```

### Allocation ID Extraction

```javascript
const allocationId = allocation.index !== undefined 
    ? allocation.index 
    : (allocation.id || allocation.ID);
```

**Why so complex?**

Different API responses use different field names:
```javascript
// From get_allocations API:
{index: 15, Category: "Rent"}

// Or sometimes:
{id: 15, category: "Rent"}

// Or:
{ID: 15}
```

**Priority:**
1. `allocation.index` - Preferred
2. `allocation.id` - Fallback 1
3. `allocation.ID` - Fallback 2

### API Call - UPDATE

```javascript
await updateAllocation(allocationId, {
    user_id: userId,           // ✨ v6.1: Was missing!
    category,
    allocated_amount: parseFloat(amount),
    year: period.year,         // ✨ v6.1: Was missing!
    month: period.month,       // ✨ v6.1: Was missing!
});
```

**v6.1 Fixes:**

Before (BROKEN):
```javascript
await updateAllocation(allocationId, {
    category,
    allocated_amount: parseFloat(amount)
});
// Backend error: 422 Unprocessable Entity
// Missing required fields!
```

After (FIXED):
```javascript
await updateAllocation(allocationId, {
    user_id: userId,           // ✓ Added
    category,
    allocated_amount: parseFloat(amount),
    year: period.year,         // ✓ Added
    month: period.month,       // ✓ Added
});
// Success! ✓
```

### Success Flow

```javascript
Alert.alert('Success', 'Budget allocation updated successfully', [
    {
        text: 'OK',
        onPress: () => {
            if (onSuccess) onSuccess();
            navigation.goBack();
        }
    },
]);
```

**What Happens:**

1. **Show Success Alert**
   - Title: "Success"
   - Message: "Budget allocation updated successfully"
   - One button: "OK"

2. **User Taps OK**
   - `onPress` fires
   - Checks if `onSuccess` callback exists
   - If yes: Call it (refreshes previous screen)
   - `navigation.goBack()` - Returns to previous screen

**Complete User Journey:**

```
User: Edits Rent from 25000 to 25001
      ↓
Taps "Update Allocation"
      ↓
handleSave() runs
      ↓
Budget validation passes (no warning)
      ↓
proceedWithAllocation() runs
      ↓
API: PUT /api/allocations/15
     Body: {user_id: 28, category: "Rent", allocated_amount: 25001, year: 2026, month: 1}
      ↓
Backend: Validates, updates database
      ↓
Returns: {status: "success"}
      ↓
Mobile: Shows "Success" alert
      ↓
User: Taps "OK"
      ↓
onSuccess() called → Allocations list refreshes
      ↓
navigation.goBack() → Back to Allocations List
      ↓
User sees updated amount: ₹25,001 ✓
```

---

## Render Method

### Form UI

```javascript
return (
    <ScrollView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
            <TouchableOpacity onPress={() => navigation.goBack()}>
                <Text style={styles.backButton}>←</Text>
            </TouchableOpacity>
            <Text style={styles.headerTitle}>
                {isEditMode ? 'Update Allocation' : 'Add Allocation'}
            </Text>
        </View>

        {/* Form Card */}
        <View style={styles.card}>
            {/* Category Input */}
            <Text style={styles.label}>Category *</Text>
            <TextInput
                style={styles.input}
                placeholder="e.g., Rent, Food, Transport"
                value={category}
                onChangeText={setCategory}
            />

            {/* Amount Input */}
            <Text style={styles.label}>Allocated Amount *</Text>
            <TextInput
                style={styles.input}
                placeholder="0"
                value={amount}
                onChangeText={setAmount}
                keyboardType="numeric"
            />

            {/* Save Button */}
            <TouchableOpacity
                style={[styles.button, loading && styles.buttonDisabled]}
                onPress={handleSave}
                disabled={loading}
            >
                <Text style={styles.buttonText}>
                    {loading 
                        ? (isEditMode ? 'Updating...' : 'Saving...') 
                        : (isEditMode ? 'Update Allocation' : 'Add Allocation')
                    }
                </Text>
            </TouchableOpacity>
        </View>
    </ScrollView>
);
```

**Dynamic Elements:**

1. **Header Title**
   ```javascript
   {isEditMode ? 'Update Allocation' : 'Add Allocation'}
   ```
   - Edit: "Update Allocation"
   - Add: "Add Allocation"

2. **Button Text**
   ```javascript
   {loading 
       ? (isEditMode ? 'Updating...' : 'Saving...') 
       : (isEditMode ? 'Update Allocation' : 'Add Allocation')
   }
   ```
   **States:**
   - Edit + Loading: "Updating..."
   - Edit + Not Loading: "Update Allocation"
   - Add + Loading: "Saving..."
   - Add + Not Loading: "Add Allocation"

---

## Summary of v6.1 Changes

### What Was Fixed

1. **Budget Validation** ✅
   - Now excludes current allocation when editing
   - Prevents false "over-allocation" warnings

2. **API Parameters** ✅
   - Added `user_id`
   - Added `year`
   - Added `month`
   - Backend now accepts the request

3. **Error Handling** ✅
   - Better error messages
   - Shows actual API error details

4. **Pre-population** ✅
   - Form correctly fills with existing data
   - Handles different field name formats

### Before & After

**Before v6.1:**
```
User: Edit Rent from 25000 to 25001
→ Warning: "Over-allocation" ❌
→ If proceed: API Error 422 ❌
```

**After v6.1:**
```
User: Edit Rent from 25000 to 25001
→ No warning ✓
→ Update succeeds ✓
→ Data refreshes ✓
```

---

*Part 2 Complete - Continued in Part 3 with other data management screens...*
