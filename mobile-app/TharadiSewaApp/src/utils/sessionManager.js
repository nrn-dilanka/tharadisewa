import AsyncStorage from '@react-native-async-storage/async-storage';

// Keys for AsyncStorage
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'accessToken',
  REFRESH_TOKEN: 'refreshToken',
  USER_DATA: 'userData',
  AUTH_STATE: 'authState',
  LAST_LOGIN: 'lastLogin',
  APP_STATE: 'appState',
};

export const sessionManager = {
  // Store user session data
  async saveSession(user, tokens) {
    try {
      const sessionData = {
        user,
        tokens,
        lastLogin: new Date().toISOString(),
        expiresAt: tokens.access ? this.getTokenExpiry(tokens.access) : null,
      };

      await Promise.all([
        AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access || ''),
        AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh || ''),
        AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user)),
        AsyncStorage.setItem(STORAGE_KEYS.AUTH_STATE, JSON.stringify(sessionData)),
        AsyncStorage.setItem(STORAGE_KEYS.LAST_LOGIN, sessionData.lastLogin),
      ]);

      return true;
    } catch (error) {
      console.error('Error saving session:', error);
      return false;
    }
  },

  // Retrieve user session data
  async getSession() {
    try {
      const [accessToken, refreshToken, userData, authState, lastLogin] = await Promise.all([
        AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN),
        AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN),
        AsyncStorage.getItem(STORAGE_KEYS.USER_DATA),
        AsyncStorage.getItem(STORAGE_KEYS.AUTH_STATE),
        AsyncStorage.getItem(STORAGE_KEYS.LAST_LOGIN),
      ]);

      if (!accessToken || !userData) {
        return null;
      }

      return {
        tokens: {
          access: accessToken,
          refresh: refreshToken,
        },
        user: JSON.parse(userData),
        authState: authState ? JSON.parse(authState) : null,
        lastLogin,
      };
    } catch (error) {
      console.error('Error getting session:', error);
      return null;
    }
  },

  // Clear user session data
  async clearSession() {
    try {
      await Promise.all([
        AsyncStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN),
        AsyncStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN),
        AsyncStorage.removeItem(STORAGE_KEYS.USER_DATA),
        AsyncStorage.removeItem(STORAGE_KEYS.AUTH_STATE),
        AsyncStorage.removeItem(STORAGE_KEYS.LAST_LOGIN),
      ]);
      return true;
    } catch (error) {
      console.error('Error clearing session:', error);
      return false;
    }
  },

  // Update user data in session
  async updateUserData(userData) {
    try {
      const currentSession = await this.getSession();
      if (currentSession) {
        await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
        
        const updatedAuthState = {
          ...currentSession.authState,
          user: userData,
        };
        await AsyncStorage.setItem(STORAGE_KEYS.AUTH_STATE, JSON.stringify(updatedAuthState));
      }
      return true;
    } catch (error) {
      console.error('Error updating user data:', error);
      return false;
    }
  },

  // Update tokens in session
  async updateTokens(tokens) {
    try {
      await Promise.all([
        AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access || ''),
        AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh || ''),
      ]);

      // Update auth state with new token expiry
      const currentSession = await this.getSession();
      if (currentSession) {
        const updatedAuthState = {
          ...currentSession.authState,
          tokens,
          expiresAt: tokens.access ? this.getTokenExpiry(tokens.access) : null,
        };
        await AsyncStorage.setItem(STORAGE_KEYS.AUTH_STATE, JSON.stringify(updatedAuthState));
      }
      return true;
    } catch (error) {
      console.error('Error updating tokens:', error);
      return false;
    }
  },

  // Check if session is valid
  async isSessionValid() {
    try {
      const session = await this.getSession();
      if (!session || !session.tokens.access) {
        return false;
      }

      // Check if token is expired
      const expiryTime = this.getTokenExpiry(session.tokens.access);
      if (expiryTime && new Date() >= new Date(expiryTime)) {
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error checking session validity:', error);
      return false;
    }
  },

  // Get token expiry from JWT token
  getTokenExpiry(token) {
    try {
      if (!token) return null;
      
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      
      // Decode base64 URL
      const payload = JSON.parse(
        atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
      );
      
      // exp is in seconds since epoch, convert to milliseconds
      if (payload.exp) {
        return new Date(payload.exp * 1000);
      }
      
      return null;
    } catch (error) {
      console.error('Error parsing token expiry:', error);
      return null;
    }
  },

  // Get time until token expires (in minutes)
  async getTimeUntilExpiry() {
    try {
      const session = await this.getSession();
      if (!session || !session.tokens.access) {
        return 0;
      }

      const expiryTime = this.getTokenExpiry(session.tokens.access);
      if (!expiryTime) return 0;

      const now = new Date();
      const expiry = new Date(expiryTime);
      const diffMs = expiry.getTime() - now.getTime();
      
      return Math.max(0, Math.floor(diffMs / (1000 * 60))); // Return minutes
    } catch (error) {
      console.error('Error getting time until expiry:', error);
      return 0;
    }
  },

  // Check if token needs refresh (expires in next 5 minutes)
  async shouldRefreshToken() {
    try {
      const timeUntilExpiry = await this.getTimeUntilExpiry();
      return timeUntilExpiry <= 5 && timeUntilExpiry > 0; // Refresh if expires in 5 minutes or less
    } catch (error) {
      console.error('Error checking if should refresh token:', error);
      return false;
    }
  },

  // Save app state
  async saveAppState(state) {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.APP_STATE, JSON.stringify(state));
      return true;
    } catch (error) {
      console.error('Error saving app state:', error);
      return false;
    }
  },

  // Get app state
  async getAppState() {
    try {
      const state = await AsyncStorage.getItem(STORAGE_KEYS.APP_STATE);
      return state ? JSON.parse(state) : null;
    } catch (error) {
      console.error('Error getting app state:', error);
      return null;
    }
  },
};

export default sessionManager;