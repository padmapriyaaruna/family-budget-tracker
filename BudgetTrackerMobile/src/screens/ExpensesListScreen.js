import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    StyleSheet,
    RefreshControl,
    Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getExpenses, deleteExpense } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const ExpensesListScreen = ({ onNavigate }) => {
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const period = getCurrentPeriod();

    useEffect(() => {
        loadExpenses();
    }, []);

    const loadExpenses = async () => {
        try {
            const userData = await AsyncStorage.getItem('userData');
            const user = JSON.parse(userData);
            const data = await getExpenses(user.id, period.year, period.month);
            setExpenses(data);
        } catch (error) {
            console.error('Error loading expenses:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleDelete = (expenseId) => {
        Alert.alert(
            'Delete Expense',
            'Are you sure?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await deleteExpense(expenseId);
                            Alert.alert('Success', 'Expense deleted');
                            loadExpenses();
                        } catch (error) {
                            Alert.alert('Error', 'Failed to delete');
                        }
                    },
                },
            ]
        );
    };

    const renderExpense = ({ item }) => (
        <View style={styles.expenseCard}>
            <View style={styles.expenseHeader}>
                <Text style={styles.category}>{item.Category || item.category}</Text>
                <Text style={styles.amount}>{formatCurrency(item.Amount || item.amount)}</Text>
            </View>
            <Text style={styles.subcategory}>{item.Subcategory || item.subcategory}</Text>
            <Text style={styles.date}>{item.Date || item.date}</Text>
            {(item.Comment || item.comment) && <Text style={styles.comment}>{item.Comment || item.comment}</Text>}
            <View style={styles.actions}>
                <TouchableOpacity
                    style={styles.deleteBtn}
                    onPress={() => handleDelete(item.id)}>
                    <Text style={styles.deleteBtnText}>Delete</Text>
                </TouchableOpacity>
            </View>
        </View>
    );

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => onNavigate('Dashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title}>My Expenses</Text>
                <TouchableOpacity onPress={() => onNavigate('AddExpense')}>
                    <Text style={styles.addButton}>+ Add</Text>
                </TouchableOpacity>
            </View>

            <FlatList
                data={expenses}
                renderItem={renderExpense}
                keyExtractor={(item, index) => item.id?.toString() || index.toString()}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={loadExpenses} />
                }
                ListEmptyComponent={
                    <Text style={styles.emptyText}>No expenses yet</Text>
                }
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        backgroundColor: COLORS.white,
        marginTop: 40,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.lightGray,
    },
    backButton: {
        fontSize: 16,
        color: COLORS.primary,
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    addButton: {
        fontSize: 16,
        color: COLORS.primary,
        fontWeight: '600',
    },
    expenseCard: {
        backgroundColor: COLORS.white,
        padding: 16,
        marginHorizontal: 16,
        marginVertical: 8,
        borderRadius: 8,
        borderLeftWidth: 4,
        borderLeftColor: COLORS.danger,
    },
    expenseHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    category: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    amount: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.danger,
    },
    subcategory: {
        fontSize: 14,
        color: COLORS.textLight,
        marginBottom: 4,
    },
    date: {
        fontSize: 12,
        color: COLORS.gray,
    },
    comment: {
        fontSize: 14,
        color: COLORS.text,
        marginTop: 8,
        fontStyle: 'italic',
    },
    actions: {
        marginTop: 12,
        flexDirection: 'row',
        justifyContent: 'flex-end',
    },
    deleteBtn: {
        backgroundColor: COLORS.danger,
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 4,
    },
    deleteBtnText: {
        color: COLORS.white,
        fontWeight: '600',
        fontSize: 14,
    },
    emptyText: {
        textAlign: 'center',
        marginTop: 50,
        fontSize: 16,
        color: COLORS.textLight,
    },
});

export default ExpensesListScreen;
