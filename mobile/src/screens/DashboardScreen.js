import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    RefreshControl,
    Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getDashboard } from '../services/api';
import { COLORS, CURRENCY_SYMBOL } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const DashboardScreen = ({ navigation, route }) => {
    const [user, setUser] = useState(null);
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [period, setPeriod] = useState(getCurrentPeriod());

    useEffect(() => {
        loadUserData();
    }, []);

    const loadUserData = async () => {
        try {
            const userData = await AsyncStorage.getItem('userData');
            if (userData) {
                const parsedUser = JSON.parse(userData);
                setUser(parsedUser);
                fetchDashboard(parsedUser.id);
            }
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    };

    const fetchDashboard = async (userId) => {
        try {
            const data = await getDashboard(userId, period.year, period.month);
            setDashboard(data);
        } catch (error) {
            console.error('Error fetching dashboard:', error);
            Alert.alert('Error', 'Failed to load dashboard data');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = useCallback(() => {
        setRefreshing(true);
        if (user) {
            fetchDashboard(user.id);
        }
    }, [user, period]);

    const handleLogout = async () => {
        Alert.alert(
            'Logout',
            'Are you sure you want to logout?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Logout',
                    style: 'destructive',
                    onPress: async () => {
                        await AsyncStorage.clear();
                        navigation.replace('Login');
                    },
                },
            ]
        );
    };

    if (loading || !user || !dashboard) {
        return (
            <View style={styles.loadingContainer}>
                <Text>Loading...</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.welcomeText}>Welcome back,</Text>
                    <Text style={styles.userName}>{user.full_name}</Text>
                </View>
                <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
                    <Text style={styles.logoutText}>Logout</Text>
                </TouchableOpacity>
            </View>

            {/* Period Display */}
            <View style={styles.periodCard}>
                <Text style={styles.periodText}>
                    {`${period.month}/${period.year}`}
                </Text>
            </View>

            {/* Summary Cards */}
            <View style={styles.summaryGrid}>
                {/* Income Card */}
                <View style={[styles.summaryCard, styles.incomeCard]}>
                    <Text style={styles.summaryLabel}>Total Income</Text>
                    <Text style={styles.summaryAmount}>
                        {formatCurrency(dashboard.income.total)}
                    </Text>
                    <Text style={styles.summaryCount}>
                        {dashboard.income.count} entries
                    </Text>
                </View>

                {/* Expenses Card */}
                <View style={[styles.summaryCard, styles.expenseCard]}>
                    <Text style={styles.summaryLabel}>Total Spent</Text>
                    <Text style={styles.summaryAmount}>
                        {formatCurrency(dashboard.expenses.total)}
                    </Text>
                    <Text style={styles.summaryCount}>
                        {dashboard.expenses.count} expenses
                    </Text>
                </View>

                {/* Savings Card */}
                <View style={[styles.summaryCard, styles.savingsCard]}>
                    <Text style={styles.summaryLabel}>Savings</Text>
                    <Text style={styles.summaryAmount}>
                        {formatCurrency(dashboard.savings)}
                    </Text>
                    <Text style={styles.summaryCount}>
                        {dashboard.savings >= 0 ? 'Surplus' : 'Deficit'}
                    </Text>
                </View>

                {/* Allocations Card */}
                <View style={[styles.summaryCard, styles.allocationCard]}>
                    <Text style={styles.summaryLabel}>Budget Used</Text>
                    <Text style={styles.summaryAmount}>
                        {dashboard.allocations.allocated > 0
                            ? `${((dashboard.allocations.spent / dashboard.allocations.allocated) * 100).toFixed(1)}%`
                            : '0%'}
                    </Text>
                    <Text style={styles.summaryCount}>
                        {formatCurrency(dashboard.allocations.spent)} / {formatCurrency(dashboard.allocations.allocated)}
                    </Text>
                </View>
            </View>

            {/* Action Buttons */}
            <View style={styles.actionsContainer}>
                <Text style={styles.sectionTitle}>Quick Actions</Text>

                <TouchableOpacity
                    style={[styles.actionButton, { backgroundColor: COLORS.primary }]}
                    onPress={() => navigation.navigate('IncomeList')}>
                    <Text style={styles.actionIcon}>💵</Text>
                    <Text style={styles.actionText}>Manage Income</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, { backgroundColor: COLORS.secondary }]}
                    onPress={() => navigation.navigate('AllocationsList')}>
                    <Text style={styles.actionIcon}>🎯</Text>
                    <Text style={styles.actionText}>Budget Allocations</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, { backgroundColor: COLORS.warning }]}
                    onPress={() => navigation.navigate('ExpensesList')}>
                    <Text style={styles.actionIcon}>💸</Text>
                    <Text style={styles.actionText}>View Expenses</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, { backgroundColor: COLORS.danger }]}
                    onPress={() => navigation.navigate('AddExpense')}>
                    <Text style={styles.actionIcon}>➕</Text>
                    <Text style={styles.actionText}>Add New Expense</Text>
                </TouchableOpacity>
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 20,
        backgroundColor: COLORS.white,
    },
    welcomeText: {
        fontSize: 16,
        color: COLORS.textLight,
    },
    userName: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    logoutButton: {
        padding: 8,
    },
    logoutText: {
        color: COLORS.danger,
        fontSize: 16,
    },
    periodCard: {
        backgroundColor: COLORS.primary,
        padding: 16,
        margin: 16,
        borderRadius: 8,
        alignItems: 'center',
    },
    periodText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.white,
    },
    summaryGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        padding: 8,
    },
    summaryCard: {
        width: '48%',
        margin: '1%',
        padding: 16,
        borderRadius: 8,
        backgroundColor: COLORS.white,
    },
    incomeCard: {
        borderLeftWidth: 4,
        borderLeftColor: COLORS.primary,
    },
    expenseCard: {
        borderLeftWidth: 4,
        borderLeftColor: COLORS.danger,
    },
    savingsCard: {
        borderLeftWidth: 4,
        borderLeftColor: COLORS.success,
    },
    allocationCard: {
        borderLeftWidth: 4,
        borderLeftColor: COLORS.secondary,
    },
    summaryLabel: {
        fontSize: 14,
        color: COLORS.textLight,
        marginBottom: 8,
    },
    summaryAmount: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    summaryCount: {
        fontSize: 12,
        color: COLORS.textLight,
    },
    actionsContainer: {
        padding: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 16,
    },
    actionButton: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        borderRadius: 8,
        marginBottom: 12,
    },
    actionIcon: {
        fontSize: 24,
        marginRight: 16,
    },
    actionText: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.white,
        flex: 1,
    },
});

export default DashboardScreen;
