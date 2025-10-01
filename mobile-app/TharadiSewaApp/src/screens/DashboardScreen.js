import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import CustomButton from '../components/CustomButton';

const DashboardScreen = () => {
  const { user, logout, isLoading } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const getRoleDisplay = (role) => {
    const roleMap = {
      'customer': 'Customer',
      'staff': 'Staff Member',
      'technician': 'Technician',
      'sales': 'Sales Representative',
      'support': 'Support Staff',
      'manager': 'Manager',
      'admin': 'Administrator',
      'owner': 'Business Owner',
    };
    return roleMap[role] || role;
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>TharadiSewa</Text>
          <Text style={styles.subtitle}>Dashboard</Text>
        </View>

        <View style={styles.welcomeCard}>
          <Text style={styles.welcomeTitle}>
            Welcome back, {user?.first_name}!
          </Text>
          <Text style={styles.welcomeText}>
            You're logged in as {getRoleDisplay(user?.role)}
          </Text>
        </View>

        <View style={styles.userInfoCard}>
          <Text style={styles.cardTitle}>Profile Information</Text>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Full Name:</Text>
            <Text style={styles.infoValue}>
              {user?.full_name || `${user?.first_name} ${user?.last_name}`}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Username:</Text>
            <Text style={styles.infoValue}>{user?.username}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Email:</Text>
            <Text style={styles.infoValue}>{user?.email}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Phone:</Text>
            <Text style={styles.infoValue}>
              {user?.phone_number || 'Not provided'}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Role:</Text>
            <Text style={styles.infoValue}>{getRoleDisplay(user?.role)}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Verified:</Text>
            <Text style={[
              styles.infoValue,
              user?.is_verified ? styles.verified : styles.unverified
            ]}>
              {user?.is_verified ? 'Yes' : 'No'}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Member Since:</Text>
            <Text style={styles.infoValue}>
              {user?.date_joined ? 
                new Date(user.date_joined).toLocaleDateString() : 
                'Unknown'
              }
            </Text>
          </View>
        </View>

        <View style={styles.actionsCard}>
          <Text style={styles.cardTitle}>Quick Actions</Text>
          
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionButtonText}>Update Profile</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionButtonText}>Change Password</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionButtonText}>View Services</Text>
          </TouchableOpacity>
          
          {user?.role === 'customer' && (
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>My Orders</Text>
            </TouchableOpacity>
          )}
          
          {['admin', 'manager', 'staff'].includes(user?.role) && (
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>Manage Users</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.logoutContainer}>
          <CustomButton
            title="Sign Out"
            onPress={handleLogout}
            loading={isLoading}
            variant="danger"
            size="large"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    fontWeight: '500',
  },
  welcomeCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  welcomeTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  welcomeText: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  userInfoCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionsCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    flex: 1,
  },
  infoValue: {
    fontSize: 16,
    color: '#333',
    flex: 1.5,
    textAlign: 'right',
  },
  verified: {
    color: '#28a745',
    fontWeight: '600',
  },
  unverified: {
    color: '#dc3545',
    fontWeight: '600',
  },
  actionButton: {
    backgroundColor: '#f8f9fa',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  actionButtonText: {
    fontSize: 16,
    color: '#007bff',
    fontWeight: '500',
    textAlign: 'center',
  },
  logoutContainer: {
    marginTop: 20,
  },
});

export default DashboardScreen;