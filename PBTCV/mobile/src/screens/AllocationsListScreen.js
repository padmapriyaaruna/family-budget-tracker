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
import { getAllocations } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const AllocationsListScreen = ({ navigation }) => {
    const [allocations, setAllocations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const period = getCurrentPeriod();

    useEffect(() => {
        loadAllocations();
    }, []);

    const loadAllocations = async () => {
        try {
            const userData = await AsyncStorage.getItem('userData');
            const user = JSON.parse(userData);
            const data = await getAllocations(user.id, period.year, period.month);
            setAllocations(data);
        } catch (error) {
            console.error('Error loading allocations:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const renderAllocation = ({ item }) => {
        const percentUsed = item.allocated_amount > 0
            ? (item.spent_amount / item.allocated_amount * 100).toFixed(1)
            : 0;

        return (
            <TouchableOpacity
                style={styles.allocationCard}
                onPress={() => navigation.navigate('AddAllocation', { allocation: item })}
            >
                <Text style={styles.category}>{item.category}</Text>
                <View style={styles.amountRow}>
                    <View>
                        <Text style={styles.label}>Allocated</Text>
                        <Text style={styles.allocated}>{formatCurrency(item.allocated_amount)}</Text>
                    </View>
                    <View>
                        <Text style={styles.label}>Spent</Text>
                        <Text style={styles.spent}>{formatCurrency(item.spent_amount)}</Text>
                    </View>
                    <View>
                        <Text style={styles.label}>Balance</Text>
                        <Text style={[styles.balance, item.balance < 0 && styles.negative]}>
                            {formatCurrency(item.balance)}
                        </Text>
                    </View>
                </View>
                <View style={styles.progressBar}>
                    <View style={[styles.progress, { width: `${Math.min(percentUsed, 100)}%` }]} />
                </View>
                <Text style={styles.percent}>{percentUsed}% used</Text>
            </TouchableOpacity>
        );
    };

    return (
        <View style={styles.container}>
            <FlatList
                data={allocations}
                renderItem={renderAllocation}
                keyExtractor={(item) => item.id.toString()}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={loadAllocations} />
                }
                ListEmptyComponent={
                    <Text style={styles.emptyText}>No allocations set yet</Text>
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
    allocationCard: {
        backgroundColor: COLORS.white,
        padding: 16,
        marginHorizontal: 16,
        marginVertical: 8,
        borderRadius: 8,
        borderLeftWidth: 4,
        borderLeftColor: COLORS.secondary,
    },
    category: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 12,
    },
    amountRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    label: {
        fontSize: 12,
        color: COLORS.textLight,
        marginBottom: 4,
    },
    allocated: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.secondary,
    },
    spent: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.warning,
    },
    balance: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.success,
    },
    negative: {
        color: COLORS.danger,
    },
    progressBar: {
        height: 8,
        backgroundColor: COLORS.lightGray,
        borderRadius: 4,
        overflow: 'hidden',
        marginBottom: 8,
    },
    progress: {
        height: '100%',
        backgroundColor: COLORS.secondary,
    },
    percent: {
        fontSize: 12,
        color: COLORS.textLight,
        textAlign: 'right',
    },
    emptyText: {
        textAlign: 'center',
        marginTop: 50,
        fontSize: 16,
        color: COLORS.textLight,
    },
});

export default AllocationsListScreen;
