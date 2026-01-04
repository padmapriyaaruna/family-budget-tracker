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

const ViewFamilyMembersScreen = ({ onNavigate }) => {
    const [members, setMembers] = useState([]);
    const [refreshing, setRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [householdId, setHouseholdId] = useState(null);

    useEffect(() => {
        loadHouseholdId();
    }, []);

    useEffect(() => {
        if (householdId) {
            loadMembers();
        }
    }, [householdId]);

    const loadHouseholdId = async () => {
        const userData = await AsyncStorage.getItem('userData');
        const user = JSON.parse(userData);
        setHouseholdId(user.household_id);
    };

    const loadMembers = async () => {
        try {
            const token = await AsyncStorage.getItem('authToken');
            const response = await axios.get(
                `${API_BASE_URL}/api/households/${householdId}/members`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setMembers(response.data.data.members);
        } catch (error) {
            console.error('Load members error:', error);
            Alert.alert('Error', 'Failed to load members');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleDelete = (memberId, memberName) => {
        Alert.alert(
            'Delete Member',
            `Are you sure you want to delete ${memberName}?`,
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            const token = await AsyncStorage.getItem('authToken');
                            await axios.delete(
                                `${API_BASE_URL}/api/households/${householdId}/members/${memberId}`,
                                { headers: { Authorization: `Bearer ${token}` } }
                            );
                            Alert.alert('Success', 'Member deleted');
                            loadMembers();
                        } catch (error) {
                            const errorMsg = error.response?.data?.detail || 'Failed to delete member';
                            Alert.alert('Error', errorMsg);
                        }
                    },
                },
            ]
        );
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
                <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadMembers(); }} />
            }>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => onNavigate('Dashboard')}>
                    <Text style={styles.backButton}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Family Members</Text>
                <View style={{ width: 50 }} />
            </View>

            <View style={styles.membersList}>
                {members.map((member) => (
                    <View key={member.id} style={styles.memberCard}>
                        <View style={styles.memberInfo}>
                            <Text style={styles.memberName}>{member.full_name}</Text>
                            <Text style={styles.memberDetails}>
                                {member.email} • {member.relationship}
                            </Text>
                            <View style={styles.badgeContainer}>
                                {member.role === 'admin' && (
                                    <View style={styles.adminBadge}>
                                        <Text style={styles.badgeText}>Admin</Text>
                                    </View>
                                )}
                                {!member.is_active && (
                                    <View style={styles.pendingBadge}>
                                        <Text style={styles.badgeText}>Pending</Text>
                                    </View>
                                )}
                            </View>
                        </View>
                        {member.role !== 'admin' && (
                            <View style={styles.actions}>
                                <TouchableOpacity
                                    style={styles.deleteButton}
                                    onPress={() => handleDelete(member.id, member.full_name)}>
                                    <Text style={styles.deleteButtonText}>Delete</Text>
                                </TouchableOpacity>
                            </View>
                        )}
                    </View>
                ))}
                {members.length === 0 && (
                    <Text style={styles.emptyText}>No members yet</Text>
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
    membersList: {
        padding: 16,
    },
    memberCard: {
        backgroundColor: COLORS.white,
        padding: 16,
        borderRadius: 10,
        marginBottom: 12,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
    },
    memberInfo: {
        marginBottom: 12,
    },
    memberName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    memberDetails: {
        fontSize: 14,
        color: COLORS.textLight,
        marginBottom: 8,
    },
    badgeContainer: {
        flexDirection: 'row',
        gap: 8,
    },
    adminBadge: {
        backgroundColor: COLORS.primary,
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 4,
    },
    pendingBadge: {
        backgroundColor: COLORS.warning,
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 4,
    },
    badgeText: {
        color: COLORS.white,
        fontSize: 12,
        fontWeight: '600',
    },
    actions: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
    },
    deleteButton: {
        backgroundColor: COLORS.danger,
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 6,
    },
    deleteButtonText: {
        color: COLORS.white,
        fontSize: 14,
        fontWeight: '600',
    },
    emptyText: {
        textAlign: 'center',
        color: COLORS.gray,
        fontSize: 16,
        marginTop: 32,
    },
});

export default ViewFamilyMembersScreen;
