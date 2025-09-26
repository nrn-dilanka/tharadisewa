import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { loadUserFromToken } from '../store/slices/authSlice';

interface AuthContextType {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: any;
  login: (credentials: { username: string; password: string }) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const dispatch = useAppDispatch();
  const { isAuthenticated, user, loading } = useAppSelector((state) => state.auth);

  useEffect(() => {
    // Load user from stored token on app start
    dispatch(loadUserFromToken());
  }, [dispatch]);

  const contextValue: AuthContextType = {
    isLoading: loading,
    isAuthenticated,
    user,
    login: async (credentials) => {
      // This will be handled by the auth slice
    },
    register: async (userData) => {
      // This will be handled by the auth slice
    },
    logout: async () => {
      // This will be handled by the auth slice
    },
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}