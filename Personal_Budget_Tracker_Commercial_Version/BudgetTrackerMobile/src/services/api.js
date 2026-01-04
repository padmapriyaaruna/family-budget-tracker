import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../config';

// Create axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 seconds for Render cold starts
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            await AsyncStorage.removeItem('authToken');
            await AsyncStorage.removeItem('userData');
        }
        return Promise.reject(error);
    }
);

// Authentication API
export const login = async (username, password) => {
    console.log('=== LOGIN DEBUG START ===');
    console.log('Username received:', username);
    console.log('Password received:', password ? '***' : 'EMPTY');
    console.log('API Base URL:', API_BASE_URL);

    const payload = { email: username, password: password };
    console.log('Payload to send:', JSON.stringify({ email: username, password: '***' }));

    try {
        const response = await apiClient.post('/api/auth/login', payload);
        console.log('Response status:', response.status);
        console.log('Response data:', response.data);

        if (response.data.status === 'success') {
            // Save token and user data
            await AsyncStorage.setItem('authToken', response.data.data.token);
            await AsyncStorage.setItem('userData', JSON.stringify(response.data.data.user));
            console.log('Token and user data saved successfully');
        }
        console.log('=== LOGIN DEBUG END ===');
        return response.data;
    } catch (error) {
        console.log('=== LOGIN ERROR ===');
        console.log('Error:', error);
        console.log('Error response:', error.response?.data);
        console.log('Error status:', error.response?.status);
        throw error;
    }
};

export const acceptInvite = async (inviteToken, password) => {
    const response = await apiClient.post('/api/auth/accept-invite', {
        invite_token: inviteToken,
        password,
    });
    return response.data;
};

export const logout = async () => {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('userData');
};

// User API
export const getProfile = async () => {
    const response = await apiClient.get('/api/user/profile');
    return response.data.data;
};

export const getHouseholdMembers = async (householdId) => {
    const response = await apiClient.get(`/api/household/${householdId}/members`);
    return response.data.data;
};

// Dashboard API
export const getDashboard = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;

    const response = await apiClient.get(`/api/dashboard/${userId}`, { params });
    return response.data.data;
};

// Income API
export const getIncome = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;

    const response = await apiClient.get(`/api/income/${userId}`, { params });
    return response.data.data;
};

export const addIncome = async (data) => {
    const response = await apiClient.post('/api/income', data);
    return response.data;
};

export const updateIncome = async (incomeId, data) => {
    const response = await apiClient.put(`/api/income/${incomeId}`, data);
    return response.data;
};

export const deleteIncome = async (incomeId) => {
    const response = await apiClient.delete(`/api/income/${incomeId}`);
    return response.data;
};

// Allocations API
export const getAllocations = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;

    const response = await apiClient.get(`/api/allocations/${userId}`, { params });
    return response.data.data;
};

export const addAllocation = async (data) => {
    const response = await apiClient.post('/api/allocations', data);
    return response.data;
};

export const updateAllocation = async (allocationId, data) => {
    const response = await apiClient.put(`/api/allocations/${allocationId}`, data);
    return response.data;
};

export const deleteAllocation = async (allocationId) => {
    const response = await apiClient.delete(`/api/allocations/${allocationId}`);
    return response.data;
};

export const copyAllocations = async (userId, fromYear, fromMonth, toYear, toMonth) => {
    const response = await apiClient.post('/api/allocations/copy', {
        user_id: userId,
        from_year: fromYear,
        from_month: fromMonth,
        to_year: toYear,
        to_month: toMonth,
    });
    return response.data;
};

// Expenses API
export const getExpenses = async (userId, year = null, month = null) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;

    const response = await apiClient.get(`/api/expenses/${userId}`, { params });
    return response.data.data;
};

export const addExpense = async (data) => {
    const response = await apiClient.post('/api/expenses', data);
    return response.data;
};

export const updateExpense = async (expenseId, data) => {
    const response = await apiClient.put(`/api/expenses/${expenseId}`, data);
    return response.data;
};

export const deleteExpense = async (expenseId) => {
    const response = await apiClient.delete(`/api/expenses/${expenseId}`);
    return response.data;
};

export default apiClient;
