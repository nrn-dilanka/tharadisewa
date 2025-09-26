import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

// Import screens (will be created later)
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import ForgotPasswordScreen from '../screens/auth/ForgotPasswordScreen';

import DashboardScreen from '../screens/dashboard/DashboardScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';

import CustomersScreen from '../screens/customers/CustomersScreen';
import CustomerDetailScreen from '../screens/customers/CustomerDetailScreen';
import AddCustomerScreen from '../screens/customers/AddCustomerScreen';

import ShopsScreen from '../screens/shops/ShopsScreen';
import ShopDetailScreen from '../screens/shops/ShopDetailScreen';
import AddShopScreen from '../screens/shops/AddShopScreen';

import ProductsScreen from '../screens/products/ProductsScreen';
import ProductDetailScreen from '../screens/products/ProductDetailScreen';
import AddProductScreen from '../screens/products/AddProductScreen';

import PurchasesScreen from '../screens/purchases/PurchasesScreen';
import PurchaseDetailScreen from '../screens/purchases/PurchaseDetailScreen';
import AddPurchaseScreen from '../screens/purchases/AddPurchaseScreen';

import UsersScreen from '../screens/users/UsersScreen';
import UserDetailScreen from '../screens/users/UserDetailScreen';
import AddUserScreen from '../screens/users/AddUserScreen';

// Navigation types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

export type MainTabParamList = {
  Dashboard: undefined;
  Customers: undefined;
  Products: undefined;
  Purchases: undefined;
  More: undefined;
};

export type DashboardStackParamList = {
  DashboardHome: undefined;
  Profile: undefined;
  Settings: undefined;
};

export type CustomersStackParamList = {
  CustomersList: undefined;
  CustomerDetail: { customerId: number };
  AddCustomer: undefined;
  EditCustomer: { customerId: number };
};

export type ShopsStackParamList = {
  ShopsList: undefined;
  ShopDetail: { shopId: number };
  AddShop: undefined;
  EditShop: { shopId: number };
};

export type ProductsStackParamList = {
  ProductsList: undefined;
  ProductDetail: { productId: number };
  AddProduct: undefined;
  EditProduct: { productId: number };
};

export type PurchasesStackParamList = {
  PurchasesList: undefined;
  PurchaseDetail: { purchaseId: number };
  AddPurchase: undefined;
  EditPurchase: { purchaseId: number };
};

export type UsersStackParamList = {
  UsersList: undefined;
  UserDetail: { userId: number };
  AddUser: undefined;
  EditUser: { userId: number };
};

export type DrawerParamList = {
  MainTabs: undefined;
  Users: undefined;
  Shops: undefined;
  Reports: undefined;
  Settings: undefined;
  Logout: undefined;
};

// Create navigators
const RootStack = createNativeStackNavigator<RootStackParamList>();
const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();
const DashboardStack = createNativeStackNavigator<DashboardStackParamList>();
const CustomersStack = createNativeStackNavigator<CustomersStackParamList>();
const ProductsStack = createNativeStackNavigator<ProductsStackParamList>();
const PurchasesStack = createNativeStackNavigator<PurchasesStackParamList>();
const UsersStack = createNativeStackNavigator<UsersStackParamList>();
const ShopsStack = createNativeStackNavigator<ShopsStackParamList>();
const Drawer = createDrawerNavigator<DrawerParamList>();

// Auth Stack Navigator
function AuthNavigator() {
  return (
    <AuthStack.Navigator 
      screenOptions={{ 
        headerShown: false,
        animation: 'slide_from_right'
      }}
    >
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
      <AuthStack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
    </AuthStack.Navigator>
  );
}

// Dashboard Stack Navigator
function DashboardNavigator() {
  return (
    <DashboardStack.Navigator>
      <DashboardStack.Screen 
        name="DashboardHome" 
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
      <DashboardStack.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
      <DashboardStack.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </DashboardStack.Navigator>
  );
}

// Customers Stack Navigator
function CustomersNavigator() {
  return (
    <CustomersStack.Navigator>
      <CustomersStack.Screen 
        name="CustomersList" 
        component={CustomersScreen}
        options={{ title: 'Customers' }}
      />
      <CustomersStack.Screen 
        name="CustomerDetail" 
        component={CustomerDetailScreen}
        options={{ title: 'Customer Details' }}
      />
      <CustomersStack.Screen 
        name="AddCustomer" 
        component={AddCustomerScreen}
        options={{ title: 'Add Customer' }}
      />
    </CustomersStack.Navigator>
  );
}

// Products Stack Navigator
function ProductsNavigator() {
  return (
    <ProductsStack.Navigator>
      <ProductsStack.Screen 
        name="ProductsList" 
        component={ProductsScreen}
        options={{ title: 'Products' }}
      />
      <ProductsStack.Screen 
        name="ProductDetail" 
        component={ProductDetailScreen}
        options={{ title: 'Product Details' }}
      />
      <ProductsStack.Screen 
        name="AddProduct" 
        component={AddProductScreen}
        options={{ title: 'Add Product' }}
      />
    </ProductsStack.Navigator>
  );
}

// Purchases Stack Navigator
function PurchasesNavigator() {
  return (
    <PurchasesStack.Navigator>
      <PurchasesStack.Screen 
        name="PurchasesList" 
        component={PurchasesScreen}
        options={{ title: 'Purchases' }}
      />
      <PurchasesStack.Screen 
        name="PurchaseDetail" 
        component={PurchaseDetailScreen}
        options={{ title: 'Purchase Details' }}
      />
      <PurchasesStack.Screen 
        name="AddPurchase" 
        component={AddPurchaseScreen}
        options={{ title: 'New Purchase' }}
      />
    </PurchasesStack.Navigator>
  );
}

// Users Stack Navigator (Admin only)
function UsersNavigator() {
  return (
    <UsersStack.Navigator>
      <UsersStack.Screen 
        name="UsersList" 
        component={UsersScreen}
        options={{ title: 'Users' }}
      />
      <UsersStack.Screen 
        name="UserDetail" 
        component={UserDetailScreen}
        options={{ title: 'User Details' }}
      />
      <UsersStack.Screen 
        name="AddUser" 
        component={AddUserScreen}
        options={{ title: 'Add User' }}
      />
    </UsersStack.Navigator>
  );
}

// Shops Stack Navigator
function ShopsNavigator() {
  return (
    <ShopsStack.Navigator>
      <ShopsStack.Screen 
        name="ShopsList" 
        component={ShopsScreen}
        options={{ title: 'Shops' }}
      />
      <ShopsStack.Screen 
        name="ShopDetail" 
        component={ShopDetailScreen}
        options={{ title: 'Shop Details' }}
      />
      <ShopsStack.Screen 
        name="AddShop" 
        component={AddShopScreen}
        options={{ title: 'Add Shop' }}
      />
    </ShopsStack.Navigator>
  );
}

// Bottom Tab Navigator
function MainTabNavigator() {
  const userRole = useSelector((state: RootState) => state.auth.user?.role);

  return (
    <MainTab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#6b7280',
      }}
    >
      <MainTab.Screen 
        name="Dashboard" 
        component={DashboardNavigator}
        options={{
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <DashboardIcon color={color} size={size} />
          ),
        }}
      />
      <MainTab.Screen 
        name="Customers" 
        component={CustomersNavigator}
        options={{
          tabBarLabel: 'Customers',
          tabBarIcon: ({ color, size }) => (
            <CustomersIcon color={color} size={size} />
          ),
        }}
      />
      <MainTab.Screen 
        name="Products" 
        component={ProductsNavigator}
        options={{
          tabBarLabel: 'Products',
          tabBarIcon: ({ color, size }) => (
            <ProductsIcon color={color} size={size} />
          ),
        }}
      />
      <MainTab.Screen 
        name="Purchases" 
        component={PurchasesNavigator}
        options={{
          tabBarLabel: 'Purchases',
          tabBarIcon: ({ color, size }) => (
            <PurchasesIcon color={color} size={size} />
          ),
        }}
      />
    </MainTab.Navigator>
  );
}

// Drawer Navigator (for admin features and settings)
function DrawerNavigator() {
  const userRole = useSelector((state: RootState) => state.auth.user?.role);

  return (
    <Drawer.Navigator
      screenOptions={{
        headerShown: false,
        drawerStyle: {
          backgroundColor: '#ffffff',
          width: 280,
        },
        drawerActiveTintColor: '#3b82f6',
        drawerInactiveTintColor: '#6b7280',
      }}
    >
      <Drawer.Screen 
        name="MainTabs" 
        component={MainTabNavigator}
        options={{
          drawerLabel: 'Dashboard',
          drawerIcon: ({ color, size }) => (
            <DashboardIcon color={color} size={size} />
          ),
        }}
      />
      
      {(userRole === 'admin' || userRole === 'manager') && (
        <>
          <Drawer.Screen 
            name="Users" 
            component={UsersNavigator}
            options={{
              drawerLabel: 'Users',
              drawerIcon: ({ color, size }) => (
                <UsersIcon color={color} size={size} />
              ),
            }}
          />
          <Drawer.Screen 
            name="Shops" 
            component={ShopsNavigator}
            options={{
              drawerLabel: 'Shops',
              drawerIcon: ({ color, size }) => (
                <ShopsIcon color={color} size={size} />
              ),
            }}
          />
        </>
      )}
    </Drawer.Navigator>
  );
}

// Main App Navigator
function AppNavigator() {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return (
    <RootStack.Navigator screenOptions={{ headerShown: false }}>
      {isAuthenticated ? (
        <RootStack.Screen name="Main" component={DrawerNavigator} />
      ) : (
        <RootStack.Screen name="Auth" component={AuthNavigator} />
      )}
    </RootStack.Navigator>
  );
}

// Placeholder icon components (to be replaced with actual icons)
const DashboardIcon = ({ color, size }: { color: string; size: number }) => (
  <div style={{ width: size, height: size, backgroundColor: color }} />
);

const CustomersIcon = ({ color, size }: { color: string; size: number }) => (
  <div style={{ width: size, height: size, backgroundColor: color }} />
);

const ProductsIcon = ({ color, size }: { color: string; size: number }) => (
  <div style={{ width: size, height: size, backgroundColor: color }} />
);

const PurchasesIcon = ({ color, size }: { color: string; size: number }) => (
  <div style={{ width: size, height: size, backgroundColor: color }} />
);

const UsersIcon = ({ color, size }: { color: string; size: number }) => (
  <div style={{ width: size, height: size, backgroundColor: color }} />
);

const ShopsIcon = ({ color, size }: { color: string; size: number }) => (
  <div style={{ width: size, height: size, backgroundColor: color }} />
);

// Main Navigation Component
export default function Navigation() {
  return (
    <NavigationContainer>
      <AppNavigator />
    </NavigationContainer>
  );
}