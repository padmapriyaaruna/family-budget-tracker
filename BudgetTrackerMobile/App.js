import React, { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import Screens
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import AddExpenseScreen from './src/screens/AddExpenseScreen';

const App = () => {
    const [currentScreen, setCurrentScreen] = useState('Login');
    const [user, setUser] = useState(null);

    // Check if user is already logged in
    useEffect(() => {
        checkLoginStatus();
    }, []);

    const checkLoginStatus = async () => {
        try {
            const token = await AsyncStorage.getItem('authToken');
            const userData = await AsyncStorage.getItem('userData');
            if (token && userData) {
                setUser(JSON.parse(userData));
                setCurrentScreen('Dashboard');
            }
        } catch (error) {
            console.error('Error checking login status:', error);
        }
    };

    const handleLogin = (userData) => {
        setUser(userData);
        setCurrentScreen('Dashboard');
    };

    const handleLogout = async () => {
        await AsyncStorage.clear();
        setUser(null);
        setCurrentScreen('Login');
    };

    const handleNavigate = (screenName) => {
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

    return null;
};

export default App;

