import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
    RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { API_BASE_URL, COLORS } from '../config';

const HouseholdDetailScreen = ({ route, onNavigate }) => {
    const { householdId, householdName } = route.params;
    const [household, setHousehold] = useState(null);
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadHouseholdDetails();
    }, []);

    const loadHouseholdDetails = async () => {
        try {
            const token = await AsyncStorage.getItem('authToken');
            const response = await axios.get(
                `${API_BASE_URL}/api/admin/households/${householdId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );

            if (response.data.status === 'success') {
                setHousehold(response.data.data.household);
                setMembers(response.data.data.members);
            }
        } catch (error) {
            console.error('Load error:', error);
            Alert.alert('Error', 'Failed to load household details');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleRefresh = () => {
        setRefreshing(true);
        loadHouseholdDetails();
    };

    const handleDeactivate = () => {
        const action = household?.is_active ? 'deactivate' : 'activate';
        Alert.alert(
            `${action.charAt(0).toUpperCase() + action.slice(1)} Household`,
            `Are you sure you want to ${action} this household? This will ${action} all users in the household.`,
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: action.charAt(0).toUpperCase() + action.slice(1),
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            const token = await AsyncStorage.getItem('authToken');
                            await axios.patch(
                                `${API_BASE_URL}/api/admin/households/${householdId}/deactivate`,
                                {},
                                { headers: { Authorization: `Bearer ${token}` } }
                            );
                            Alert.alert('Success', `Household ${action}d successfully`);
                            loadHouseholdDetails();
                        } catch (error) {
                            console.error('Deactivate error:', error);
                            Alert.alert('Error', `Failed to ${action} household`);
                        }
                    },
                },
            ]
        );
    };

    const handleDelete = () => {
        Alert.alert(
            'DELETE Household',
            `⚠️ WARNING: This will PERMANENTLY delete:\n\n• Household "${householdName}"\n• All ${members.length} users\n• All expenses\n• All income\n• All allocations\n• All savings\n\nThis action CANNOT be undone!`,
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'DELETE PERMANENTLY',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            const token = await AsyncStorage.getItem('authToken');
                            await axios.delete(
                                `${API_BASE_URL}/api/admin/households/${householdId}`,
                                { headers: { Authorization: `Bearer ${token}` } }
                            );
                            Alert.alert('Success', 'Household deleted permanently', [
                                {
                                    text: 'OK',
                                    onPress: () => onNavigate('SuperAdminDashboard'),
                                },
                            ]);
                        } catch (error) {
                            console.error('Delete error:', error);
                            Alert.alert('Error', 'Failed to delete household');
                        }
                    },
                },
            ]
        );
    };

    if (loading) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color={COLORS.primary} />
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
                <TouchableOpacity onPress={() => onNavigate('SuperAdminDashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title} numberOfLines={1}>{householdName}</Text>
                <View style={{ width: 50 }} />
            </View>

            {/* Household Info */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Household Info</Text>
                <View style={styles.infoCard}>
                    <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Name:</Text>
                        <Text style={styles.infoValue}>{household?.name}</Text>
                    </View>
                    <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Status:</Text>
                        <Text
                            style={[
                                styles.statusBadge,
                                household?.is_active ? styles.activeBadge : styles.inactiveBadge,
                            ]}>
                            {household?.is_active ? 'Active' : 'Inactive'}
                        </Text>
                    </View>
                    <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Members:</Text>
                        <Text style={styles.infoValue}>{members.length}</Text>
                    </View>
                </View>
            </View>

            {/* Members List */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Members ({members.length})</Text>
                {members.map((member) => (
                    <View key={member.id} style={styles.memberCard}>
                        <View style={styles.memberInfo}>
                            <Text style={styles.memberName}>{member.full_name}</Text>
                            <Text style={styles.memberEmail}>{member.email}</Text>
                            <View style={styles.memberMeta}>
                                <Text style={styles.memberRole}>
                                    {member.role === 'admin' ? '👑 Admin' : '👤 Member'}
                                </Text>
                                {member.relationship && (
                                    <Text style={styles.memberRelationship}>• {member.relationship}</Text>
                                )}
                                <Text
                                    style={[
                                        styles.memberStatus,
                                        member.is_active ? styles.activeStatus : styles.inactiveStatus,
                                    ]}>
                                    • {member.is_active ? 'Active' : 'Inactive'}
                                </Text>
                            </View>
                        </View>
                    </View>
                ))}
            </View>

            {/* Action Buttons */}
            <View style={styles.actions}>
                <TouchableOpacity
                    style={[styles.button, styles.deactivateButton]}
                    onPress={handleDeactivate}>
                    <Text style={styles.buttonText}>
                        {household?.is_active ? '⏸ Deactivate' : '▶️ Activate'}
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity style={[styles.button, styles.deleteButton]} onPress={handleDelete}>
                    <Text style={styles.buttonText}>🗑️ Delete Permanently</Text>
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
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        flex: 1,
        textAlign: 'center',
        marginHorizontal: 8,
    },
    section: {
        padding: 16,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 12,
    },
    infoCard: {
        backgroundColor: COLORS.white,
        borderRadius: 8,
        padding: 16,
    },
    infoRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    infoLabel: {
        fontSize: 14,
        color: COLORS.textLight,
    },
    infoValue: {
        fontSize: 14,
        fontWeight: '600',
        color: COLORS.text,
    },
    statusBadge: {
        paddingHorizontal: 12,
        paddingVertical: 4,
        borderRadius: 12,
        fontSize: 12,
        fontWeight: '600',
    },
    activeBadge: {
        backgroundColor: '#E8F5E9',
        color: '#2E7D32',
    },
    inactiveBadge: {
        backgroundColor: '#FFEBEE',
        color: '#C62828',
    },
    memberCard: {
        backgroundColor: COLORS.white,
        borderRadius: 8,
        padding: 16,
        marginBottom: 8,
    },
    memberInfo: {
        flex: 1,
    },
    memberName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    memberEmail: {
        fontSize: 14,
        color: COLORS.textLight,
        marginBottom: 6,
    },
    memberMeta: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
    },
    memberRole: {
        fontSize: 13,
        fontWeight: '600',
        color: COLORS.primary,
    },
    memberRelationship: {
        fontSize: 13,
        color: COLORS.textLight,
    },
    memberStatus: {
        fontSize: 13,
    },
    activeStatus: {
        color: '#2E7D32',
    },
    inactiveStatus: {
        color: '#C62828',
    },
    actions: {
        padding: 16,
    },
    button: {
        borderRadius: 8,
        padding: 16,
        alignItems: 'center',
        marginBottom: 12,
    },
    deactivateButton: {
        backgroundColor: COLORS.warning || '#FFA726',
    },
    deleteButton: {
        backgroundColor: COLORS.danger || '#EF5350',
    },
    buttonText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default HouseholdDetailScreen;
