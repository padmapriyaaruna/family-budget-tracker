import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { COLORS } from './src/config';

// Import Screens
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import AddExpenseScreen from './src/screens/AddExpenseScreen';
import ExpensesListScreen from './src/screens/ExpensesListScreen';
import IncomeListScreen from './src/screens/IncomeListScreen';
import AllocationsListScreen from './src/screens/AllocationsListScreen';
import AddIncomeScreen from './src/screens/AddIncomeScreen';
import AddAllocationScreen from './src/screens/AddAllocationScreen';

const Stack = createStackNavigator();

const App = () => {
    return (
        <NavigationContainer>
            <Stack.Navigator
                initialRouteName="Login"
                screenOptions={{
                    headerStyle: {
                        backgroundColor: COLORS.primary,
                    },
                    headerTintColor: COLORS.white,
                    headerTitleStyle: {
                        fontWeight: 'bold',
                    },
                }}>
                {/* Auth */}
                <Stack.Screen
                    name="Login"
                    component={LoginScreen}
                    options={{ headerShown: false }}
                />

                {/* Main */}
                <Stack.Screen
                    name="Dashboard"
                    component={DashboardScreen}
                    options={{ title: 'Dashboard', headerLeft: null }}
                />

                {/* Expenses */}
                <Stack.Screen
                    name="ExpensesList"
                    component={ExpensesListScreen}
                    options={{ title: 'My Expenses' }}
                />
                <Stack.Screen
                    name="AddExpense"
                    component={AddExpenseScreen}
                    options={{ title: 'Add Expense' }}
                />

                {/* Income */}
                <Stack.Screen
                    name="IncomeList"
                    component={IncomeListScreen}
                    options={{ title: 'My Income' }}
                />
                <Stack.Screen
                    name="AddIncome"
                    component={AddIncomeScreen}
                    options={{ title: 'Add Income' }}
                />

                {/* Allocations */}
                <Stack.Screen
                    name="AllocationsList"
                    component={AllocationsListScreen}
                    options={{ title: 'Budget Allocations' }}
                />
                <Stack.Screen
                    name="AddAllocation"
                    component={AddAllocationScreen}
                    options={{ title: 'Add Allocation' }}
                />
            </Stack.Navigator>
        </NavigationContainer>
    );
};

export default App;
