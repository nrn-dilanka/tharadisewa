import api from '../services/api';

export const testAPI = {
  // Test basic connectivity
  async testConnection() {
    try {
      console.log('Testing API connection...');
      console.log('Base URL:', api.defaults.baseURL);
      
      // Try a simple health check or test endpoint
      const response = await api.get('/auth/test-connection/');
      
      console.log('Connection test successful:', response.data);
      return {
        success: true,
        data: response.data,
        message: 'Connection successful',
      };
    } catch (error) {
      console.error('Connection test failed:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config,
      });
      
      return {
        success: false,
        error: error.message,
        message: 'Connection failed',
      };
    }
  },

  // Test user registration endpoint
  async testRegistration() {
    try {
      console.log('Testing registration endpoint...');
      
      const testData = {
        username: 'testuser123',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        password: 'TestPass123',
        password_confirm: 'TestPass123',
        role: 'customer',
      };
      
      const response = await api.post('/auth/register/', testData);
      
      console.log('Registration test successful:', response.data);
      return {
        success: true,
        data: response.data,
        message: 'Registration endpoint working',
      };
    } catch (error) {
      console.error('Registration test failed:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config?.url,
      });
      
      return {
        success: false,
        error: error.response?.data || error.message,
        message: 'Registration endpoint failed',
      };
    }
  },
};

export default testAPI;