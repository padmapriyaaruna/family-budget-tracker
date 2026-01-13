import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getIncome } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const IncomeListScreen = ({ navigation }) => {
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
            const data = await getIncome(user.id, period.year, period.month);
            setIncome(data);
        } catch (error) {
            console.error('Error loading income:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const renderIncome = ({ item }) => (
        <View style={styles.incomeCard}>
            <View style={styles.incomeHeader}>
                <Text style={styles.source}>{item.source}</Text>
                <Text style={styles.amount}>{formatCurrency(item.amount)}</Text>
            </View>
            <Text style={styles.date}>{item.date}</Text>
        </View>
    );

    return (
        <View style={styles.container}>
            <FlatList
                data={income}
                renderItem={renderIncome}
                keyExtractor={(item) => item.id.toString()}
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
    emptyText: {
        textAlign: 'center',
        marginTop: 50,
        fontSize: 16,
        color: COLORS.textLight,
    },
});

export default IncomeListScreen;
