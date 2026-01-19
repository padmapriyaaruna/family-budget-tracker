# Mobile Application Screens - Part 3: List Screens & Data Management

## AllocationsListScreen.js ✨ (v6.1 - Includes Edit Button)

**Location:** `BudgetTrackerMobile/src/screens/AllocationsListScreen.js`  
**Lines:** 288  
**Purpose:** Display all budget allocations with edit and delete options  

### Key Features (v6.1)
- ✅ Shows all allocations for current month
- ✅ **Edit button** (new in v6.1)
- ✅ Delete button with confirmation
- ✅ Pull-to-refresh
- ✅ Progress bars showing usage
- ✅ Color-coded balances

### Component Structure

```javascript
const AllocationsListScreen = ({ onNavigate, screenKey }) => {
    const [allocations, setAllocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const period = getCurrentPeriod();
```

### Data Loading with Auto-Refresh

```javascript
// Load on mount
useEffect(() => {
    loadAllocations();
}, []);

// Reload when screen becomes active ✨
useEffect(() => {
    if (screenKey !== undefined) {
        loadAllocations();
    }
}, [screenKey]);
```

**Why Two useEffects?**
1. First: Runs once when component mounts
2. Second: Runs whenever `screenKey` changes (when returning from edit screen)

### Render Allocation Card

```javascript
const renderAllocation = ({ item }) => {
    const allocatedAmount = item['Allocated Amount'] || item.allocated_amount || 0;
    const spentAmount = item['Spent Amount'] || item.spent_amount || 0;
    const balance = allocatedAmount - spentAmount;
    const allocationId = item.index || item.id;
    const percentUsed = Math.round((spentAmount / allocatedAmount) * 100);
    
    return (
        <View style={styles.allocationCard}>
            <Text style={styles.category}>{item.Category}</Text>
            
            {/* Amounts Display */}
            <View style={styles.amountsRow}>
                <View>
                    <Text>Allocated</Text>
                    <Text>{formatCurrency(allocatedAmount)}</Text>
                </View>
                <View>
                    <Text>Spent</Text>
                    <Text>{formatCurrency(spentAmount)}</Text>
                </View>
                <View>
                    <Text>Balance</Text>
                    <Text style={balance < 0 && styles.negative}>
                        {formatCurrency(balance)}
                    </Text>
                </View>
            </View>
            
            {/* Progress Bar */}
            <View style={styles.progressBar}>
                <View style={{width: `${Math.min(percentUsed, 100)}%`}} />
            </View>
            
            {/* Action Buttons ✨ v6.1 */}
            <View style={styles.actions}>
                <TouchableOpacity 
                    onPress={() => handleEdit(item)}
                    style={styles.editButton}
                >
                    <Text>✏️ Edit</Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                    onPress={() => handleDelete(allocationId)}
                    style={styles.deleteButton}
                >
                    <Text>🗑️ Delete</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
};
```

### Edit Handler ✨ (New in v6.1)

```javascript
const handleEdit = (item) => {
    onNavigate('AddAllocation', {
        allocation: item,
        onSuccess: loadAllocations
    });
};
```

**What This Does:**
1. Navigates to AddAllocationScreen
2. Passes allocation data
3. Passes callback to refresh list after save

---

## AddExpenseScreen.js

**Location:** `BudgetTrackerMobile/src/screens/AddExpenseScreen.js`  
**Lines:** 280  
**Purpose:** Record new expenses  

### Form Fields
```javascript
const [date, setDate] = useState(new Date());
const [category, setCategory] = useState('');
const [subcategory, setSubcategory] = useState('');
const [amount, setAmount] = useState('');
const [comment, setComment] = useState('');
```

### Category Dropdown

```javascript
// Load categories from user's allocations
useEffect(() => {
    loadCategories();
}, []);

const loadCategories = async () => {
    const user = await AsyncStorage.getItem('userData');
    const allocations = await getAllocations(user.id, year, month);
    const cats = allocations.data.map(a => a.Category || a.category);
    setCategories(cats);
};
```

### Subcategory Options

```javascript
const subcategoryOptions = [
    'Investment',
    'Food - Online',
    'Food - Hotel',
    'Grocery - Online',
    'Grocery - Offline',
    'School Fee',
    'Extra-Curricular',
    'Co-Curricular',
    'House Rent',
    'Maintenance',
    'Vehicle',
    'Gadgets',
    'Others'
];
```

### Save Handler

```javascript
const handleSave = async () => {
    // Validation
    if (!category || !amount || amount <= 0) {
        Alert.alert('Error', 'Fill all required fields');
        return;
    }
    
    // Subcategory validation
    if (subcategory === 'Others' && !comment.trim()) {
        Alert.alert('Error', 'Comment required for Others');
        return;
    }
    
    // Save expense
    await addExpense({
        user_id: userId,
        date: date.toISOString().split('T')[0],
        category,
        subcategory,
        amount: parseFloat(amount),
        comment
    });
    
    Alert.alert('Success', 'Expense added', [
        { text: 'OK', onPress: () => navigation.goBack() }
    ]);
};
```

---

## AddIncomeScreen.js

**Location:** `BudgetTrackerMobile/src/screens/AddIncomeScreen.js`  
**Lines:** 155  
**Purpose:** Record income  

### Simple Structure
```javascript
const [date, setDate] = useState(new Date());
const [source, setSource] = useState('');
const [amount, setAmount] = useState('');

const handleSave = async () => {
    await addIncome({
        user_id: userId,
        date: date.toISOString().split('T')[0],
        source,
        amount: parseFloat(amount)
    });
    
    navigation.goBack();
};
```

---

## ExpensesListScreen.js

**Location:** `BudgetTrackerMobile/src/screens/ExpensesListScreen.js`  
**Lines:** 302  
**Purpose:** Show all expenses  

### Features
- Displays expenses in reverse chronological order
- Shows date, category, subcategory, amount
- Edit and delete options
- Pull-to-refresh
- Filtering by date range

### Render Expense

```javascript
const renderExpense = ({ item }) => (
    <View style={styles.expenseCard}>
        <View style={styles.expenseHeader}>
            <Text style={styles.date}>
                {formatDate(item.date)}
            </Text>
            <Text style={styles.amount}>
                {formatCurrency(item.amount)}
            </Text>
        </View>
        
        <Text style={styles.category}>
            {item.category}
        </Text>
        
        {item.subcategory && (
            <Text style={styles.subcategory}>
                {item.subcategory}
            </Text>
        )}
        
        {item.comment && (
            <Text style={styles.comment}>
                {item.comment}
            </Text>
        )}
        
        <View style={styles.actions}>
            <TouchableOpacity onPress={() => handleEdit(item)}>
                <Text>✏️ Edit</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => handleDelete(item.id)}>
                <Text>🗑️ Delete</Text>
            </TouchableOpacity>
        </View>
    </View>
);
```

---

## IncomeListScreen.js

**Location:** `BudgetTrackerMobile/src/screens/IncomeListScreen.js`  
**Lines:** 143  
**Purpose:** Show all income records  

### Simple List View
```javascript
const renderIncome = ({ item }) => (
    <View style={styles.incomeCard}>
        <Text style={styles.date}>{formatDate(item.date)}</Text>
        <Text style={styles.source}>{item.source}</Text>
        <Text style={styles.amount}>{formatCurrency(item.amount)}</Text>
        <View style={styles.actions}>
            <TouchableOpacity onPress={() => handleEdit(item)}>
                <Text>✏️</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => handleDelete(item.id)}>
                <Text>🗑️</Text>
            </TouchableOpacity>
        </View>
    </View>
);
```

---

## API Service Functions (api.js)

**Location:** `BudgetTrackerMobile/src/services/api.js`  
**Lines:** 273  
**Purpose:** All backend communication  

### Configuration

```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../config';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
});
```

### Request Interceptor (Auto-attach Token)

```javascript
apiClient.interceptors.request.use(
    async (config) => {
        const token = await AsyncStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);
```

**What This Does:**
- Runs before every API request
- Gets saved token from storage
- Adds to Authorization header
- Backend validates token

### Authentication Functions

```javascript
export const login = async (credentials) => {
    const response = await apiClient.post('/api/auth/login', credentials);
    return response.data;
};
```

### Income Functions

```javascript
export const getIncome = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;
    
    const response = await apiClient.get(`/api/income/${userId}`, { params });
    return response.data;
};

export const addIncome = async (data) => {
    const response = await apiClient.post('/api/income', data);
    return response.data;
};

export const updateIncome = async (id, data) => {
    const response = await apiClient.put(`/api/income/${id}`, data);
    return response.data;
};

export const deleteIncome = async (id) => {
    const response = await apiClient.delete(`/api/income/${id}`);
    return response.data;
};
```

### Allocation Functions ✨ (v6.1 Updated)

```javascript
export const getAllocations = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;
    
    const response = await apiClient.get(`/api/allocations/${userId}`, { params });
    return response.data; // Returns: {status: "success", data: [...]}
};

export const addAllocation = async (data) => {
    const response = await apiClient.post('/api/allocations', data);
    return response.data;
};

// ✨ v6.1: Fixed to include all required fields
export const updateAllocation = async (id, data) => {
    const response = await apiClient.put(`/api/allocations/${id}`, data);
    return response.data;
};

export const deleteAllocation = async (id) => {
    const response = await apiClient.delete(`/api/allocations/${id}`);
    return response.data;
};
```

### Expense Functions

```javascript
export const getExpenses = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;
    
    const response = await apiClient.get(`/api/expenses/${userId}`, { params });
    return response.data;
};

export const addExpense = async (data) => {
    const response = await apiClient.post('/api/expenses', data);
    return response.data;
};

export const updateExpense = async (id, data) => {
    const response = await apiClient.put(`/api/expenses/${id}`, data);
    return response.data;
};

export const deleteExpense = async (id) => {
    const response = await apiClient.delete(`/api/expenses/${id}`);
    return response.data;
};
```

### Dashboard Function

```javascript
export const getDashboard = async (userId, year, month) => {
    const response = await apiClient.get(`/api/dashboard/${userId}`, {
        params: { year, month }
    });
    return response.data;
    // Returns:
    // {
    //     income: {total: X, count: Y},
    //     expenses: {total: X, count: Y},
    //     allocations: {allocated: X, spent: Y, balance: Z}
    // }
};
```

### Error Handling Pattern

```javascript
try {
    const response = await apiClient.get('/api/endpoint');
    return response.data;
} catch (error) {
    if (error.response) {
        // Server responded with error
        throw new Error(error.response.data.detail || 'Server error');
    } else if (error.request) {
        // Request made but no response
        throw new Error('Network error');
    } else {
        // Other error
        throw new Error('Request failed');
    }
}
```

---

## Summary of Mobile App

### Complete Screen List

1. ✅ LoginScreen - Authentication
2. ✅ DashboardScreen - Home
3. ✅ AddAllocationScreen - Add/Edit allocations (v6.1)
4. ✅ AllocationsListScreen - View allocations (v6.1)
5. ✅ AddExpenseScreen - Add expense
6. ✅ ExpensesListScreen - View expenses
7. ✅ AddIncomeScreen - Add income
8. ✅ IncomeListScreen - View income
9. SavingsScreen - Liquidity tracking
10. SuperAdminDashboardScreen - Admin functions
11. ViewFamilyMembersScreen - Member management
12. AddMemberScreen - Add members
13. AddFamilyAdminScreen - Add family admin
14. HouseholdDetailScreen - Household info
15. SuperAdminDashboard - System overview

### Key Patterns

**State Management:**
```javascript
const [data, setData] = useState(initialValue);
```

**Data Loading:**
```javascript
useEffect(() => {
    loadData();
}, [dependency]);
```

**API Calls:**
```javascript
const response = await apiFunction(params);
```

**Navigation:**
```javascript
onNavigate('ScreenName', params);
```

**Error Handling:**
```javascript
try {
    // operation
} catch (error) {
    Alert.alert('Error', error.message);
}
```

---

*Mobile App Documentation Complete - Proceeding to Backend API...*
