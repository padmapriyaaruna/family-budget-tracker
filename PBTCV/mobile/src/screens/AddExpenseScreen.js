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
import { Picker } from '@react-native-picker/picker';
import DateTimePicker from '@react-native-community/datetimepicker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { addExpense } from '../services/api';
import { COLORS, EXPENSE_SUBCATEGORIES, PAYMENT_MODES } from '../config';
import { formatDate } from '../utils/helpers';

const AddExpenseScreen = ({ navigation }) => {
    const [userId, setUserId] = useState(null);
    const [date, setDate] = useState(new Date());
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [category, setCategory] = useState('');
    const [subcategory, setSubcategory] = useState(EXPENSE_SUBCATEGORIES[0]);
    const [amount, setAmount] = useState('');
    const [comment, setComment] = useState('');
    const [paymentMode, setPaymentMode] = useState(PAYMENT_MODES[0]);
    const [paymentDetails, setPaymentDetails] = useState('');
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
        if (!category || !amount || amount <= 0) {
            Alert.alert('Error', 'Please fill all required fields');
            return;
        }

        setLoading(true);
        try {
            await addExpense({
                user_id: userId,
                date: formatDate(date),
                category,
                subcategory,
                amount: parseFloat(amount),
                comment: comment || null,
                payment_mode: paymentMode,
                payment_details: paymentDetails || null,
            });

            Alert.alert('Success', 'Expense added successfully', [
                { text: 'OK', onPress: () => navigation.goBack() },
            ]);
        } catch (error) {
            console.error('Error adding expense:', error);
            Alert.alert('Error', 'Failed to add expense');
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
                {/* Date */}
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

                {/* Category */}
                <Text style={styles.label}>Category *</Text>
                <TextInput
                    style={styles.input}
                    placeholder="e.g., Groceries, Transport"
                    value={category}
                    onChangeText={setCategory}
                />

                {/* Subcategory */}
                <Text style={styles.label}>Subcategory *</Text>
                <View style={styles.pickerContainer}>
                    <Picker
                        selectedValue={subcategory}
                        onValueChange={setSubcategory}
                        style={styles.picker}>
                        {EXPENSE_SUBCATEGORIES.map((item) => (
                            <Picker.Item key={item} label={item} value={item} />
                        ))}
                    </Picker>
                </View>

                {/* Payment Mode */}
                <Text style={styles.label}>Payment Mode *</Text>
                <View style={styles.pickerContainer}>
                    <Picker
                        selectedValue={paymentMode}
                        onValueChange={setPaymentMode}
                        style={styles.picker}>
                        {PAYMENT_MODES.map((item) => (
                            <Picker.Item key={item} label={item} value={item} />
                        ))}
                    </Picker>
                </View>

                {/* Payment Details */}
                <Text style={styles.label}>Payment Details</Text>
                <TextInput
                    style={styles.input}
                    placeholder="e.g., Card ending in 1234, UPI ID, etc."
                    value={paymentDetails}
                    onChangeText={setPaymentDetails}
                />

                {/* Amount */}
                <Text style={styles.label}>Amount (₹) *</Text>
                <TextInput
                    style={styles.input}
                    placeholder="0.00"
                    value={amount}
                    onChangeText={setAmount}
                    keyboardType="decimal-pad"
                />

                {/* Comment */}
                <Text style={styles.label}>Comment</Text>
                <TextInput
                    style={[styles.input, styles.textArea]}
                    placeholder="Add notes (optional)"
                    value={comment}
                    onChangeText={setComment}
                    multiline
                    numberOfLines={3}
                />

                {/* Save Button */}
                <TouchableOpacity
                    style={[styles.button, loading && styles.buttonDisabled]}
                    onPress={handleSave}
                    disabled={loading}>
                    <Text style={styles.buttonText}>
                        {loading ? 'Saving...' : 'Save Expense'}
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
    textArea: {
        height: 80,
        textAlignVertical: 'top',
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
    pickerContainer: {
        backgroundColor: COLORS.white,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: COLORS.lightGray,
    },
    picker: {
        height: 50,
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

export default AddExpenseScreen;
