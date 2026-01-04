import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    StyleSheet,
    RefreshControl,
    Alert,
    ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getExpenses, deleteExpense } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';
import EditExpenseModal from '../components/EditExpenseModal';

const ExpensesListScreen = ({ onNavigate }) => {
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [selectedExpense, setSelectedExpense] = useState(null);
    const [expandedCategories, setExpandedCategories] = useState({});
    const period = getCurrentPeriod();

    useEffect(() => {
        loadExpenses();
    }, []);

    const loadExpenses = async () => {
        try {
            const userData = await AsyncStorage.getItem('userData');
            const user = JSON.parse(userData);
            // Get all expenses (no period filter)
            const data = await getExpenses(user.id);
            setExpenses(data);
        } catch (error) {
            console.error('Error loading expenses:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    // Group expenses by category
    const groupedExpenses = expenses.reduce((acc, expense) => {
        const category = expense.Category || expense.category || 'Uncategorized';
        if (!acc[category]) {
            acc[category] = [];
        }
        acc[category].push(expense);
        return acc;
    }, {});

    const toggleCategory = (category) => {
        setExpandedCategories(prev => ({
            ...prev,
            [category]: !prev[category]
        }));
    };

    const handleEdit = (expense) => {
        setSelectedExpense(expense);
        setEditModalVisible(true);
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

            <ScrollView
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={loadExpenses} />
                }>
                {Object.keys(groupedExpenses).length === 0 ? (
                    <Text style={styles.emptyText}>No expenses yet</Text>
                ) : (
                    Object.entries(groupedExpenses).map(([category, categoryExpenses]) => {
                        const total = categoryExpenses.reduce((sum, exp) =>
                            sum + (exp.Amount || exp.amount || 0), 0);
                        const isExpanded = expandedCategories[category];

                        return (
                            <View key={category} style={styles.categorySection}>
                                {/* Category Header */}
                                <TouchableOpacity
                                    style={styles.categoryHeader}
                                    onPress={() => toggleCategory(category)}>
                                    <View style={styles.categoryHeaderLeft}>
                                        <Text style={styles.categoryName}>{category}</Text>
                                        <Text style={styles.categoryCount}>
                                            ({categoryExpenses.length})
                                        </Text>
                                    </View>
                                    <Text style={styles.categoryTotal}>
                                        {formatCurrency(total)}
                                    </Text>
                                    <Text style={styles.categoryArrow}>
                                        {isExpanded ? '▼' : '▶'}
                                    </Text>
                                </TouchableOpacity>

                                {/* Expanded Expenses */}
                                {isExpanded && categoryExpenses.map((item) => (
                                    <View key={item.id} style={styles.expenseCard}>
                                        <View style={styles.expenseHeader}>
                                            <Text style={styles.subcategory}>
                                                {item.Subcategory || item.subcategory}
                                            </Text>
                                            <Text style={styles.amount}>
                                                {formatCurrency(item.Amount || item.amount)}
                                            </Text>
                                        </View>
                                        <Text style={styles.date}>{item.Date || item.date}</Text>
                                        {(item.Comment || item.comment) && (
                                            <Text style={styles.comment}>
                                                {item.Comment || item.comment}
                                            </Text>
                                        )}
                                        <View style={styles.actions}>
                                            <TouchableOpacity
                                                style={styles.editBtn}
                                                onPress={() => handleEdit(item)}>
                                                <Text style={styles.editBtnText}>Edit</Text>
                                            </TouchableOpacity>
                                            <TouchableOpacity
                                                style={styles.deleteBtn}
                                                onPress={() => handleDelete(item.id)}>
                                                <Text style={styles.deleteBtnText}>Delete</Text>
                                            </TouchableOpacity>
                                        </View>
                                    </View>
                                ))}
                            </View>
                        );
                    })
                )}
            </ScrollView>

            <EditExpenseModal
                visible={editModalVisible}
                expense={selectedExpense}
                onClose={() => setEditModalVisible(false)}
                onSave={() => {
                    setEditModalVisible(false);
                    loadExpenses();
                }}
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
    categorySection: {
        marginBottom: 12,
        marginHorizontal: 12,
    },
    categoryHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: COLORS.white,
        padding: 16,
        borderRadius: 10,
        elevation: 4, // Android shadow
        shadowColor: '#000', // iOS shadow
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
        borderLeftWidth: 5,
        borderLeftColor: COLORS.primary,
    },
    categoryHeaderLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    categoryName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        flex: 1,
    },
    categoryCount: {
        fontSize: 14,
        color: COLORS.textLight,
        fontStyle: 'italic',
        marginRight: 12,
    },
    categoryTotal: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginRight: 8,
    },
    categoryArrow: {
        fontSize: 18,
        color: COLORS.primary,
        fontWeight: 'bold',
        width: 24,
        textAlign: 'center',
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
        gap: 8,
    },
    editBtn: {
        backgroundColor: COLORS.secondary,
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 4,
        marginRight: 8,
    },
    editBtnText: {
        color: COLORS.white,
        fontWeight: '600',
        fontSize: 14,
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
