import api from './api';

export const productService = {
  // Get all products
  async getAllProducts() {
    try {
      const response = await api.get('/products/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get all products error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get products' },
      };
    }
  },

  // Get product by ID
  async getProduct(productId) {
    try {
      const response = await api.get(`/products/${productId}/`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get product error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get product' },
      };
    }
  },

  // Create new product
  async createProduct(productData) {
    try {
      const response = await api.post('/products/', productData);
      return {
        success: true,
        data: response.data,
        message: 'Product created successfully',
      };
    } catch (error) {
      console.error('Create product error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create product' },
        message: error.response?.data?.message || 'Failed to create product',
      };
    }
  },

  // Update product
  async updateProduct(productId, productData) {
    try {
      const response = await api.patch(`/products/${productId}/`, productData);
      return {
        success: true,
        data: response.data,
        message: 'Product updated successfully',
      };
    } catch (error) {
      console.error('Update product error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update product' },
        message: error.response?.data?.message || 'Failed to update product',
      };
    }
  },

  // Delete product
  async deleteProduct(productId) {
    try {
      await api.delete(`/products/${productId}/`);
      return {
        success: true,
        message: 'Product deleted successfully',
      };
    } catch (error) {
      console.error('Delete product error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to delete product' },
        message: error.response?.data?.message || 'Failed to delete product',
      };
    }
  },

  // Toggle product status
  async toggleProductStatus(productId) {
    try {
      const response = await api.post(`/products/${productId}/toggle_status/`);
      return {
        success: true,
        data: response.data,
        message: 'Product status updated successfully',
      };
    } catch (error) {
      console.error('Toggle product status error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to toggle product status' },
      };
    }
  },

  // Regenerate QR code
  async regenerateQRCode(productId) {
    try {
      const response = await api.post(`/products/${productId}/regenerate_qr_code/`);
      return {
        success: true,
        data: response.data,
        message: 'QR code regenerated successfully',
      };
    } catch (error) {
      console.error('Regenerate QR code error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to regenerate QR code' },
      };
    }
  },

  // Get product statistics
  async getProductStats() {
    try {
      const response = await api.get('/products/stats/');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get product stats error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to get product statistics' },
      };
    }
  },

  // Bulk create products
  async bulkCreateProducts(productsData) {
    try {
      const response = await api.post('/products/bulk_create/', productsData);
      return {
        success: true,
        data: response.data,
        message: 'Products created successfully',
      };
    } catch (error) {
      console.error('Bulk create products error:', error);
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to create products' },
      };
    }
  },
};

export default productService;