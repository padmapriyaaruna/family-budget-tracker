/**
 * Application Configuration
 * Update API_BASE_URL with your local machine IP
 */

// API Configuration - Use production Render URL
export const API_BASE_URL = 'https://family-budget-api-seyi.onrender.com';

// App Configuration
export const APP_NAME = 'Family Budget Tracker';
export const CURRENCY_SYMBOL = '₹';
export const DATE_FORMAT = 'YYYY-MM-DD';

// Subcategory Options
export const EXPENSE_SUBCATEGORIES = [
    'Investment',
    'Food - Online',
    'Food - Hotel',
    'Grocery - Online',
    'Grocery - Offline',
    'School Fee',
    'Extra-Curricular',
    'Co-Curricular',
    'House Rent',
    'Maintenance',
    'Vehicle',
    'Gadgets',
    'Others'
];

// Category Options (Allocation Categories)
export const EXPENSE_CATEGORIES = [
    'Groceries',
    'Transport',
    'Entertainment',
    'Healthcare',
    'Education',
    'Utilities',
    'Shopping',
    'Food & Dining',
    'Housing',
    'Personal Care',
    'Others'
];

// Theme Colors
export const COLORS = {
    primary: '#4CAF50',
    secondary: '#2196F3',
    danger: '#F44336',
    warning: '#FF9800',
    success: '#4CAF50',
    background: '#F5F5F5',
    white: '#FFFFFF',
    black: '#000000',
    gray: '#9E9E9E',
    lightGray: '#E0E0E0',
    text: '#212121',
    textLight: '#757575',
};

export default {
    API_BASE_URL,
    APP_NAME,
    CURRENCY_SYMBOL,
    DATE_FORMAT,
    EXPENSE_SUBCATEGORIES,
    COLORS,
};
