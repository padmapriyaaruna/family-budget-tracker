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
import { addExpense, getAllocations } from '../services/api';
import { COLORS, EXPENSE_SUBCATEGORIES, EXPENSE_CATEGORIES } from '../config';
import { formatDate, getCurrentPeriod } from '../utils/helpers';

const AddExpenseScreen = ({ navigation }) => {
    const [userId, setUserId] = useState(null);
    const [date, setDate] = useState(new Date());
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [category, setCategory] = useState('');
    const [categories, setCategories] = useState([]);
    const [subcategory, setSubcategory] = useState(EXPENSE_SUBCATEGORIES[0]);
    const [amount, setAmount] = useState('');
    const [comment, setComment] = useState('');
    const [loading, setLoading] = useState(false);
    const [loadingCategories, setLoadingCategories] = useState(true);

    useEffect(() => {
        loadUserId();
    }, []);

    useEffect(() => {
        if (userId) {
            loadCategories();
        }
    }, [userId]);

    const loadUserId = async () => {
        const userData = await AsyncStorage.getItem('userData');
        if (userData) {
            const user = JSON.parse(userData);
            setUserId(user.id);
        }
    };

    const loadCategories = async () => {
        try {
            setLoadingCategories(true);
            const period = getCurrentPeriod();
            const allocations = await getAllocations(userId, period.year, period.month);

            // Extract unique categories from allocations
            const uniqueCategories = [...new Set(allocations.map(a => a.category))];

            if (uniqueCategories.length > 0) {
                setCategories(uniqueCategories);
                setCategory(uniqueCategories[0]); // Set first category as default
            } else {
                // Fallback to generic categories if no allocations exist
                setCategories(EXPENSE_CATEGORIES);
                setCategory(EXPENSE_CATEGORIES[0]);
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            // Fallback to generic categories on error
            setCategories(EXPENSE_CATEGORIES);
            setCategory(EXPENSE_CATEGORIES[0]);
        } finally {
            setLoadingCategories(false);
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
                {loadingCategories ? (
                    <View style={styles.input}>
                        <Text style={styles.placeholderText}>Loading categories...</Text>
                    </View>
                ) : categories.length === 0 ? (
                    <View style={styles.input}>
                        <Text style={styles.placeholderText}>No allocations found. Add allocations first.</Text>
                    </View>
                ) : (
                    <View style={styles.pickerContainer}>
                        <Picker
                            selectedValue={category}
                            onValueChange={setCategory}
                            style={styles.picker}>
                            {categories.map((item) => (
                                <Picker.Item key={item} label={item} value={item} />
                            ))}
                        </Picker>
                    </View>
                )}

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
    placeholderText: {
        color: COLORS.gray,
        fontSize: 14,
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
