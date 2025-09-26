import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Platform } from 'react-native';

// Storage abstraction for web/native compatibility
class StorageService {
  static async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    } else {
      // For native, you would import AsyncStorage here
      // For now, using localStorage as fallback
      return localStorage.getItem(key);
    }
  }

  static async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
    } else {
      // For native, you would import AsyncStorage here
      // For now, using localStorage as fallback
      localStorage.setItem(key, value);
    }
  }

  static async removeItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
    } else {
      // For native, you would import AsyncStorage here
      // For now, using localStorage as fallback
      localStorage.removeItem(key);
    }
  }
}

// API Configuration
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiService {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.instance.interceptors.request.use(
      async (config) => {
        const token = await StorageService.getItem('access_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = await StorageService.getItem('refresh_token');
            
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
                refresh: refreshToken,
              });

              const { access } = response.data;
              await StorageService.setItem('access_token', access);

              // Retry the original request with new token
              originalRequest.headers.Authorization = `Bearer ${access}`;
              return this.instance(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            await StorageService.removeItem('access_token');
            await StorageService.removeItem('refresh_token');
            
            // Dispatch logout action if store is available
            if (typeof window !== 'undefined' && (window as any).store) {
              (window as any).store.dispatch({ type: 'auth/clearAuth' });
            }
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // HTTP Methods
  get<T = any>(url: string, config?: any): Promise<AxiosResponse<T>> {
    return this.instance.get(url, config);
  }

  post<T = any>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.instance.post(url, data, config);
  }

  put<T = any>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.instance.put(url, data, config);
  }

  patch<T = any>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.instance.patch(url, data, config);
  }

  delete<T = any>(url: string, config?: any): Promise<AxiosResponse<T>> {
    return this.instance.delete(url, config);
  }

  // File upload
  upload<T = any>(url: string, formData: FormData, config?: any): Promise<AxiosResponse<T>> {
    return this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
    });
  }
}

// Export singleton instance
export const api = new ApiService();
export { StorageService };