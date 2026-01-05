import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    RefreshControl,
    Alert,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, COLORS } from '../config';

const SuperAdminDashboard = ({ onLogout, onNavigate }) => {
    const [stats, setStats] = useState(null);
    const [households, setHouseholds] = useState([]);
    const [refreshing, setRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const token = await AsyncStorage.getItem('authToken');
            const headers = { Authorization: `Bearer ${token}` };

            // Get stats
            const statsRes = await axios.get(`${API_BASE_URL}/api/admin/stats`, { headers });
            setStats(statsRes.data.data);

            // Get households
            const householdsRes = await axios.get(`${API_BASE_URL}/api/admin/households`, { headers });
            setHouseholds(householdsRes.data.data.households);
        } catch (error) {
            console.error('Load error:', error);
            Alert.alert('Error', 'Failed to load data');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleRefresh = () => {
        setRefreshing(true);
        loadData();
    };

    if (loading) {
        return (
            <View style={styles.container}>
                <Text>Loading...</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
            }>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.title}>System Dashboard</Text>
                    <Text style={styles.subtitle}>Super Admin</Text>
                </View>
                <TouchableOpacity onPress={onLogout}>
                    <Text style={styles.logoutBtn}>Logout</Text>
                </TouchableOpacity>
            </View>

            {/* Stats Cards */}
            <View style={styles.statsGrid}>
                <View style={[styles.statCard, styles.householdCard]}>
                    <Text style={styles.statNumber}>{stats?.total_households || 0}</Text>
                    <Text style={styles.statLabel}>Households</Text>
                </View>
                <View style={[styles.statCard, styles.userCard]}>
                    <Text style={styles.statNumber}>{stats?.total_users || 0}</Text>
                    <Text style={styles.statLabel}>Total Users</Text>
                </View>
            </View>

            {/* Quick Actions */}
            <View style={styles.section}>
                <TouchableOpacity
                    style={styles.actionButton}
                    onPress={() => onNavigate('AddFamilyAdmin')}>
                    <Text style={styles.actionButtonText}>+ Create Family Admin</Text>
                </TouchableOpacity>
            </View>

            {/* Households List */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>All Households</Text>
                {households.map((household) => (
                    <TouchableOpacity
                        key={household.id}
                        style={styles.householdItem}
                        onPress={() => onNavigate('HouseholdDetail', {
                            householdId: household.id,
                            householdName: household.name,
                        })}>
                        <View style={styles.householdInfo}>
                            <Text style={styles.householdName}>{household.name}</Text>
                            <Text style={styles.householdDetails}>
                                Admin: {household.admin_name} • {household.member_count} members
                            </Text>
                        </View>
                        <View style={styles.householdStatus}>
                            <View
                                style={[
                                    styles.statusDot,
                                    household.is_active ? styles.activeDot : styles.inactiveDot,
                                ]}
                            />
                            <Text style={styles.arrow}>›</Text>
                        </View>
                    </TouchableOpacity>
                ))}
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
        padding: 20,
        backgroundColor: COLORS.white,
        marginTop: 40,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.lightGray,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    subtitle: {
        fontSize: 14,
        color: COLORS.textLight,
        marginTop: 4,
    },
    logoutBtn: {
        color: COLORS.danger,
        fontSize: 16,
        fontWeight: '600',
    },
    statsGrid: {
        flexDirection: 'row',
        padding: 16,
        gap: 12,
    },
    statCard: {
        flex: 1,
        backgroundColor: COLORS.white,
        padding: 20,
        borderRadius: 12,
        alignItems: 'center',
        elevation: 3,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.15,
        shadowRadius: 3.84,
    },
    householdCard: {
        borderLeftWidth: 5,
        borderLeftColor: COLORS.primary,
    },
    userCard: {
        borderLeftWidth: 5,
        borderLeftColor: COLORS.secondary,
    },
    statNumber: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 8,
    },
    statLabel: {
        fontSize: 14,
        color: COLORS.textLight,
    },
    section: {
        padding: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 12,
    },
    householdItem: {
        backgroundColor: COLORS.white,
        padding: 16,
        borderRadius: 10,
        marginBottom: 12,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
    },
    householdInfo: {
        flex: 1,
    },
    householdName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    householdDetails: {
        fontSize: 13,
        color: COLORS.textLight,
    },
    householdStatus: {
        marginLeft: 12,
    },
    statusDot: {
        width: 12,
        height: 12,
        borderRadius: 6,
    },
    activeDot: {
        backgroundColor: COLORS.success,
    },
    inactiveDot: {
        backgroundColor: COLORS.gray,
    },
    arrow: {
        fontSize: 24,
        color: COLORS.textLight,
        marginLeft: 8,
    },
    actionButton: {
        backgroundColor: COLORS.primary,
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
    },
    actionButtonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default SuperAdminDashboard;
