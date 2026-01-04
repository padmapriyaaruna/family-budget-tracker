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
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, COLORS } from '../config';

const AddFamilyAdminScreen = ({ onNavigate }) => {
    const [householdName, setHouseholdName] = useState('');
    const [adminName, setAdminName] = useState('');
    const [adminEmail, setAdminEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [inviteToken, setInviteToken] = useState('');

    const handleCreate = async () => {
        if (!householdName || !adminName || !adminEmail) {
            Alert.alert('Error', 'Please fill in all fields');
            return;
        }

        setLoading(true);
        try {
            const token = await AsyncStorage.getItem('authToken');
            const response = await axios.post(
                `${API_BASE_URL}/api/admin/create-family`,
                {
                    household_name: householdName,
                    admin_name: adminName,
                    admin_email: adminEmail,
                },
                {
                    headers: { Authorization: `Bearer ${token}` },
                }
            );

            if (response.data.status === 'success') {
                setInviteToken(response.data.data.invite_token);
                Alert.alert(
                    'Success',
                    `Family created! Share the invite token with ${adminName}.`
                );
            }
        } catch (error) {
            console.error('Create family error:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to create family';
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
        setHouseholdName('');
        setAdminName('');
        setAdminEmail('');
        setInviteToken('');
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => onNavigate('SuperAdminDashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Create Family Admin</Text>
                <View style={{ width: 50 }} />
            </View>

            <View style={styles.form}>
                {!inviteToken ? (
                    <>
                        <Text style={styles.label}>Family Name *</Text>
                        <TextInput
                            style={styles.input}
                            value={householdName}
                            onChangeText={setHouseholdName}
                            placeholder="Enter family name"
                        />

                        <Text style={styles.label}>Admin Name *</Text>
                        <TextInput
                            style={styles.input}
                            value={adminName}
                            onChangeText={setAdminName}
                            placeholder="Enter admin full name"
                        />

                        <Text style={styles.label}>Admin Email *</Text>
                        <TextInput
                            style={styles.input}
                            value={adminEmail}
                            onChangeText={setAdminEmail}
                            placeholder="Enter admin email"
                            keyboardType="email-address"
                            autoCapitalize="none"
                        />

                        <TouchableOpacity
                            style={[styles.button, loading && styles.buttonDisabled]}
                            onPress={handleCreate}
                            disabled={loading}>
                            {loading ? (
                                <ActivityIndicator color="#FFFFFF" />
                            ) : (
                                <Text style={styles.buttonText}>Create Family Admin</Text>
                            )}
                        </TouchableOpacity>
                    </>
                ) : (
                    <View style={styles.tokenContainer}>
                        <Text style={styles.successTitle}>✅ Family Created!</Text>
                        <Text style={styles.instructions}>
                            Share this invite token with {adminName}. They can use it to set their password and access the app as the family admin.
                        </Text>

                        <View style={styles.tokenBox}>
                            <Text style={styles.tokenLabel}>Invite Token:</Text>
                            <Text style={styles.tokenText}>{inviteToken}</Text>
                        </View>

                        <TouchableOpacity style={styles.copyButton} onPress={copyToken}>
                            <Text style={styles.copyButtonText}>📋 Copy Token</Text>
                        </TouchableOpacity>

                        <TouchableOpacity style={styles.doneButton} onPress={resetForm}>
                            <Text style={styles.doneButtonText}>Create Another Family</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={styles.backToDashboard}
                            onPress={() => onNavigate('SuperAdminDashboard')}>
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

export default AddFamilyAdminScreen;
