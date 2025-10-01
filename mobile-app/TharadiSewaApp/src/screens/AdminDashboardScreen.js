import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  FlatList,
  Modal,
  TextInput,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../contexts/AuthContext';
import CrudModalForm from '../components/CrudModalForm';
import { colors } from '../constants/colors';
import productService from '../services/productService';
import shopService from '../services/shopService';
import customerService from '../services/customerService';

const AdminDashboardScreen = ({ navigation }) => {
  const { user, logout, getUserList, deleteUser } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState('');
  
  // Data states
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [shops, setShops] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [stats, setStats] = useState({
    users: 0,
    products: 0,
    shops: 0,
    customers: 0,
  });

  // Form states
  const [formData, setFormData] = useState({});
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    await Promise.all([
      loadUsers(),
      loadProducts(),
      loadShops(),
      loadCustomers(),
    ]);
    setLoading(false);
    setRefreshing(false);
  };

  const loadUsers = async () => {
    try {
      const result = await getUserList();
      if (result.success) {
        const usersData = result.data.results || result.data || [];
        setUsers(usersData);
        setStats(prev => ({ ...prev, users: usersData.length }));
      }
    } catch (error) {
      console.error('Load users error:', error);
    }
  };

  const loadProducts = async () => {
    try {
      const result = await productService.getAllProducts();
      console.log('Load products result:', result.data.results);
      if (result.success) {
        const productsData = result.data.results.data || result.data || [];
        setProducts(productsData);
        setStats(prev => ({ ...prev, products: productsData.length }));
      }
    } catch (error) {
      console.error('Load products error:', error);
    }
  };

  const loadShops = async () => {
    try {
      const result = await shopService.getAllShops();
      if (result.success) {
        const shopsData = result.data.results || result.data || [];
        setShops(shopsData);
        setStats(prev => ({ ...prev, shops: shopsData.length }));
      }
    } catch (error) {
      console.error('Load shops error:', error);
    }
  };

  const loadCustomers = async () => {
    try {
      const result = await customerService.getAllCustomers();
      if (result.success) {
        const customersData = result.data.results || result.data || [];
        setCustomers(customersData);
        setStats(prev => ({ ...prev, customers: customersData.length }));
      }
    } catch (error) {
      console.error('Load customers error:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadAllData();
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: logout
        },
      ]
    );
  };

  const openCreateModal = (type) => {
    setModalType(type);
    setEditingItem(null);
    setFormData({});
    setModalVisible(true);
  };

  const openEditModal = (type, item) => {
    setModalType(type);
    setEditingItem(item);
    setFormData(item);
    setModalVisible(true);
  };

  const handleSaveItem = async (data) => {
    console.log('AdminDashboard handleSaveItem - Type:', modalType, 'Data:', data);
    setLoading(true);
    try {
      let result;
      if (modalType === 'product') {
        if (editingItem) {
          console.log('Updating product with ID:', editingItem.id);
          result = await productService.updateProduct(editingItem.id, data);
        } else {
          console.log('Creating new product');
          result = await productService.createProduct(data);
        }
        if (result.success) loadProducts();
      } else if (modalType === 'shop') {
        if (editingItem) {
          result = await shopService.updateShop(editingItem.id, data);
        } else {
          result = await shopService.createShop(data);
        }
        if (result.success) loadShops();
      } else if (modalType === 'customer') {
        if (editingItem) {
          result = await customerService.updateCustomer(editingItem.id, data);
        } else {
          result = await customerService.createCustomer(data);
        }
        if (result.success) loadCustomers();
      }

      console.log('API result:', result);

      if (result?.success) {
        Alert.alert('Success', result.message || 'Operation completed successfully');
        setModalVisible(false);
        setEditingItem(null);
        setFormData({});
        setModalType('');
      } else {
        Alert.alert('Error', result?.message || 'Operation failed');
      }
    } catch (error) {
      console.error('Save item error:', error);
      Alert.alert('Error', error.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ title, isActive, onPress, count }) => (
    <TouchableOpacity
      style={[styles.tabButton, isActive && styles.activeTabButton]}
      onPress={onPress}
    >
      <Text style={[styles.tabButtonText, isActive && styles.activeTabButtonText]}>
        {title}
      </Text>
      {count !== undefined && (
        <Text style={[styles.tabCount, isActive && styles.activeTabCount]}>
          {count}
        </Text>
      )}
    </TouchableOpacity>
  );

  const StatCard = ({ title, value, color = colors.primary, onPress }) => (
    <TouchableOpacity style={[styles.statCard, { borderLeftColor: color }]} onPress={onPress}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </TouchableOpacity>
  );

  const ItemCard = ({ item, type, onEdit, onDelete }) => {
    let title, subtitle, details;
    
    switch (type) {
      case 'user':
        title = item.full_name || `${item.first_name} ${item.last_name}`;
        subtitle = `@${item.username} • ${item.email}`;
        details = `Role: ${item.role || 'user'}`;
        break;
      case 'product':
        title = item.name;
        subtitle = item.sku ? `SKU: ${item.sku}` : 'No SKU';
        details = `Price: $${item.price || 'N/A'} • Stock: ${item.stock_quantity || 0}`;
        break;
      case 'shop':
        title = item.name;
        subtitle = item.full_address || `${item.city}, ${item.postal_code}`;
        details = `Customer: ${item.customer?.full_name || 'N/A'}`;
        break;
      case 'customer':
        title = item.full_name || `${item.first_name} ${item.last_name}`;
        subtitle = item.email || 'No email';
        details = `Phone: ${item.phone_number || 'N/A'}`;
        break;
    }

    return (
      <View style={styles.itemCard}>
        <View style={styles.itemInfo}>
          <Text style={styles.itemTitle}>{title}</Text>
          <Text style={styles.itemSubtitle}>{subtitle}</Text>
          <Text style={styles.itemDetails}>{details}</Text>
          {item.is_active !== undefined && (
            <Text style={[styles.statusBadge, {
              backgroundColor: item.is_active ? colors.success + '20' : colors.error + '20',
              color: item.is_active ? colors.success : colors.error
            }]}>
              {item.is_active ? 'Active' : 'Inactive'}
            </Text>
          )}
        </View>
        <View style={styles.itemActions}>
          <TouchableOpacity
            style={[styles.actionButton, styles.editButton]}
            onPress={() => onEdit(item)}
          >
            <Text style={styles.editButtonText}>Edit</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionButton, styles.deleteButton]}
            onPress={() => onDelete(item.id, title)}
          >
            <Text style={styles.deleteButtonText}>Delete</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <View style={styles.overviewContent}>
            <Text style={styles.sectionTitle}>System Overview</Text>
            <View style={styles.statsGrid}>
              <StatCard 
                title="Total Users" 
                value={stats.users} 
                color={colors.primary} 
                onPress={() => setActiveTab('users')}
              />
              <StatCard 
                title="Products" 
                value={stats.products} 
                color={colors.success} 
                onPress={() => setActiveTab('products')}
              />
              <StatCard 
                title="Shops" 
                value={stats.shops} 
                color={colors.warning} 
                onPress={() => setActiveTab('shops')}
              />
              <StatCard 
                title="Customers" 
                value={stats.customers} 
                color={colors.info} 
                onPress={() => setActiveTab('customers')}
              />
            </View>
            
            <View style={styles.quickActions}>
              <Text style={styles.sectionTitle}>Quick Actions</Text>
              <TouchableOpacity
                style={styles.quickActionButton}
                onPress={() => navigation.navigate('CreateUser')}
              >
                <Text style={styles.quickActionText}>👤 Create New User</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.quickActionButton}
                onPress={() => navigation.navigate('CreateProduct')}
              >
                <Text style={styles.quickActionText}>📦 Add New Product</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.quickActionButton}
                onPress={() => navigation.navigate('CreateShop')}
              >
                <Text style={styles.quickActionText}>🏪 Create New Shop</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.quickActionButton}
                onPress={() => navigation.navigate('CreateCustomer')}
              >
                <Text style={styles.quickActionText}>👥 Add New Customer</Text>
              </TouchableOpacity>
            </View>
          </View>
        );
      case 'users':
        return (
          <FlatList
            data={users}
            renderItem={({ item }) => (
              <ItemCard
                item={item}
                type="user"
                onEdit={(user) => navigation.navigate('CreateUser', { user })}
                onDelete={(userId, username) => {
                  Alert.alert(
                    'Delete User',
                    `Delete user "${username}"?`,
                    [
                      { text: 'Cancel', style: 'cancel' },
                      {
                        text: 'Delete',
                        style: 'destructive',
                        onPress: async () => {
                          const result = await deleteUser(userId);
                          if (result.success) {
                            Alert.alert('Success', 'User deleted');
                            loadUsers();
                          } else {
                            Alert.alert('Error', 'Failed to delete user');
                          }
                        },
                      },
                    ]
                  );
                }}
              />
            )}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            ListEmptyComponent={
              <Text style={styles.emptyText}>No users found</Text>
            }
          />
        );
      case 'products':
        return (
          <FlatList
            data={products}
            renderItem={({ item }) => (
              <ItemCard
                item={item}
                type="product"
                onEdit={(product) => navigation.navigate('CreateProduct', { product })}
                onDelete={(productId, productName) => {
                  Alert.alert(
                    'Delete Product',
                    `Delete product "${productName}"?`,
                    [
                      { text: 'Cancel', style: 'cancel' },
                      {
                        text: 'Delete',
                        style: 'destructive',
                        onPress: async () => {
                          const result = await productService.deleteProduct(productId);
                          if (result.success) {
                            Alert.alert('Success', 'Product deleted');
                            loadProducts();
                          } else {
                            Alert.alert('Error', 'Failed to delete product');
                          }
                        },
                      },
                    ]
                  );
                }}
              />
            )}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            ListEmptyComponent={
              <Text style={styles.emptyText}>No products found</Text>
            }
          />
        );
      case 'shops':
        return (
          <FlatList
            data={shops}
            renderItem={({ item }) => (
              <ItemCard
                item={item}
                type="shop"
                onEdit={(shop) => navigation.navigate('CreateShop', { shop })}
                onDelete={(shopId, shopName) => {
                  Alert.alert(
                    'Delete Shop',
                    `Delete shop "${shopName}"?`,
                    [
                      { text: 'Cancel', style: 'cancel' },
                      {
                        text: 'Delete',
                        style: 'destructive',
                        onPress: async () => {
                          const result = await shopService.deleteShop(shopId);
                          if (result.success) {
                            Alert.alert('Success', 'Shop deleted');
                            loadShops();
                          } else {
                            Alert.alert('Error', 'Failed to delete shop');
                          }
                        },
                      },
                    ]
                  );
                }}
              />
            )}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            ListEmptyComponent={
              <Text style={styles.emptyText}>No shops found</Text>
            }
          />
        );
      case 'customers':
        return (
          <FlatList
            data={customers}
            renderItem={({ item }) => (
              <ItemCard
                item={item}
                type="customer"
                onEdit={(customer) => navigation.navigate('CreateCustomer', { customer })}
                onDelete={(customerId, customerName) => {
                  Alert.alert(
                    'Delete Customer',
                    `Delete customer "${customerName}"?`,
                    [
                      { text: 'Cancel', style: 'cancel' },
                      {
                        text: 'Delete',
                        style: 'destructive',
                        onPress: async () => {
                          const result = await customerService.deleteCustomer(customerId);
                          if (result.success) {
                            Alert.alert('Success', 'Customer deleted');
                            loadCustomers();
                          } else {
                            Alert.alert('Error', 'Failed to delete customer');
                          }
                        },
                      },
                    ]
                  );
                }}
              />
            )}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            ListEmptyComponent={
              <Text style={styles.emptyText}>No customers found</Text>
            }
          />
        );
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.greeting}>Welcome, {user?.first_name}!</Text>
          <Text style={styles.role}>System Administrator</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabsContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <TabButton 
            title="Overview" 
            isActive={activeTab === 'overview'} 
            onPress={() => setActiveTab('overview')} 
          />
          <TabButton 
            title="Users" 
            count={stats.users}
            isActive={activeTab === 'users'} 
            onPress={() => setActiveTab('users')} 
          />
          <TabButton 
            title="Products" 
            count={stats.products}
            isActive={activeTab === 'products'} 
            onPress={() => setActiveTab('products')} 
          />
          <TabButton 
            title="Shops" 
            count={stats.shops}
            isActive={activeTab === 'shops'} 
            onPress={() => setActiveTab('shops')} 
          />
          <TabButton 
            title="Customers" 
            count={stats.customers}
            isActive={activeTab === 'customers'} 
            onPress={() => setActiveTab('customers')} 
          />
        </ScrollView>
      </View>

      {/* Content */}
      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {renderTabContent()}
      </ScrollView>

      {/* Add Button for current tab */}
      {activeTab !== 'overview' && (
        <TouchableOpacity
          style={styles.floatingButton}
          onPress={() => {
            switch (activeTab) {
              case 'users':
                navigation.navigate('CreateUser');
                break;
              case 'products':
                navigation.navigate('CreateProduct');
                break;
              case 'shops':
                navigation.navigate('CreateShop');
                break;
              case 'customers':
                navigation.navigate('CreateCustomer');
                break;
              default:
                // Fallback to modal for any other types
                openCreateModal(activeTab.slice(0, -1));
            }
          }}
        >
          <Text style={styles.floatingButtonText}>+</Text>
        </TouchableOpacity>
      )}

      {/* CRUD Modal */}
      <CrudModalForm
        visible={modalVisible}
        type={modalType}
        mode={editingItem ? 'edit' : 'create'}
        initialData={editingItem}
        onSave={handleSaveItem}
        onCancel={() => {
          setModalVisible(false);
          setEditingItem(null);
          setFormData({});
          setModalType('');
        }}
        loading={loading}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerContent: {
    flex: 1,
  },
  greeting: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text.primary,
  },
  role: {
    fontSize: 14,
    color: colors.admin.primary,
    marginTop: 2,
  },
  logoutButton: {
    backgroundColor: colors.danger,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  logoutButtonText: {
    color: colors.white,
    fontSize: 14,
    fontWeight: '600',
  },
  tabsContainer: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tabButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    marginRight: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  activeTabButton: {
    borderBottomWidth: 3,
    borderBottomColor: colors.primary,
  },
  tabButtonText: {
    fontSize: 16,
    color: colors.text.secondary,
  },
  activeTabButtonText: {
    color: colors.primary,
    fontWeight: '600',
  },
  tabCount: {
    backgroundColor: colors.text.secondary,
    color: colors.white,
    fontSize: 12,
    marginLeft: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    overflow: 'hidden',
  },
  activeTabCount: {
    backgroundColor: colors.primary,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  overviewContent: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text.primary,
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    marginBottom: 12,
    width: '48%',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text.primary,
  },
  statTitle: {
    fontSize: 14,
    color: colors.text.secondary,
    marginTop: 4,
  },
  quickActions: {
    marginBottom: 20,
  },
  quickActionButton: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionText: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '500',
  },
  itemCard: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  itemInfo: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text.primary,
    marginBottom: 4,
  },
  itemSubtitle: {
    fontSize: 14,
    color: colors.text.secondary,
    marginBottom: 2,
  },
  itemDetails: {
    fontSize: 14,
    color: colors.text.secondary,
    marginBottom: 4,
  },
  statusBadge: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  itemActions: {
    flexDirection: 'row',
  },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
    marginLeft: 8,
  },
  editButton: {
    backgroundColor: colors.info,
  },
  editButtonText: {
    color: colors.white,
    fontSize: 12,
    fontWeight: '600',
  },
  deleteButton: {
    backgroundColor: colors.danger,
  },
  deleteButtonText: {
    color: colors.white,
    fontSize: 12,
    fontWeight: '600',
  },
  emptyText: {
    textAlign: 'center',
    fontSize: 16,
    color: colors.text.secondary,
    padding: 40,
  },
  floatingButton: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    backgroundColor: colors.primary,
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  floatingButtonText: {
    color: colors.white,
    fontSize: 24,
    fontWeight: 'bold',
  },
});

export default AdminDashboardScreen;