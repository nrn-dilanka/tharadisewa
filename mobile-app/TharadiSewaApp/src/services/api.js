import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { APP_CONFIG } from '../config/app';

// Base URL for your Django backend
const BASE_URL = APP_CONFIG.API.BASE_URL;

console.log('🔧 API Configuration:', {
  BASE_URL,
  FULL_API_URL: `${BASE_URL}/api`,
  TIMEOUT: APP_CONFIG.API.TIMEOUT,
});

// Create axios instance
const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: APP_CONFIG.API.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Token management
export const tokenStorage = {
  async setTokens(accessToken, refreshToken) {
    try {
      console.log('💾 Storing tokens...');
      await AsyncStorage.setItem('accessToken', accessToken);
      await AsyncStorage.setItem('refreshToken', refreshToken);
      console.log('✅ Tokens stored successfully');
    } catch (error) {
      console.error('❌ Error saving tokens:', error);
    }
  },

  async getAccessToken() {
    try {
      const token = await AsyncStorage.getItem('accessToken');
      console.log('📖 Retrieved access token:', token ? '[TOKEN_EXISTS]' : '[NO_TOKEN]');
      return token;
    } catch (error) {
      console.error('❌ Error getting access token:', error);
      return null;
    }
  },

  async getRefreshToken() {
    try {
      const token = await AsyncStorage.getItem('refreshToken');
      console.log('📖 Retrieved refresh token:', token ? '[TOKEN_EXISTS]' : '[NO_TOKEN]');
      return token;
    } catch (error) {
      console.error('❌ Error getting refresh token:', error);
      return null;
    }
  },

  async clearTokens() {
    try {
      console.log('🗑️ Clearing tokens...');
      await AsyncStorage.removeItem('accessToken');
      await AsyncStorage.removeItem('refreshToken');
      console.log('✅ Tokens cleared successfully');
    } catch (error) {
      console.error('❌ Error clearing tokens:', error);
    }
  },
};

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    const token = await tokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Added authorization token to request');
    }
    
    // Log request details in development
    if (__DEV__) {
      console.log('📤 Request config:', {
        url: config.url,
        method: config.method,
        headers: {
          ...config.headers,
          Authorization: config.headers.Authorization ? '[HIDDEN]' : 'none',
        },
        data: config.data,
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    
    if (__DEV__) {
      console.log('📥 Response data:', response.data);
    }
    
    return response;
  },
  async (error) => {
    console.error('❌ API Error:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
    });
    
    const originalRequest = error.config;

    // Handle token refresh for 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      console.log('🔄 Attempting token refresh...');

      try {
        const refreshToken = await tokenStorage.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access, refresh } = response.data;
          await tokenStorage.setTokens(access, refresh || refreshToken);
          console.log('✅ Token refresh successful');

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
        // Refresh failed, clear tokens and redirect to login
        await tokenStorage.clearTokens();
      }
    }

    // Enhanced error handling
    if (error.code === 'ECONNABORTED') {
      error.message = `Request timeout after ${APP_CONFIG.API.TIMEOUT}ms. Please check your internet connection.`;
    } else if (error.code === 'NETWORK_ERROR' || !error.response) {
      error.message = `Network error. Please check your internet connection and ensure the server is running at ${BASE_URL}`;
    } else if (error.response?.status === 404) {
      error.message = `API endpoint not found: ${error.config?.url}`;
    } else if (error.response?.status >= 500) {
      error.message = `Server error (${error.response.status}). Please try again later.`;
    }

    return Promise.reject(error);
  }
);

export default api;