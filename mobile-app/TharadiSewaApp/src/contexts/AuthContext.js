import React, { createContext, useContext, useReducer, useEffect } from 'react';
import authService, { tokenStorage } from '../services/authService';
import sessionManager from '../utils/sessionManager';
import { APP_CONFIG } from '../config/app';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isAdmin: false,
  registrationEnabled: false,
  isLoading: true,
  error: null,
};

// Actions
const AuthActionTypes = {
  SET_LOADING: 'SET_LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_USER: 'SET_USER',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_ERROR: 'SET_ERROR',
  SET_REGISTRATION_STATUS: 'SET_REGISTRATION_STATUS',
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AuthActionTypes.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };

    case AuthActionTypes.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isAdmin: action.payload.user?.role === 'admin',
        isLoading: false,
        error: null,
      };

    case AuthActionTypes.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isAdmin: false,
        isLoading: false,
        error: action.payload,
      };

    case AuthActionTypes.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isAdmin: false,
        isLoading: false,
        error: null,
      };

    case AuthActionTypes.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        isAdmin: action.payload?.role === 'admin',
        isLoading: false,
      };

    case AuthActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case AuthActionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case AuthActionTypes.SET_REGISTRATION_STATUS:
      return {
        ...state,
        registrationEnabled: action.payload,
      };

    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check if user is already logged in
  useEffect(() => {
    checkAuthStatus();
    checkRegistrationStatus();
    
    // Set up periodic token refresh check
    const interval = setInterval(async () => {
      if (state.isAuthenticated) {
        const shouldRefresh = await sessionManager.shouldRefreshToken();
        if (shouldRefresh) {
          try {
            const result = await authService.refreshToken();
            if (result.success) {
              await sessionManager.updateTokens(result.data);
            } else {
              // Refresh failed, log out user
              dispatch({ type: AuthActionTypes.LOGOUT });
              await sessionManager.clearSession();
            }
          } catch (error) {
            console.error('Auto token refresh failed:', error);
          }
        }
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [state.isAuthenticated]);

  const checkRegistrationStatus = async () => {
    try {
      const result = await authService.checkRegistrationStatus();
      if (result.success) {
        dispatch({
          type: AuthActionTypes.SET_REGISTRATION_STATUS,
          payload: result.data.registration_enabled,
        });
      }
    } catch (error) {
      console.error('Registration status check error:', error);
    }
  };

  const checkAuthStatus = async () => {
    try {
      dispatch({ type: AuthActionTypes.SET_LOADING, payload: true });
      
      // Check if session exists and is valid
      const isValid = await sessionManager.isSessionValid();
      if (isValid) {
        // Get user data from session
        const session = await sessionManager.getSession();
        if (session?.user) {
          dispatch({
            type: AuthActionTypes.SET_USER,
            payload: session.user,
          });
        } else {
          // Session invalid, try to get fresh user data
          const userResult = await authService.getCurrentUser();
          if (userResult.success) {
            dispatch({
              type: AuthActionTypes.SET_USER,
              payload: userResult.data,
            });
            await sessionManager.updateUserData(userResult.data);
          } else {
            // Unable to get user data, clear session
            await sessionManager.clearSession();
            dispatch({ type: AuthActionTypes.LOGOUT });
          }
        }
      } else {
        // Session invalid or doesn't exist
        await sessionManager.clearSession();
        dispatch({ type: AuthActionTypes.LOGOUT });
      }
    } catch (error) {
      console.error('Auth status check error:', error);
      await sessionManager.clearSession();
      dispatch({ type: AuthActionTypes.LOGOUT });
    }
  };

  const login = async (credentials) => {
    try {
      dispatch({ type: AuthActionTypes.SET_LOADING, payload: true });
      
      const result = await authService.login(credentials);
      
      if (result.success) {
        dispatch({
          type: AuthActionTypes.LOGIN_SUCCESS,
          payload: result.data,
        });
        
        // Save session data
        await sessionManager.saveSession(result.data.user, {
          access: result.data.access,
          refresh: result.data.refresh,
        });
        
        return { success: true, message: result.message };
      } else {
        dispatch({
          type: AuthActionTypes.LOGIN_FAILURE,
          payload: result.error,
        });
        return { success: false, error: result.error, message: result.message };
      }
    } catch (error) {
      const errorMessage = 'Login failed. Please try again.';
      dispatch({
        type: AuthActionTypes.LOGIN_FAILURE,
        payload: { message: errorMessage },
      });
      return { success: false, error: { message: errorMessage } };
    }
  };

  const register = async (userData) => {
    try {
      dispatch({ type: AuthActionTypes.SET_LOADING, payload: true });
      
      const result = await authService.register(userData);
      
      if (result.success) {
        // If registration successful and tokens returned, log user in
        if (result.data.access && result.data.refresh) {
          dispatch({
            type: AuthActionTypes.LOGIN_SUCCESS,
            payload: result.data,
          });
          
          // Save session data
          await sessionManager.saveSession(result.data.user, {
            access: result.data.access,
            refresh: result.data.refresh,
          });
          
          // Update registration status after first admin created
          if (result.isFirstAdmin) {
            dispatch({
              type: AuthActionTypes.SET_REGISTRATION_STATUS,
              payload: false,
            });
          }
        } else {
          dispatch({ type: AuthActionTypes.SET_LOADING, payload: false });
        }
        
        return { 
          success: true, 
          message: result.message, 
          isFirstAdmin: result.isFirstAdmin 
        };
      } else {
        dispatch({
          type: AuthActionTypes.SET_ERROR,
          payload: result.error,
        });
        return { success: false, error: result.error, message: result.message };
      }
    } catch (error) {
      const errorMessage = 'Registration failed. Please try again.';
      dispatch({
        type: AuthActionTypes.SET_ERROR,
        payload: { message: errorMessage },
      });
      return { success: false, error: { message: errorMessage } };
    }
  };

  const logout = async () => {
    try {
      dispatch({ type: AuthActionTypes.SET_LOADING, payload: true });
      await authService.logout();
      await sessionManager.clearSession();
      dispatch({ type: AuthActionTypes.LOGOUT });
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      await sessionManager.clearSession();
      dispatch({ type: AuthActionTypes.LOGOUT });
    }
  };

  const updateProfile = async (userData) => {
    try {
      const result = await authService.updateProfile(userData);
      
      if (result.success) {
        dispatch({
          type: AuthActionTypes.SET_USER,
          payload: result.data,
        });
        await sessionManager.updateUserData(result.data);
        return { success: true, message: result.message };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { 
        success: false, 
        error: { message: 'Failed to update profile' } 
      };
    }
  };

  const changePassword = async (passwords) => {
    try {
      const result = await authService.changePassword(passwords);
      return result;
    } catch (error) {
      return { 
        success: false, 
        error: { message: 'Failed to change password' } 
      };
    }
  };

  const clearError = () => {
    dispatch({ type: AuthActionTypes.CLEAR_ERROR });
  };

  // Admin functions
  const adminCreateUser = async (userData) => {
    try {
      const result = await authService.adminCreateUser(userData);
      return result;
    } catch (error) {
      return { 
        success: false, 
        error: { message: 'Failed to create user' } 
      };
    }
  };

  const adminUpdateUser = async (userId, userData) => {
    try {
      const result = await authService.adminUpdateUser(userId, userData);
      return result;
    } catch (error) {
      return { 
        success: false, 
        error: { message: 'Failed to update user' } 
      };
    }
  };

  const getUserList = async () => {
    try {
      const result = await authService.getUserList();
      return result;
    } catch (error) {
      return { 
        success: false, 
        error: { message: 'Failed to get user list' } 
      };
    }
  };

  const deleteUser = async (userId) => {
    try {
      const result = await authService.deleteUser(userId);
      return result;
    } catch (error) {
      return { 
        success: false, 
        error: { message: 'Failed to delete user' } 
      };
    }
  };

  const value = {
    // State
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isAdmin: state.isAdmin,
    registrationEnabled: state.registrationEnabled,
    isLoading: state.isLoading,
    error: state.error,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    clearError,
    checkAuthStatus,
    checkRegistrationStatus,
    
    // Admin actions
    adminCreateUser,
    adminUpdateUser,
    getUserList,
    deleteUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;