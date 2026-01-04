import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
    Modal,
    ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { login } from '../services/api';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const LoginScreen = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    // Password setup modal state
    const [setupModalVisible, setSetupModalVisible] = useState(false);
    const [inviteToken, setInviteToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [setupLoading, setSetupLoading] = useState(false);

    const handleLogin = async () => {
        if (!username || !password) {
            Alert.alert('Error', 'Please enter both username and password');
            return;
        }

        setLoading(true);
        let retries = 3;

        for (let i = 0; i < retries; i++) {
            try {
                const response = await login(username, password);

                // API returns { status: 'success', data: { token, user } }
                if (response.status === 'success' && response.data) {
                    await AsyncStorage.setItem('authToken', response.data.token);
                    await AsyncStorage.setItem('userData', JSON.stringify(response.data.user));

                    Alert.alert('Success', 'Login successful!');
                    onLogin(response.data.user);
                    setLoading(false);
                    return; // Success - exit function
                }

            } catch (error) {
                console.error('Login error:', error);

                // On last retry, show error
                if (i === retries - 1) {
                    const errorMsg = error.response?.data?.detail ||
                        error.code === 'ECONNABORTED' || error.message === 'Network Error'
                        ? 'Server is waking up. Please wait 30 seconds and try again.'
                        : 'Invalid credentials. Please check your email and password.';
                    Alert.alert('Login Failed', errorMsg);
                    setLoading(false);
                } else {
                    // Wait 2 seconds before retry
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
        }
    };

    const handlePasswordSetup = async () => {
        if (!inviteToken || !newPassword || !confirmPassword) {
            Alert.alert('Error', 'Please fill in all fields');
            return;
        }

        if (newPassword !== confirmPassword) {
            Alert.alert('Error', 'Passwords do not match');
            return;
        }

        if (newPassword.length < 6) {
            Alert.alert('Error', 'Password must be at least 6 characters');
            return;
        }

        setSetupLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/api/auth/setup-password`, {
                invite_token: inviteToken,
                password: newPassword,
            });

            if (response.data.status === 'success') {
                Alert.alert('Success', 'Password set successfully! You can now login.');
                setSetupModalVisible(false);
                setInviteToken('');
                setNewPassword('');
                setConfirmPassword('');
            }
        } catch (error) {
            console.error('Setup error:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to setup password. Invalid invite token?';
            Alert.alert('Setup Failed', errorMsg);
        } finally {
            setSetupLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.content}>
                <Text style={styles.logo}>💰</Text>
                <Text style={styles.title}>Family Budget Tracker</Text>
                <Text style={styles.subtitle}>Manage your family budget</Text>

                <TextInput
                    style={styles.input}
                    placeholder="Username"
                    value={username}
                    onChangeText={setUsername}
                    autoCapitalize="none"
                />

                <TextInput
                    style={styles.input}
                    placeholder="Password"
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry={true}
                />

                <TouchableOpacity
                    style={[styles.button, loading && styles.buttonDisabled]}
                    onPress={handleLogin}
                    disabled={loading}>
                    {loading ? (
                        <ActivityIndicator color="#FFFFFF" />
                    ) : (
                        <Text style={styles.buttonText}>Login</Text>
                    )}
                </TouchableOpacity>

                <Text style={styles.footerText}>
                    New member? Ask admin for invite link
                </Text>

                <TouchableOpacity onPress={() => setSetupModalVisible(true)}>
                    <Text style={styles.setupLink}>New User? Setup Password →</Text>
                </TouchableOpacity>
            </View>

            {/* Password Setup Modal */}
            <Modal
                visible={setupModalVisible}
                animationType="slide"
                transparent={true}
                onRequestClose={() => setSetupModalVisible(false)}>
                <View style={styles.modalOverlay}>
                    <View style={styles.modalContent}>
                        <View style={styles.modalHeader}>
                            <Text style={styles.modalTitle}>Setup Password</Text>
                            <TouchableOpacity onPress={() => setSetupModalVisible(false)}>
                                <Text style={styles.closeButton}>✕</Text>
                            </TouchableOpacity>
                        </View>

                        <ScrollView style={styles.modalForm}>
                            <Text style={styles.modalSubtitle}>
                                Enter your invite token from the admin
                            </Text>

                            <Text style={styles.label}>Invite Token</Text>
                            <TextInput
                                style={styles.modalInput}
                                value={inviteToken}
                                onChangeText={setInviteToken}
                                placeholder="Enter invite token"
                                autoCapitalize="none"
                            />

                            <Text style={styles.label}>New Password</Text>
                            <TextInput
                                style={styles.modalInput}
                                value={newPassword}
                                onChangeText={setNewPassword}
                                placeholder="At least 6 characters"
                                secureTextEntry={true}
                            />

                            <Text style={styles.label}>Confirm Password</Text>
                            <TextInput
                                style={styles.modalInput}
                                value={confirmPassword}
                                onChangeText={setConfirmPassword}
                                placeholder="Re-enter password"
                                secureTextEntry={true}
                            />

                            <TouchableOpacity
                                style={[styles.modalButton, setupLoading && styles.buttonDisabled]}
                                onPress={handlePasswordSetup}
                                disabled={setupLoading}>
                                {setupLoading ? (
                                    <ActivityIndicator color="#FFFFFF" />
                                ) : (
                                    <Text style={styles.buttonText}>Setup Password</Text>
                                )}
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.modalCancelButton}
                                onPress={() => setSetupModalVisible(false)}>
                                <Text style={styles.cancelButtonText}>Cancel</Text>
                            </TouchableOpacity>
                        </ScrollView>
                    </View>
                </View>
            </Modal>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F5',
        justifyContent: 'center',
        padding: 24,
    },
    content: {
        alignItems: 'center',
    },
    logo: {
        fontSize: 64,
        marginBottom: 16,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 8,
        color: '#212121',
    },
    subtitle: {
        fontSize: 16,
        color: '#757575',
        marginBottom: 32,
    },
    input: {
        width: '100%',
        backgroundColor: '#FFFFFF',
        borderRadius: 8,
        padding: 16,
        fontSize: 16,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: '#E0E0E0',
        color: '#212121',
    },
    button: {
        width: '100%',
        backgroundColor: '#4CAF50',
        borderRadius: 8,
        padding: 16,
        alignItems: 'center',
        marginTop: 8,
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        color: '#FFFFFF',
        fontSize: 18,
        fontWeight: '600',
    },
    footerText: {
        color: '#757575',
        fontSize: 14,
        marginTop: 24,
    },
    setupLink: {
        color: '#2196F3',
        fontSize: 16,
        fontWeight: '600',
        marginTop: 16,
        textDecorationLine: 'underline',
    },
    // Modal styles
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    modalContent: {
        backgroundColor: '#FFFFFF',
        borderRadius: 12,
        width: '90%',
        maxHeight: '80%',
        padding: 20,
    },
    modalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
        paddingBottom: 12,
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#212121',
    },
    closeButton: {
        fontSize: 28,
        color: '#9E9E9E',
    },
    modalForm: {
        marginBottom: 20,
    },
    modalSubtitle: {
        fontSize: 14,
        color: '#757575',
        marginBottom: 20,
        lineHeight: 20,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#212121',
        marginBottom: 8,
        marginTop: 12,
    },
    modalInput: {
        backgroundColor: '#F5F5F5',
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        borderWidth: 1,
        borderColor: '#E0E0E0',
    },
    modalButton: {
        backgroundColor: '#4CAF50',
        borderRadius: 8,
        padding: 16,
        alignItems: 'center',
        marginTop: 20,
    },
    modalCancelButton: {
        backgroundColor: '#E0E0E0',
        borderRadius: 8,
        padding: 16,
        alignItems: 'center',
        marginTop: 12,
    },
    cancelButtonText: {
        color: '#212121',
        fontSize: 16,
        fontWeight: '600',
    },
});

export default LoginScreen;
