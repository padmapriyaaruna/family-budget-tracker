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
import { getAllocations, deleteAllocation } from '../services/api';
import { COLORS } from '../config';
import { formatCurrency, getCurrentPeriod } from '../utils/helpers';

const AllocationsListScreen = ({ onNavigate }) => {
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

    const handleDelete = (allocationId) => {
        Alert.alert(
            'Delete Allocation',
            'Are you sure?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await deleteAllocation(allocationId);
                            Alert.alert('Success', 'Allocation deleted');
                            loadAllocations();
                        } catch (error) {
                            Alert.alert('Error', 'Failed to delete');
                        }
                    },
                },
            ]
        );
    };

    const renderAllocation = ({ item }) => {
        const allocatedAmount = item['Allocated Amount'] || item.allocated_amount || 0;
        const spentAmount = item['Spent Amount'] || item.spent_amount || 0;
        const balance = allocatedAmount - spentAmount;

        const percentUsed = allocatedAmount > 0
            ? (spentAmount / allocatedAmount * 100).toFixed(1)
            : 0;

        return (
            <View style={styles.allocationCard}>
                <Text style={styles.category}>{item.Category || item.category}</Text>
                <View style={styles.amountRow}>
                    <View>
                        <Text style={styles.label}>Allocated</Text>
                        <Text style={styles.allocated}>{formatCurrency(allocatedAmount)}</Text>
                    </View>
                    <View>
                        <Text style={styles.label}>Spent</Text>
                        <Text style={styles.spent}>{formatCurrency(spentAmount)}</Text>
                    </View>
                    <View>
                        <Text style={styles.label}>Balance</Text>
                        <Text style={[styles.balance, balance < 0 && styles.negative]}>
                            {formatCurrency(balance)}
                        </Text>
                    </View>
                </View>
                <View style={styles.progressBar}>
                    <View style={[styles.progress, { width: `${Math.min(percentUsed, 100)}%` }]} />
                </View>
                <Text style={styles.percent}>{percentUsed}% used</Text>
                <View style={styles.actions}>
                    <TouchableOpacity
                        style={styles.deleteBtn}
                        onPress={() => handleDelete(item.id)}>
                        <Text style={styles.deleteBtnText}>Delete</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => onNavigate('Dashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Budget Allocations</Text>
                <TouchableOpacity onPress={() => onNavigate('AddAllocation')}>
                    <Text style={styles.addButton}>+ Add</Text>
                </TouchableOpacity>
            </View>
            <FlatList
                data={allocations}
                renderItem={renderAllocation}
                keyExtractor={(item, index) => item.id?.toString() || index.toString()}
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

export default AllocationsListScreen;
