import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ScrollView,
    Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { addAllocation, updateAllocation } from '../services/api';
import { COLORS } from '../config';
import { getCurrentPeriod } from '../utils/helpers';

const AddAllocationScreen = ({ navigation, route }) => {
    const allocation = route.params?.allocation;
    const isEditMode = !!allocation;

    const [userId, setUserId] = useState(null);
    const [category, setCategory] = useState(allocation?.category || '');
    const [amount, setAmount] = useState(allocation?.allocated_amount?.toString() || '');
    const [loading, setLoading] = useState(false);
    const period = getCurrentPeriod();

    useEffect(() => {
        loadUserId();
    }, []);

    const loadUserId = async () => {
        const userData = await AsyncStorage.getItem('userData');
        if (userData) {
            const user = JSON.parse(userData);
            setUserId(user.id);
        }
    };

    const handleSave = async () => {
        if (!category || !amount || amount <= 0) {
            Alert.alert('Error', 'Please fill all required fields');
            return;
        }

        setLoading(true);
        try {
            if (isEditMode) {
                // Update existing allocation
                await updateAllocation(allocation.id, {
                    category,
                    allocated_amount: parseFloat(amount),
                });
                Alert.alert('Success', 'Budget allocation updated successfully', [
                    { text: 'OK', onPress: () => navigation.goBack() },
                ]);
            } else {
                // Add new allocation
                await addAllocation({
                    user_id: userId,
                    category,
                    allocated_amount: parseFloat(amount),
                    year: period.year,
                    month: period.month,
                });
                Alert.alert('Success', 'Budget allocation added successfully', [
                    { text: 'OK', onPress: () => navigation.goBack() },
                ]);
            }
        } catch (error) {
            console.error(`Error ${isEditMode ? 'updating' : 'adding'} allocation:`, error);
            Alert.alert('Error', `Failed to ${isEditMode ? 'update' : 'add'} allocation`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.form}>
                <Text style={styles.periodText}>
                    Period: {period.month}/{period.year}
                </Text>

                <Text style={styles.label}>Category *</Text>
                <TextInput
                    style={styles.input}
                    placeholder="e.g., Groceries, Rent, Transport"
                    value={category}
                    onChangeText={setCategory}
                />

                <Text style={styles.label}>Budget Amount (₹) *</Text>
                <TextInput
                    style={styles.input}
                    placeholder="0.00"
                    value={amount}
                    onChangeText={setAmount}
                    keyboardType="decimal-pad"
                />

                <TouchableOpacity
                    style={[styles.button, loading && styles.buttonDisabled]}
                    onPress={handleSave}
                    disabled={loading}>
                    <Text style={styles.buttonText}>
                        {loading ? (isEditMode ? 'Updating...' : 'Saving...') : (isEditMode ? 'Update Allocation' : 'Save Allocation')}
                    </Text>
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
    form: {
        padding: 16,
    },
    periodText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.primary,
        textAlign: 'center',
        marginBottom: 24,
    },
    label: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.text,
        marginBottom: 8,
        marginTop: 16,
    },
    input: {
        backgroundColor: COLORS.white,
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        borderWidth: 1,
        borderColor: COLORS.lightGray,
    },
    button: {
        backgroundColor: COLORS.secondary,
        borderRadius: 8,
        padding: 16,
        alignItems: 'center',
        marginTop: 24,
        marginBottom: 32,
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        color: COLORS.white,
        fontSize: 18,
        fontWeight: '600',
    },
});

export default AddAllocationScreen;
