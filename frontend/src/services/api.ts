import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or Redux store
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login/', credentials),
  
  register: (userData: {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => api.post('/auth/register/', userData),
  
  refreshToken: (refresh: string) =>
    api.post('/auth/token/refresh/', { refresh }),
  
  logout: () => api.post('/auth/logout/'),
  
  getProfile: () => api.get('/auth/profile/'),
  
  updateProfile: (data: any) => api.put('/auth/profile/', data),
};

// Customer API
export const customerAPI = {
  getCustomers: (params?: { 
    page?: number; 
    search?: string; 
    limit?: number; 
  }) => api.get('/customers/', { params }),
  
  getCustomer: (id: number) => api.get(`/customers/${id}/`),
  
  createCustomer: (data: {
    name: string;
    email: string;
    phone: string;
    address: string;
  }) => api.post('/customers/', data),
  
  updateCustomer: (id: number, data: any) => api.put(`/customers/${id}/`, data),
  
  deleteCustomer: (id: number) => api.delete(`/customers/${id}/`),
};

// Product API
export const productAPI = {
  getProducts: (params?: { 
    page?: number; 
    search?: string; 
    category?: string; 
    limit?: number; 
  }) => api.get('/products/', { params }),
  
  getProduct: (id: number) => api.get(`/products/${id}/`),
  
  createProduct: (data: {
    name: string;
    description: string;
    price: string;
    quantity: number;
    category: string;
    sku: string;
  }) => api.post('/products/', data),
  
  updateProduct: (id: number, data: any) => api.put(`/products/${id}/`, data),
  
  deleteProduct: (id: number) => api.delete(`/products/${id}/`),
  
  updateQuantity: (id: number, quantity: number) =>
    api.patch(`/products/${id}/update_quantity/`, { quantity }),
};

// Purchase API
export const purchaseAPI = {
  getPurchases: (params?: { 
    page?: number; 
    search?: string; 
    date_from?: string;
    date_to?: string;
    limit?: number; 
  }) => api.get('/purchases/', { params }),
  
  getPurchase: (id: number) => api.get(`/purchases/${id}/`),
  
  createPurchase: (data: {
    purchase_date: string;
    supplier_name: string;
    notes?: string;
    items: Array<{
      product: number;
      quantity: number;
      unit_price: string;
    }>;
  }) => api.post('/purchases/', data),
  
  updatePurchase: (id: number, data: any) => api.put(`/purchases/${id}/`, data),
  
  deletePurchase: (id: number) => api.delete(`/purchases/${id}/`),
  
  getReports: (params?: {
    date_from?: string;
    date_to?: string;
    report_type?: 'summary' | 'detailed';
  }) => api.get('/purchases/reports/', { params }),
};

// Sales API
export const salesAPI = {
  getSales: (params?: { 
    page?: number; 
    search?: string; 
    date_from?: string;
    date_to?: string;
    limit?: number; 
  }) => api.get('/sales/', { params }),
  
  getSale: (id: number) => api.get(`/sales/${id}/`),
  
  createSale: (data: {
    sale_date: string;
    customer?: number;
    items: Array<{
      product: number;
      quantity: number;
      unit_price: string;
    }>;
  }) => api.post('/sales/', data),
  
  updateSale: (id: number, data: any) => api.put(`/sales/${id}/`, data),
  
  deleteSale: (id: number) => api.delete(`/sales/${id}/`),
  
  getReports: (params?: {
    date_from?: string;
    date_to?: string;
    report_type?: 'summary' | 'detailed';
  }) => api.get('/sales/reports/', { params }),
};

// Inventory API
export const inventoryAPI = {
  getInventory: (params?: { 
    page?: number; 
    search?: string; 
    low_stock?: boolean;
    limit?: number; 
  }) => api.get('/inventory/', { params }),
  
  getInventoryItem: (id: number) => api.get(`/inventory/${id}/`),
  
  updateStock: (id: number, data: {
    quantity: number;
    notes?: string;
  }) => api.patch(`/inventory/${id}/update_stock/`, data),
  
  getStockHistory: (productId: number, params?: {
    date_from?: string;
    date_to?: string;
  }) => api.get(`/inventory/stock-history/${productId}/`, { params }),
};

// Financial API
export const financialAPI = {
  getReports: (params?: {
    date_from?: string;
    date_to?: string;
    report_type?: 'summary' | 'detailed' | 'profit_loss' | 'cash_flow';
  }) => api.get('/financial/reports/', { params }),
  
  getExpenses: (params?: {
    page?: number;
    date_from?: string;
    date_to?: string;
    category?: string;
  }) => api.get('/financial/expenses/', { params }),
  
  createExpense: (data: {
    date: string;
    amount: string;
    description: string;
    category: string;
  }) => api.post('/financial/expenses/', data),
  
  updateExpense: (id: number, data: any) => api.put(`/financial/expenses/${id}/`, data),
  
  deleteExpense: (id: number) => api.delete(`/financial/expenses/${id}/`),
};

export default api;