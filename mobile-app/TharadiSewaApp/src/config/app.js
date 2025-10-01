// App Configuration
export const APP_CONFIG = {
  // API Configuration
  API: {
    BASE_URL: __DEV__ ? 'http://192.168.8.160:8000' : 'https://your-production-url.com',
    TIMEOUT: 15000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
  },
  
  // Authentication Configuration
  AUTH: {
    TOKEN_REFRESH_THRESHOLD: 5, // minutes
    AUTO_LOGOUT_TIMEOUT: 30, // minutes of inactivity
    MAX_LOGIN_ATTEMPTS: 5,
    LOGIN_ATTEMPT_TIMEOUT: 15, // minutes
  },
  
  // Storage Configuration
  STORAGE: {
    CACHE_DURATION: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
    MAX_CACHE_SIZE: 50, // MB
  },
  
  // UI Configuration
  UI: {
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 500,
    PAGINATION_SIZE: 20,
  },
  
  // Feature Flags
  FEATURES: {
    BIOMETRIC_AUTH: true,
    PUSH_NOTIFICATIONS: true,
    OFFLINE_MODE: true,
    DARK_THEME: true,
    DEBUG_MODE: __DEV__,
  },
  
  // App Information
  APP_INFO: {
    NAME: 'TharadiSewa',
    VERSION: '1.0.0',
    BUILD_NUMBER: 1,
    SUPPORT_EMAIL: 'support@tharadisewa.com',
    PRIVACY_URL: 'https://tharadisewa.com/privacy',
    TERMS_URL: 'https://tharadisewa.com/terms',
  },
};

// Environment specific configurations
export const getApiUrl = (endpoint = '') => {
  return `${APP_CONFIG.API.BASE_URL}/api${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
};

// Validation functions
export const isProduction = () => !__DEV__;
export const isDevelopment = () => __DEV__;

export default APP_CONFIG;