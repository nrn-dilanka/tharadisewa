import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import AuthNavigator from './AuthNavigator';
import AppNavigator from './AppNavigator';
import AdminNavigator from './AdminNavigator';
import LoadingScreen from '../components/LoadingScreen';

const NavigationController = () => {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();

  // Show loading screen while checking authentication status
  if (isLoading) {
    return <LoadingScreen message="Checking authentication..." />;
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? (
        isAdmin ? <AdminNavigator /> : <AppNavigator />
      ) : (
        <AuthNavigator />
      )}
    </NavigationContainer>
  );
};

export default NavigationController;