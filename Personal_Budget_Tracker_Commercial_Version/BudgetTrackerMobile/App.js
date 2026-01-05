import React, { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import Screens
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import AddExpenseScreen from './src/screens/AddExpenseScreen';
import ExpensesListScreen from './src/screens/ExpensesListScreen';
import IncomeListScreen from './src/screens/IncomeListScreen';
import AddIncomeScreen from './src/screens/AddIncomeScreen';
import AllocationsListScreen from './src/screens/AllocationsListScreen';
import AddAllocationScreen from './src/screens/AddAllocationScreen';
import SuperAdminDashboard from './src/screens/SuperAdminDashboard';
import AddMemberScreen from './src/screens/AddMemberScreen';
import ViewFamilyMembersScreen from './src/screens/ViewFamilyMembersScreen';
import AddFamilyAdminScreen from './src/screens/AddFamilyAdminScreen';
import HouseholdDetailScreen from './src/screens/HouseholdDetailScreen';


const App = () => {
    const [currentScreen, setCurrentScreen] = useState('Login');
    const [user, setUser] = useState(null);
    const [screenParams, setScreenParams] = useState(null);

    // No auto-login - always start at login screen

    const handleLogin = (userData) => {
        setUser(userData);
        // Route to appropriate dashboard based on role
        if (userData.role === 'superadmin') {
            setCurrentScreen('SuperAdminDashboard');
        } else {
            setCurrentScreen('Dashboard');
        }
    };

    const handleLogout = async () => {
        // Clear all stored data
        await AsyncStorage.clear();
        setUser(null);
        setCurrentScreen('Login');
    };

    const handleNavigate = (screenName, params = null) => {
        setScreenParams(params);
        setCurrentScreen(screenName);
    };

    // Render current screen
    if (currentScreen === 'Login') {
        return <LoginScreen onLogin={handleLogin} />;
    }

    if (currentScreen === 'Dashboard') {
        return <DashboardScreen user={user} onLogout={handleLogout} onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'AddExpense') {
        return <AddExpenseScreen navigation={{ goBack: () => setCurrentScreen('Dashboard') }} />;
    }

    if (currentScreen === 'ExpensesList') {
        return <ExpensesListScreen onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'IncomeList') {
        return <IncomeListScreen onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'AddIncome') {
        return <AddIncomeScreen navigation={{ goBack: () => setCurrentScreen('Dashboard') }} />;
    }

    if (currentScreen === 'AllocationsList') {
        return <AllocationsListScreen onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'AddAllocation') {
        return <AddAllocationScreen navigation={{ goBack: () => setCurrentScreen('Dashboard') }} />;
    }

    if (currentScreen === 'SuperAdminDashboard') {
        return <SuperAdminDashboard onLogout={handleLogout} onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'AddMember') {
        return <AddMemberScreen onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'ViewFamilyMembers') {
        return <ViewFamilyMembersScreen onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'AddFamilyAdmin') {
        return <AddFamilyAdminScreen onNavigate={handleNavigate} />;
    }

    if (currentScreen === 'HouseholdDetail') {
        return <HouseholdDetailScreen route={{ params: screenParams }} onNavigate={handleNavigate} />;
    }

    return null;
};

export default App;

