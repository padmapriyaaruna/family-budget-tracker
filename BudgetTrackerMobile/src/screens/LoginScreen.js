import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { login } from '../services/api';

const LoginScreen = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

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

                await AsyncStorage.setItem('authToken', response.token);
                await AsyncStorage.setItem('userData', JSON.stringify(response.user));

                Alert.alert('Success', 'Login successful!');
                onLogin(response.user);
                setLoading(false);
                return; // Success - exit function

            } catch (error) {
                console.error('Login error:', error);

                // On last retry, show error
                if (i === retries - 1) {
                    const errorMsg = error.response?.data?.detail ||
                        error.message === 'Network Error'
                        ? 'Server is waking up. Please try again in 30 seconds.'
                        : 'Invalid credentials';
                    Alert.alert('Login Failed', errorMsg);
                    setLoading(false);
                } else {
                    // Wait 2 seconds before retry
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
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
                    placeholder="Email"
                    value={email}
                    onChangeText={setEmail}
                    keyboardType="email-address"
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
            </View>
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
});

export default LoginScreen;
