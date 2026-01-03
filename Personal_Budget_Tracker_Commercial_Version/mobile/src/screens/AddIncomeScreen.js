import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ScrollView,
    Alert,
    Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { addIncome } from '../services/api';
import { COLORS } from '../config';
import { formatDate } from '../utils/helpers';

const AddIncomeScreen = ({ navigation }) => {
    const [userId, setUserId] = useState(null);
    const [date, setDate] = useState(new Date());
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [source, setSource] = useState('');
    const [amount, setAmount] = useState('');
    const [loading, setLoading] = useState(false);

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
        if (!source || !amount || amount <= 0) {
            Alert.alert('Error', 'Please fill all required fields');
            return;
        }

        setLoading(true);
        try {
            await addIncome({
                user_id: userId,
                date: formatDate(date),
                source,
                amount: parseFloat(amount),
            });

            Alert.alert('Success', 'Income added successfully', [
                { text: 'OK', onPress: () => navigation.goBack() },
            ]);
        } catch (error) {
            console.error('Error adding income:', error);
            Alert.alert('Error', 'Failed to add income');
        } finally {
            setLoading(false);
        }
    };

    const onDateChange = (event, selectedDate) => {
        setShowDatePicker(Platform.OS === 'ios');
        if (selectedDate) {
            setDate(selectedDate);
        }
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.form}>
                <Text style={styles.label}>Date *</Text>
                <TouchableOpacity
                    style={styles.dateButton}
                    onPress={() => setShowDatePicker(true)}>
                    <Text style={styles.dateText}>{formatDate(date)}</Text>
                </TouchableOpacity>
                {showDatePicker && (
                    <DateTimePicker
                        value={date}
                        mode="date"
                        display="default"
                        onChange={onDateChange}
                    />
                )}

                <Text style={styles.label}>Source *</Text>
                <TextInput
                    style={styles.input}
                    placeholder="e.g., Salary, Bonus"
                    value={source}
                    onChangeText={setSource}
                />

                <Text style={styles.label}>Amount (₹) *</Text>
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
                        {loading ? 'Saving...' : 'Save Income'}
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
    dateButton: {
        backgroundColor: COLORS.white,
        borderRadius: 8,
        padding: 12,
        borderWidth: 1,
        borderColor: COLORS.lightGray,
    },
    dateText: {
        fontSize: 16,
        color: COLORS.text,
    },
    button: {
        backgroundColor: COLORS.primary,
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

export default AddIncomeScreen;
