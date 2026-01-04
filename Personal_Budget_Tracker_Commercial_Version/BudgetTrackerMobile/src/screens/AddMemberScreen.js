import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ScrollView,
    Alert,
    ActivityIndicator,
    Clipboard,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, COLORS } from '../config';

const RELATIONSHIPS = [
    'Spouse',
    'Child',
    'Parent',
    'Sibling',
    'Other Family Member',
];

const AddMemberScreen = ({ onNavigate }) => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [relationship, setRelationship] = useState('');
    const [loading, setLoading] = useState(false);
    const [inviteToken, setInviteToken] = useState('');

    const handleAddMember = async () => {
        if (!name || !email || !relationship) {
            Alert.alert('Error', 'Please fill in all fields');
            return;
        }

        setLoading(true);
        try {
            const token = await AsyncStorage.getItem('authToken');
            const userData = await AsyncStorage.getItem('userData');
            const user = JSON.parse(userData);

            const response = await axios.post(
                `${API_BASE_URL}/api/households/${user.household_id}/members`,
                {
                    name,
                    email,
                    relationship,
                },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );

            if (response.data.status === 'success') {
                setInviteToken(response.data.data.invite_token);
                Alert.alert(
                    'Success',
                    `Member added! Share the invite token with ${name}.`
                );
            }
        } catch (error) {
            console.error('Add member error:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to add member';
            Alert.alert('Error', errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const copyToken = () => {
        Clipboard.setString(inviteToken);
        Alert.alert('Copied', 'Invite token copied to clipboard');
    };

    const resetForm = () => {
        setName('');
        setEmail('');
        setRelationship('');
        setInviteToken('');
    };

    return (
        <ScrollView style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => onNavigate('Dashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Add Family Member</Text>
                <View style={{ width: 50 }} />
            </View>

            <View style={styles.form}>
                {!inviteToken ? (
                    <>
                        <Text style={styles.label}>Full Name *</Text>
                        <TextInput
                            style={styles.input}
                            value={name}
                            onChangeText={setName}
                            placeholder="Enter full name"
                        />

                        <Text style={styles.label}>Email *</Text>
                        <TextInput
                            style={styles.input}
                            value={email}
                            onChangeText={setEmail}
                            placeholder="Enter email address"
                            keyboardType="email-address"
                            autoCapitalize="none"
                        />

                        <Text style={styles.label}>Relationship *</Text>
                        <View style={styles.pickerContainer}>
                            <Picker
                                selectedValue={relationship}
                                onValueChange={setRelationship}
                                style={styles.picker}>
                                <Picker.Item label="Select relationship" value="" />
                                {RELATIONSHIPS.map((rel) => (
                                    <Picker.Item key={rel} label={rel} value={rel} />
                                ))}
                            </Picker>
                        </View>

                        <TouchableOpacity
                            style={[styles.button, loading && styles.buttonDisabled]}
                            onPress={handleAddMember}
                            disabled={loading}>
                            {loading ? (
                                <ActivityIndicator color="#FFFFFF" />
                            ) : (
                                <Text style={styles.buttonText}>Create Member</Text>
                            )}
                        </TouchableOpacity>
                    </>
                ) : (
                    <View style={styles.tokenContainer}>
                        <Text style={styles.successTitle}>✅ Member Created!</Text>
                        <Text style={styles.instructions}>
                            Share this invite token with {name}. They can use it to set their
                            password and access the app.
                        </Text>

                        <View style={styles.tokenBox}>
                            <Text style={styles.tokenLabel}>Invite Token:</Text>
                            <Text style={styles.tokenText}>{inviteToken}</Text>
                        </View>

                        <TouchableOpacity style={styles.copyButton} onPress={copyToken}>
                            <Text style={styles.copyButtonText}>📋 Copy Token</Text>
                        </TouchableOpacity>

                        <TouchableOpacity style={styles.doneButton} onPress={resetForm}>
                            <Text style={styles.doneButtonText}>Add Another Member</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={styles.backToDashboard}
                            onPress={() => onNavigate(' Dashboard')}>
                            <Text style={styles.backToDashboardText}>Back to Dashboard</Text>
                        </TouchableOpacity>
                    </View>
                )}
            </View>
        </ScrollView>
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
    form: {
        padding: 20,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: COLORS.text,
        marginBottom: 8,
        marginTop: 12,
    },
    input: {
        backgroundColor: COLORS.white,
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        borderWidth: 1,
        borderColor: COLORS.lightGray,
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
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
    tokenContainer: {
        alignItems: 'center',
        paddingVertical: 20,
    },
    successTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.success,
        marginBottom: 16,
    },
    instructions: {
        fontSize: 14,
        color: COLORS.textLight,
        textAlign: 'center',
        marginBottom: 24,
        lineHeight: 20,
    },
    tokenBox: {
        backgroundColor: COLORS.white,
        padding: 20,
        borderRadius: 12,
        width: '100%',
        borderWidth: 2,
        borderColor: COLORS.primary,
        marginBottom: 16,
    },
    tokenLabel: {
        fontSize: 12,
        color: COLORS.textLight,
        marginBottom: 8,
    },
    tokenText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        fontFamily: 'monospace',
    },
    copyButton: {
        backgroundColor: COLORS.secondary,
        borderRadius: 8,
        padding: 16,
        width: '100%',
        alignItems: 'center',
        marginBottom: 12,
    },
    copyButtonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
    doneButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 8,
        padding: 16,
        width: '100%',
        alignItems: 'center',
        marginBottom: 12,
    },
    doneButtonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
    backToDashboard: {
        padding: 12,
    },
    backToDashboardText: {
        color: COLORS.primary,
        fontSize: 14,
        textDecorationLine: 'underline',
    },
});

export default AddMemberScreen;
