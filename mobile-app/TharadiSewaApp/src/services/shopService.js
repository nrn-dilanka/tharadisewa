import api from './api';

export const shopService = {
  // Get all shops
  async getAllShops() {
    try {
      const response = await api.get('/shops/');
      console.log('Get all shops response:', response);
      console.log('Response data structure:', response.data);
      console.log('Shops data:', response.data?.data);
      console.log('Shops results:', response.data?.data?.results);
      
      return {
        success: true,
        data: response.data?.data || response.data, // Handle nested response structure
      };
    } catch (error) {
      console.error('Get all shops error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get shops' },
      };
    }
  },

  // Get shop by ID
  async getShop(shopId) {
    try {
      const response = await api.get(`/shops/${shopId}/`);
      console.log('Get shop response:', response.data);
      return {
        success: true,
        data: response.data?.data || response.data,
      };
    } catch (error) {
      console.error('Get shop error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get shop' },
      };
    }
  },

  // Create new shop
  async createShop(shopData) {
    try {
      const response = await api.post('/shops/', shopData);
      console.log('Create shop response:', response.data);
      return {
        success: true,
        data: response.data?.data || response.data,
        message: response.data?.message || 'Shop created successfully',
      };
    } catch (error) {
      console.error('Create shop error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create shop' },
        message: error.response?.data?.message || 'Failed to create shop',
      };
    }
  },

  // Update shop
  async updateShop(shopId, shopData) {
    try {
      const response = await api.patch(`/shops/${shopId}/`, shopData);
      console.log('Update shop response:', response.data);
      return {
        success: true,
        data: response.data?.data || response.data,
        message: response.data?.message || 'Shop updated successfully',
      };
    } catch (error) {
      console.error('Update shop error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update shop' },
        message: error.response?.data?.message || 'Failed to update shop',
      };
    }
  },

  // Delete shop
  async deleteShop(shopId) {
    try {
      await api.delete(`/shops/${shopId}/`);
      return {
        success: true,
        message: 'Shop deleted successfully',
      };
    } catch (error) {
      console.error('Delete shop error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to delete shop' },
        message: error.response?.data?.message || 'Failed to delete shop',
      };
    }
  },

  // Get shops by customer
  async getShopsByCustomer(customerId) {
    try {
      const response = await api.get(`/customers/${customerId}/shops/`);
      console.log('Get shops by customer response:', response.data);
      return {
        success: true,
        data: response.data?.data || response.data,
      };
    } catch (error) {
      console.error('Get shops by customer error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get customer shops' },
      };
    }
  },

  // Get customers with shops
  async getCustomersWithShops() {
    try {
      const response = await api.get('/customers-with-shops/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get customers with shops error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get customers with shops' },
      };
    }
  },

  // Toggle shop status
  async toggleShopStatus(shopId) {
    try {
      const response = await api.post(`/shops/${shopId}/toggle-status/`);
      return {
        success: true,
        data: response.data,
        message: 'Shop status updated successfully',
      };
    } catch (error) {
      console.error('Toggle shop status error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to toggle shop status' },
      };
    }
  },

  // Get shops by city
  async getShopsByCity(cityName) {
    try {
      const response = await api.get(`/shops/city/${cityName}/`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get shops by city error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get shops by city' },
      };
    }
  },

  // Get shops by postal code
  async getShopsByPostalCode(postalCode) {
    try {
      const response = await api.get(`/shops/postal-code/${postalCode}/`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get shops by postal code error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get shops by postal code' },
      };
    }
  },

  // Get shop statistics
  async getShopStats() {
    try {
      const response = await api.get('/shops/stats/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get shop stats error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get shop statistics' },
      };
    }
  },

  // Bulk create shops
  async bulkCreateShops(shopsData) {
    try {
      const response = await api.post('/shops/bulk-create/', shopsData);
      return {
        success: true,
        data: response.data,
        message: 'Shops created successfully',
      };
    } catch (error) {
      console.error('Bulk create shops error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create shops' },
      };
    }
  },

  // Get shops with locations
  async getShopsWithLocations() {
    try {
      const response = await api.get('/shops-with-locations/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get shops with locations error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get shops with locations' },
      };
    }
  },
};

export default shopService;