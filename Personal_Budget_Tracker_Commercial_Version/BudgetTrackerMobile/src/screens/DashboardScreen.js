import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    RefreshControl,
} from 'react-native';
import { getDashboard } from '../services/api';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';
import { COLORS } from '../config';

const DashboardScreen = ({ user, onLogout, onNavigate }) => {
    const [dashboard, setDashboard] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const period = getCurrentPeriod();

    useEffect(() => {
        fetchDashboard();
    }, []);

    const fetchDashboard = async () => {
        try {
            const data = await getDashboard(user.id, period.year, period.month);
            setDashboard(data);
        } catch (error) {
            console.error('Error fetching dashboard:', error);
        } finally {
            setRefreshing(false);
        }
    };

    if (!dashboard) {
        return (
            <View style={styles.container}>
                <Text>Loading...</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={fetchDashboard} />
            }>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.welcomeText}>Welcome back,</Text>
                    <Text style={styles.userName}>{user.full_name}</Text>
                </View>
                <TouchableOpacity onPress={onLogout} style={styles.logoutButton}>
                    <Text style={styles.logoutText}>Logout</Text>
                </TouchableOpacity>
            </View>

            {/* Period */}
            <View style={styles.periodCard}>
                <Text style={styles.periodText}>
                    {period.month}/{period.year}
                </Text>
            </View>

            {/* Summary Cards */}
            <View style={styles.summaryGrid}>
                <View style={[styles.summaryCard, styles.incomeCard]}>
                    <Text style={styles.summaryLabel}>Total Income</Text>
                    <Text style={styles.summaryAmount}>
                        {formatCurrency(dashboard.income.total)}
                    </Text>
                </View>

                <View style={[styles.summaryCard, styles.expenseCard]}>
                    <Text style={styles.summaryLabel}>Total Spent</Text>
                    <Text style={styles.summaryAmount}>
                        {formatCurrency(dashboard.expenses.total)}
                    </Text>
                </View>

                <View style={[styles.summaryCard, styles.savingsCard]}>
                    <Text style={styles.summaryLabel}>Savings</Text>
                    <Text style={styles.summaryAmount}>
                        {formatCurrency(dashboard.savings)}
                    </Text>
                </View>

                <View style={[
                    styles.summaryCard,
                    dashboard.budget_used_percentage > 100 ? styles.budgetOverCard : styles.budgetUnderCard
                ]}>
                    <Text style={styles.summaryLabel}>Budget Used</Text>
                    <Text style={styles.summaryAmount}>
                        {dashboard.budget_used_percentage !== undefined
                            ? `${dashboard.budget_used_percentage}%`
                            : '0%'}
                    </Text>
                </View>
            </View>

            {/* Quick Actions */}
            <View style={styles.actionsSection}>
                <Text style={styles.sectionTitle}>Quick Actions</Text>
                <TouchableOpacity
                    style={[styles.actionButton, styles.addExpenseButton]}
                    onPress={() => onNavigate('AddExpense')}>
                    <Text style={styles.actionButtonText}>+ Add Expense</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.actionButton, styles.addIncomeButton]}
                    onPress={() => onNavigate('AddIncome')}>
                    <Text style={styles.actionButtonText}>+ Add Income</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.actionButton, styles.addAllocationButton]}
                    onPress={() => onNavigate('AddAllocation')}>
                    <Text style={styles.actionButtonText}>+ Add Allocation</Text>
                </TouchableOpacity>
            </View>

            {/* View Data Sections */}
            <View style={styles.actionsSection}>
                <Text style={styles.sectionTitle}>View Data</Text>
                <TouchableOpacity
                    style={[styles.actionButton, styles.viewButton]}
                    onPress={() => onNavigate('ExpensesList')}>
                    <Text style={styles.actionButtonText}>View All Expenses</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.actionButton, styles.viewButton]}
                    onPress={() => onNavigate('IncomeList')}>
                    <Text style={styles.actionButtonText}>View All Income</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.actionButton, styles.viewButton]}
                    onPress={() => onNavigate('AllocationsList')}>
                    <Text style={styles.actionButtonText}>View All Allocations</Text>
                </TouchableOpacity>
            </View>

            {/* Family Management (Admin Only) */}
            {user?.role === 'admin' && (
                <View style={styles.actionsSection}>
                    <Text style={styles.sectionTitle}>Family Management</Text>
                    <TouchableOpacity
                        style={[styles.actionButton, styles.manageButton]}
                        onPress={() => onNavigate('AddMember')}>
                        <Text style={styles.actionButtonText}>+ Add Family Member</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[styles.actionButton, styles.viewButton]}
                        onPress={() => onNavigate('ViewFamilyMembers')}>
                        <Text style={styles.actionButtonText}>View Family Members</Text>
                    </TouchableOpacity>
                </View>
            )}

            <View style={styles.footer}>
                <Text style={styles.footerText}>Pull down to refresh</Text>
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F5',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 20,
        backgroundColor: '#FFFFFF',
        marginTop: 40,
    },
    welcomeText: {
        fontSize: 16,
        color: '#757575',
    },
    userName: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#212121',
    },
    logoutButton: {
        padding: 8,
    },
    logoutText: {
        color: '#F44336',
        fontSize: 16,
    },
    periodCard: {
        backgroundColor: '#4CAF50',
        padding: 16,
        margin: 16,
        borderRadius: 8,
        alignItems: 'center',
    },
    periodText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
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
        backgroundColor: '#FFFFFF',
    },
    incomeCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#4CAF50',
    },
    expenseCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#F44336',
    },
    savingsCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#4CAF50',
    },
    budgetOverCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#F44336',
        backgroundColor: '#FFEBEE', // Light red background  
    },
    budgetUnderCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#4CAF50',
        backgroundColor: '#E8F5E9', // Light green background
    },
    summaryLabel: {
        fontSize: 14,
        color: '#757575',
        marginBottom: 8,
    },
    summaryAmount: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#212121',
    },
    actionsSection: {
        padding: 16,
        marginTop: 8,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#212121',
        marginBottom: 12,
    },
    actionButton: {
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 12,
    },
    addExpenseButton: {
        backgroundColor: COLORS.danger,
    },
    addIncomeButton: {
        backgroundColor: COLORS.success,
    },
    addAllocationButton: {
        backgroundColor: COLORS.secondary,
    },
    viewButton: {
        backgroundColor: COLORS.primary,
    },
    manageButton: {
        backgroundColor: '#FF9800', // Orange for management
    },
    actionButtonText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: 'bold',
    },
    footer: {
        padding: 20,
        alignItems: 'center',
    },
    footerText: {
        color: '#757575',
        fontSize: 14,
    },
});

export default DashboardScreen;
