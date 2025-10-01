import api from './api';

export const customerService = {
  // Get all customers
  async getAllCustomers() {
    try {
      const response = await api.get('/customers/');
      console.log('Get all customers response:', response.data.results);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get all customers error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get customers' },
      };
    }
  },

  // Get customer by ID
  async getCustomer(customerId) {
    try {
      const response = await api.get(`/customers/${customerId}/`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get customer error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get customer' },
      };
    }
  },

  // Create new customer
  async createCustomer(customerData) {
    try {
      const response = await api.post('/customers/', customerData);
      return {
        success: true,
        data: response.data,
        message: 'Customer created successfully',
      };
    } catch (error) {
      console.error('Create customer error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create customer' },
        message: error.response?.data?.message || 'Failed to create customer',
      };
    }
  },

  // Update customer
  async updateCustomer(customerId, customerData) {
    try {
      const response = await api.patch(`/customers/${customerId}/`, customerData);
      return {
        success: true,
        data: response.data,
        message: 'Customer updated successfully',
      };
    } catch (error) {
      console.error('Update customer error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update customer' },
        message: error.response?.data?.message || 'Failed to update customer',
      };
    }
  },

  // Delete customer
  async deleteCustomer(customerId) {
    try {
      await api.delete(`/customers/${customerId}/`);
      return {
        success: true,
        message: 'Customer deleted successfully',
      };
    } catch (error) {
      console.error('Delete customer error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to delete customer' },
        message: error.response?.data?.message || 'Failed to delete customer',
      };
    }
  },

  // Get customer statistics
  async getCustomerStats() {
    try {
      const response = await api.get('/customers/statistics/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get customer stats error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get customer statistics' },
      };
    }
  },

  // Get verified customers
  async getVerifiedCustomers() {
    try {
      const response = await api.get('/customers/verified/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get verified customers error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get verified customers' },
      };
    }
  },

  // Get unverified customers
  async getUnverifiedCustomers() {
    try {
      const response = await api.get('/customers/unverified/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get unverified customers error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get unverified customers' },
      };
    }
  },

  // Verify customer
  async verifyCustomer(customerId) {
    try {
      const response = await api.post(`/customers/${customerId}/verify/`);
      return {
        success: true,
        data: response.data,
        message: 'Customer verified successfully',
      };
    } catch (error) {
      console.error('Verify customer error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to verify customer' },
      };
    }
  },

  // Activate/Deactivate customer
  async toggleCustomerStatus(customerId) {
    try {
      const response = await api.post(`/customers/${customerId}/activate/`);
      return {
        success: true,
        data: response.data,
        message: 'Customer status updated successfully',
      };
    } catch (error) {
      console.error('Toggle customer status error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update customer status' },
      };
    }
  },

  // Create user account for customer
  async createUserAccount(customerId, userData) {
    try {
      const response = await api.post(`/customers/${customerId}/create_user_account/`, userData);
      return {
        success: true,
        data: response.data,
        message: 'User account created successfully',
      };
    } catch (error) {
      console.error('Create user account error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create user account' },
      };
    }
  },

  // Export customers
  async exportCustomers() {
    try {
      const response = await api.get('/customers/export/', {
        responseType: 'blob',
      });
      return {
        success: true,
        data: response.data,
        message: 'Customers exported successfully',
      };
    } catch (error) {
      console.error('Export customers error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to export customers' },
      };
    }
  },

  // Bulk operations
  async bulkOperations(operation, customerIds) {
    try {
      const response = await api.post('/customers/bulk_operations/', {
        operation,
        customer_ids: customerIds,
      });
      return {
        success: true,
        data: response.data,
        message: `Bulk ${operation} completed successfully`,
      };
    } catch (error) {
      console.error('Bulk operations error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to perform bulk operations' },
      };
    }
  },
};

export default customerService;