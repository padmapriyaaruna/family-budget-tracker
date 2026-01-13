import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    RefreshControl,
    TouchableOpacity,
    ActivityIndicator,
} from 'react-native';
import { API_URL } from '../config';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { formatCurrency } from '../utils/helpers';
import { COLORS } from '../config';

const SavingsScreen = ({ user, onNavigate }) => {
    const [yearsData, setYearsData] = useState([]);
    const [expandedYear, setExpandedYear] = useState(null);
    const [liquidityData, setLiquidityData] = useState({});
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        setIsAdmin(user.role === 'admin');
        fetchYears();
    }, []);

    const fetchYears = async () => {
        try {
            const token = await AsyncStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/savings/years/${user.id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const result = await response.json();
            if (result.status === 'success') {
                setYearsData(result.data);
                // Auto-expand most recent year if available
                if (result.data.length > 0 && !expandedYear) {
                    const mostRecentYear = result.data[0];
                    setExpandedYear(mostRecentYear);
                    fetchLiquidity(mostRecentYear);
                }
            }
        } catch (error) {
            console.error('Error fetching savings years:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const fetchLiquidity = async (year) => {
        try {
            const token = await AsyncStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/savings/liquidity/${user.id}/${year}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const result = await response.json();
            if (result.status === 'success') {
                setLiquidityData(prev => ({
                    ...prev,
                    [year]: result.data.liquidity
                }));
            }
        } catch (error) {
            console.error('Error fetching liquidity:', error);
        }
    };

    const toggleYear = (year) => {
        if (expandedYear === year) {
            setExpandedYear(null);
        } else {
            setExpandedYear(year);
            if (!liquidityData[year]) {
                fetchLiquidity(year);
            }
        }
    };

    const calculateYearTotal = (year) => {
        const data = liquidityData[year];
        if (!data || data.length === 0) return 0;

        return data.reduce((total, item) => total + (parseFloat(item.liquidity) || 0), 0);
    };

    const renderMemberView = (year) => {
        const data = liquidityData[year];
        if (!data || data.length === 0) {
            return <Text style={styles.noDataText}>No liquidity data for this year</Text>;
        }

        const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];

        return (
            <View style={styles.tableContainer}>
                {/* Header Row */}
                <View style={styles.tableRow}>
                    <Text style={[styles.tableHeader, { flex: 2 }]}>Month</Text>
                    <Text style={[styles.tableHeader, styles.textRight, { flex: 1 }]}>Liquidity</Text>
                </View>

                {/* Data Rows */}
                {data
                    .sort((a, b) => a.month - b.month)
                    .map((item, index) => (
                        <View key={index} style={[styles.tableRow, index % 2 === 0 && styles.tableRowEven]}>
                            <Text style={[styles.tableCell, { flex: 2 }]}>
                                {monthNames[parseInt(item.month)]}
                            </Text>
                            <Text style={[
                                styles.tableCell,
                                styles.textRight,
                                { flex: 1 },
                                parseFloat(item.liquidity) < 0 && styles.negativeAmount
                            ]}>
                                {formatCurrency(item.liquidity)}
                            </Text>
                        </View>
                    ))}
            </View>
        );
    };

    const renderAdminView = (year) => {
        const data = liquidityData[year];
        if (!data || data.length === 0) {
            return <Text style={styles.noDataText}>No liquidity data for this year</Text>;
        }

        const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];

        // Build pivot table structure: { month: { member1: amount, member2: amount, total: amount } }
        const pivotData = {};
        const members = new Set();

        data.forEach(item => {
            const month = parseInt(item.month);
            const member = item.member;
            const liquidity = parseFloat(item.liquidity) || 0;

            members.add(member);

            if (!pivotData[month]) {
                pivotData[month] = {};
            }
            pivotData[month][member] = liquidity;
        });

        // Calculate totals for each month
        const sortedMonths = Object.keys(pivotData).map(m => parseInt(m)).sort((a, b) => a - b);
        const membersList = Array.from(members).sort();

        return (
            <ScrollView horizontal style={styles.tableContainer}>
                <View>
                    {/* Header Row */}
                    <View style={[styles.tableRow, styles.adminTableHeader]}>
                        <Text style={[styles.tableHeader, styles.monthColumn]}>Month</Text>
                        {membersList.map((member, idx) => (
                            <Text key={idx} style={[styles.tableHeader, styles.memberColumn]}>
                                {member}
                            </Text>
                        ))}
                        <Text style={[styles.tableHeader, styles.totalColumn]}>Total</Text>
                    </View>

                    {/* Data Rows */}
                    {sortedMonths.map((month, index) => {
                        const monthData = pivotData[month];
                        const rowTotal = membersList.reduce((sum, member) =>
                            sum + (monthData[member] || 0), 0);

                        return (
                            <View key={month} style={[styles.tableRow, index % 2 === 0 && styles.tableRowEven]}>
                                <Text style={[styles.tableCell, styles.monthColumn]}>
                                    {monthNames[month]}
                                </Text>
                                {membersList.map((member, idx) => (
                                    <Text
                                        key={idx}
                                        style={[
                                            styles.tableCell,
                                            styles.memberColumn,
                                            styles.textRight,
                                            (monthData[member] || 0) < 0 && styles.negativeAmount
                                        ]}
                                    >
                                        {formatCurrency(monthData[member] || 0)}
                                    </Text>
                                ))}
                                <Text style={[
                                    styles.tableCell,
                                    styles.totalColumn,
                                    styles.textRight,
                                    styles.boldText,
                                    rowTotal < 0 && styles.negativeAmount
                                ]}>
                                    {formatCurrency(rowTotal)}
                                </Text>
                            </View>
                        );
                    })}
                </View>
            </ScrollView>
        );
    };

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={styles.loadingText}>Loading savings data...</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={() => {
                    setRefreshing(true);
                    fetchYears();
                }} />
            }
        >
            <View style={styles.header}>
                <Text style={styles.title}>💰 Savings Tracker</Text>
                <Text style={styles.subtitle}>
                    Track your household's liquid funds (Income - Allocations)
                </Text>
            </View>

            {yearsData.length === 0 ? (
                <View style={styles.noDataContainer}>
                    <Text style={styles.noDataText}>
                        💡 No income/allocation data found.
                    </Text>
                    <Text style={styles.noDataSubtext}>
                        Add income in the Income tab to see liquidity here!
                    </Text>
                </View>
            ) : (
                <View style={styles.content}>
                    <Text style={styles.infoText}>
                        <Text style={styles.boldText}>Liquidity</Text> = Income - Total Allocations for each month
                    </Text>

                    {yearsData.map((year) => {
                        const isExpanded = expandedYear === year;
                        const yearTotal = calculateYearTotal(year);

                        return (
                            <View key={year} style={styles.yearCard}>
                                <TouchableOpacity
                                    style={styles.yearHeader}
                                    onPress={() => toggleYear(year)}
                                >
                                    <Text style={styles.yearText}>
                                        {isAdmin ? `📅 ${year} - Family Total Liquidity: ` : `👤 My Personal Liquidity - ${year}: `}
                                        <Text style={[
                                            styles.yearTotal,
                                            yearTotal < 0 && styles.negativeAmount
                                        ]}>
                                            {formatCurrency(yearTotal)}
                                        </Text>
                                    </Text>
                                    <Text style={styles.expandIcon}>
                                        {isExpanded ? '▼' : '▶'}
                                    </Text>
                                </TouchableOpacity>

                                {isExpanded && (
                                    <View style={styles.yearContent}>
                                        {isAdmin ? renderAdminView(year) : renderMemberView(year)}
                                    </View>
                                )}
                            </View>
                        );
                    })}

                    <View style={styles.tipContainer}>
                        <Text style={styles.tipText}>
                            💡 <Text style={styles.boldText}>Tip:</Text> Liquidity shows unallocated funds.
                            Positive values mean you have extra money, negative means you over-allocated!
                        </Text>
                    </View>
                </View>
            )}
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F5',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#F5F5F5',
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: '#757575',
    },
    header: {
        backgroundColor: '#FFFFFF',
        padding: 20,
        marginTop: 40,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#212121',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 14,
        color: '#757575',
    },
    content: {
        padding: 16,
    },
    infoText: {
        fontSize: 14,
        color: '#757575',
        marginBottom: 16,
        padding: 12,
        backgroundColor: '#E3F2FD',
        borderRadius: 8,
    },
    boldText: {
        fontWeight: 'bold',
        color: '#212121',
    },
    yearCard: {
        backgroundColor: '#FFFFFF',
        borderRadius: 8,
        marginBottom: 12,
        overflow: 'hidden',
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    yearHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        backgroundColor: '#F5F5F5',
    },
    yearText: {
        fontSize: 16,
        color: '#212121',
        flex: 1,
    },
    yearTotal: {
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    expandIcon: {
        fontSize: 16,
        color: '#757575',
        marginLeft: 8,
    },
    yearContent: {
        padding: 16,
    },
    tableContainer: {
        marginTop: 8,
    },
    tableRow: {
        flexDirection: 'row',
        paddingVertical: 12,
        paddingHorizontal: 8,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    tableRowEven: {
        backgroundColor: '#FAFAFA',
    },
    adminTableHeader: {
        backgroundColor: '#E8F5E9',
    },
    tableHeader: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#212121',
        paddingHorizontal: 8,
    },
    tableCell: {
        fontSize: 14,
        color: '#424242',
        paddingHorizontal: 8,
    },
    monthColumn: {
        width: 120,
    },
    memberColumn: {
        width: 100,
    },
    totalColumn: {
        width: 100,
        backgroundColor: '#FFF9C4',
    },
    textRight: {
        textAlign: 'right',
    },
    negativeAmount: {
        color: '#F44336',
    },
    noDataContainer: {
        padding: 32,
        alignItems: 'center',
    },
    noDataText: {
        fontSize: 16,
        color: '#757575',
        textAlign: 'center',
        marginBottom: 8,
    },
    noDataSubtext: {
        fontSize: 14,
        color: '#9E9E9E',
        textAlign: 'center',
    },
    tipContainer: {
        marginTop: 16,
        padding: 12,
        backgroundColor: '#FFF3E0',
        borderRadius: 8,
        borderLeftWidth: 4,
        borderLeftColor: '#FF9800',
    },
    tipText: {
        fontSize: 14,
        color: '#757575',
        lineHeight: 20,
    },
});

export default SavingsScreen;
