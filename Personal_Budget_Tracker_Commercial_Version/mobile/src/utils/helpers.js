/**
 * Utility functions for formatting and data manipulation
 */

// Format currency
export const formatCurrency = (amount) => {
    return `₹${Number(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;
};

// Format date to YYYY-MM-DD
export const formatDate = (date) => {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

// Get month name
export const getMonthName = (month) => {
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month - 1];
};

// Validate email
export const isValidEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

// Calculate budget metrics
export const calculateBudgetMetrics = (allocations) => {
    const totalAllocated = allocations.reduce((sum, a) => sum + a.allocated_amount, 0);
    const totalSpent = allocations.reduce((sum, a) => sum + a.spent_amount, 0);
    const totalBalance = allocations.reduce((sum, a) => sum + a.balance, 0);

    return {
        totalAllocated,
        totalSpent,
        totalBalance,
        spentPercentage: totalAllocated > 0 ? (totalSpent / totalAllocated * 100) : 0,
    };
};

// Group expenses by category
export const groupExpensesByCategory = (expenses) => {
    return expenses.reduce((groups, expense) => {
        const category = expense.category;
        if (!groups[category]) {
            groups[category] = [];
        }
        groups[category].push(expense);
        return groups;
    }, {});
};

// Get current period
export const getCurrentPeriod = () => {
    const today = new Date();
    return {
        year: today.getFullYear(),
        month: today.getMonth() + 1,
    };
};
