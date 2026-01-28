import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    StyleSheet,
    RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getExpenses } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const ExpensesListScreen = ({ navigation }) => {
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

    const renderExpense = ({ item }) => (
        <View style={styles.expenseCard}>
            <View style={styles.expenseHeader}>
                <Text style={styles.category}>{item.category}</Text>
                <Text style={styles.amount}>{formatCurrency(item.amount)}</Text>
            </View>
            <Text style={styles.subcategory}>{item.subcategory}</Text>
            {item.payment_mode && (
                <Text style={styles.paymentInfo}>
                    💳 {item.payment_mode}
                    {item.payment_details && ` - ${item.payment_details}`}
                </Text>
            )}
            <Text style={styles.date}>{item.date}</Text>
            {item.comment && <Text style={styles.comment}>{item.comment}</Text>}
        </View>
    );

    return (
        <View style={styles.container}>
            <FlatList
                data={expenses}
                renderItem={renderExpense}
                keyExtractor={(item) => item.id.toString()}
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
    paymentInfo: {
        fontSize: 13,
        color: COLORS.secondary,
        marginBottom: 4,
        fontWeight: '500',
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
    emptyText: {
        textAlign: 'center',
        marginTop: 50,
        fontSize: 16,
        color: COLORS.textLight,
    },
});

export default ExpensesListScreen;
