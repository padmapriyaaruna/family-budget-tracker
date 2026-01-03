import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    RefreshControl,
    TouchableOpacity,
    Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getIncome, deleteIncome } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const IncomeListScreen = ({ onNavigate }) => {
    const [income, setIncome] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const period = getCurrentPeriod();

    useEffect(() => {
        loadIncome();
    }, []);

    const loadIncome = async () => {
        try {
            const userData = await AsyncStorage.getItem('userData');
            const user = JSON.parse(userData);
            // Get all income (no period filter)
            const data = await getIncome(user.id);
            setIncome(data);
        } catch (error) {
            console.error('Error loading income:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleDelete = (incomeId) => {
        Alert.alert(
            'Delete Income',
            'Are you sure?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await deleteIncome(incomeId);
                            Alert.alert('Success', 'Income deleted');
                            loadIncome();
                        } catch (error) {
                            Alert.alert('Error', 'Failed to delete');
                        }
                    },
                },
            ]
        );
    };

    const renderIncome = ({ item }) => (
        <View style={styles.incomeCard}>
            <View style={styles.incomeHeader}>
                <Text style={styles.source}>{item.Source || item.source}</Text>
                <Text style={styles.amount}>{formatCurrency(item.Amount || item.amount)}</Text>
            </View>
            <Text style={styles.date}>{item.Date || item.date}</Text>
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
            <View style={styles.header}>
                <TouchableOpacity onPress={() => onNavigate('Dashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title}>My Income</Text>
                <TouchableOpacity onPress={() => onNavigate('AddIncome')}>
                    <Text style={styles.addButton}>+ Add</Text>
                </TouchableOpacity>
            </View>
            <FlatList
                data={income}
                renderItem={renderIncome}
                keyExtractor={(item, index) => item.id?.toString() || index.toString()}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={loadIncome} />
                }
                ListEmptyComponent={
                    <Text style={styles.emptyText}>No income recorded yet</Text>
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
    incomeCard: {
        backgroundColor: COLORS.white,
        padding: 16,
        marginHorizontal: 16,
        marginVertical: 8,
        borderRadius: 8,
        borderLeftWidth: 4,
        borderLeftColor: COLORS.primary,
    },
    incomeHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    source: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    amount: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    date: {
        fontSize: 12,
        color: COLORS.gray,
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

export default IncomeListScreen;
