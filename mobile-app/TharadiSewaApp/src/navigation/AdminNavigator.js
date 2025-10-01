import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AdminDashboardScreen from '../screens/AdminDashboardScreen';
import CreateUserScreen from '../screens/CreateUserScreen';
import CreateProductScreen from '../screens/CreateProductScreen';
import CreateShopScreen from '../screens/CreateShopScreen';
import CreateCustomerScreen from '../screens/CreateCustomerScreen';

const Stack = createNativeStackNavigator();

const AdminNavigator = () => {
  return (
    <Stack.Navigator
      initialRouteName="AdminDashboard"
      screenOptions={{
        headerShown: false,
        gestureEnabled: true,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen 
        name="AdminDashboard" 
        component={AdminDashboardScreen}
        options={{
          title: 'Admin Dashboard',
        }}
      />
      <Stack.Screen 
        name="CreateUser" 
        component={CreateUserScreen}
        options={{
          title: 'Create User',
        }}
      />
      <Stack.Screen 
        name="CreateProduct" 
        component={CreateProductScreen}
        options={{
          title: 'Create Product',
        }}
      />
      <Stack.Screen 
        name="CreateShop" 
        component={CreateShopScreen}
        options={{
          title: 'Create Shop',
        }}
      />
      <Stack.Screen 
        name="CreateCustomer" 
        component={CreateCustomerScreen}
        options={{
          title: 'Create Customer',
        }}
      />
      {/* Add more admin screens here as needed */}
    </Stack.Navigator>
  );
};

export default AdminNavigator;