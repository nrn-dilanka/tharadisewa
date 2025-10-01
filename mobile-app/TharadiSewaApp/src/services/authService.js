import api, { tokenStorage } from './api';

export const authService = {
  // Check registration status (whether admin exists)
  async checkRegistrationStatus() {
    try {
      console.log('🔍 Checking registration status...');
      console.log('API Base URL:', api.defaults.baseURL);
      
      const response = await api.get('/auth/registration-status/');
      console.log('✅ Registration status response:', response.data);
      
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('❌ Registration status check error:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
        url: error.config?.url,
      });
      
      // Handle specific error cases
      if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        return {
          success: false,
          error: { 
            message: 'Cannot connect to server. Please check your internet connection and ensure the server is running.' 
          },
        };
      }
      
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to check registration status. Server may be offline.' },
      };
    }
  },

  // Register new admin (only if no admin exists)
  async register(userData) {
    try {
      console.log('🚀 Attempting registration...');
      console.log('Registration data:', { 
        ...userData, 
        password: '[HIDDEN]', 
        password_confirm: '[HIDDEN]' 
      });
      console.log('API URL:', `${api.defaults.baseURL}/auth/register/`);
      
      const response = await api.post('/auth/register/', userData);
      console.log('✅ Registration successful:', {
        ...response.data,
        access: '[TOKEN]',
        refresh: '[TOKEN]',
      });
      
      const { access, refresh, user } = response.data;
      
      // Store tokens if registration successful
      if (access && refresh) {
        await tokenStorage.setTokens(access, refresh);
        console.log('✅ Tokens stored successfully');
      }
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Registration successful',
        isFirstAdmin: response.data.is_first_admin || false,
      };
    } catch (error) {
      console.error('❌ Registration error:', error);
      console.error('Registration error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data,
        },
      });
      
      // Handle specific error cases
      if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        return {
          success: false,
          error: { 
            message: 'Cannot connect to server. Please check your internet connection and ensure the backend server is running on the correct port.' 
          },
          message: 'Network connection failed',
        };
      }
      
      if (error.response?.status === 404) {
        return {
          success: false,
          error: { 
            message: 'Registration endpoint not found. Please ensure the backend server is properly configured.' 
          },
          message: 'Server endpoint not available',
        };
      }
      
      if (error.response?.status === 500) {
        return {
          success: false,
          error: { 
            message: 'Server error occurred. Please try again or contact support if the problem persists.' 
          },
          message: 'Internal server error',
        };
      }
      
      return {
        success: false,
        error: error.response?.data || { message: 'Registration failed. Please check your data and try again.' },
        message: error.response?.data?.message || 'Registration failed',
      };
    }
  },

  // Admin creates new user
  async adminCreateUser(userData) {
    try {
      console.log('Admin creating user:', userData);
      const response = await api.post('/auth/admin/create-user/', userData);
      console.log('User creation response:', response.data);
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'User created successfully',
      };
    } catch (error) {
      console.error('Admin create user error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create user' },
        message: error.response?.data?.message || 'Failed to create user',
      };
    }
  },

  // Admin updates existing user
  async adminUpdateUser(userId, userData) {
    try {
      console.log('Admin updating user:', userId, userData);
      const response = await api.patch(`/auth/admin/update-user/${userId}/`, userData);
      console.log('User update response:', response.data);
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'User updated successfully',
      };
    } catch (error) {
      console.error('Admin update user error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update user' },
        message: error.response?.data?.message || 'Failed to update user',
      };
    }
  },

  // Login user
  async login(credentials) {
    try {
      console.log('Attempting login with credentials:', { username: credentials.username });
      console.log('Login API URL:', `${api.defaults.baseURL}/auth/login/`);
      
      // First, we need to add JWT login endpoint to Django backend
      // For now, let's assume the endpoint exists
      const response = await api.post('/auth/login/', credentials);
      console.log('Login response:', response.data);
      
      const { access, refresh, user } = response.data;
      
      // Store tokens
      await tokenStorage.setTokens(access, refresh);
      
      return {
        success: true,
        data: { user, access, refresh },
        message: 'Login successful',
      };
    } catch (error) {
      console.error('Login error:', error);
      console.error('Login error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config?.url,
      });
      
      return {
        success: false,
        error: error.response?.data || { message: 'Login failed' },
        message: error.response?.data?.message || 'Invalid credentials',
      };
    }
  },

  // Get current user profile
  async getCurrentUser() {
    try {
      const response = await api.get('/users/profile/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get current user error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get user data' },
      };
    }
  },

  // Update user profile
  async updateProfile(userData) {
    try {
      const response = await api.patch('/users/profile/', userData);
      return {
        success: true,
        data: response.data,
        message: 'Profile updated successfully',
      };
    } catch (error) {
      console.error('Update profile error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update profile' },
      };
    }
  },

  // Change password
  async changePassword(passwords) {
    try {
      const response = await api.post('/users/change_password/', passwords);
      return {
        success: true,
        data: response.data,
        message: 'Password changed successfully',
      };
    } catch (error) {
      console.error('Change password error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to change password' },
      };
    }
  },

  // Logout user
  async logout() {
    try {
      const refreshToken = await tokenStorage.getRefreshToken();
      
      // Call logout endpoint if it exists
      if (refreshToken) {
        try {
          await api.post('/auth/logout/', { refresh: refreshToken });
        } catch (logoutError) {
          console.error('Logout API error:', logoutError);
          // Continue with local logout even if API call fails
        }
      }
      
      // Clear tokens from storage
      await tokenStorage.clearTokens();
      
      return {
        success: true,
        message: 'Logged out successfully',
      };
    } catch (error) {
      console.error('Logout error:', error);
      return {
        success: false,
        error: { message: 'Logout failed' },
      };
    }
  },

  // Check if user is authenticated and get role info
  async isAuthenticated() {
    try {
      const token = await tokenStorage.getAccessToken();
      if (!token) {
        return { authenticated: false, user: null };
      }
      
      // Try to get current user info
      const userResult = await this.getCurrentUser();
      if (userResult.success) {
        return { 
          authenticated: true, 
          user: userResult.data,
          isAdmin: userResult.data.role === 'admin'
        };
      }
      
      return { authenticated: true, user: null };
    } catch (error) {
      console.error('Auth check error:', error);
      return { authenticated: false, user: null };
    }
  },

  // Get user list (admin only)
  async getUserList() {
    try {
      const response = await api.get('/users/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get user list error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get user list' },
      };
    }
  },

  // Delete user (admin only)
  async deleteUser(userId) {
    try {
      const response = await api.delete(`/users/${userId}/`);
      return {
        success: true,
        message: 'User deleted successfully',
      };
    } catch (error) {
      console.error('Delete user error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to delete user' },
      };
    }
  },

  // Refresh token
  async refreshToken() {
    try {
      const refreshToken = await tokenStorage.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await api.post('/auth/token/refresh/', {
        refresh: refreshToken,
      });

      const { access, refresh } = response.data;
      await tokenStorage.setTokens(access, refresh || refreshToken);

      return {
        success: true,
        data: { access, refresh },
      };
    } catch (error) {
      console.error('Token refresh error:', error);
      await tokenStorage.clearTokens();
      return {
        success: false,
        error: error.response?.data || { message: 'Token refresh failed' },
      };
    }
  },
};

export default authService;