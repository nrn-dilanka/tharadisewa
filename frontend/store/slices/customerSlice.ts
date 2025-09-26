import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../../services/api';

// Types
export interface Customer {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    phone_number: string;
  };
  customer_id: string;
  address: string;
  date_of_birth?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface CustomerState {
  customers: Customer[];
  currentCustomer: Customer | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
    pageSize: number;
  };
}

const initialState: CustomerState = {
  customers: [],
  currentCustomer: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    totalPages: 0,
    totalCount: 0,
    pageSize: 10,
  },
};

// Async Thunks
export const fetchCustomers = createAsyncThunk(
  'customer/fetchCustomers',
  async (params: { page?: number; search?: string; is_active?: boolean } = {}, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.search) queryParams.append('search', params.search);
      if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());

      const response = await api.get(`/customers/?${queryParams.toString()}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch customers');
    }
  }
);

export const fetchCustomerById = createAsyncThunk(
  'customer/fetchCustomerById',
  async (customerId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/customers/${customerId}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch customer');
    }
  }
);

export const createCustomer = createAsyncThunk(
  'customer/createCustomer',
  async (customerData: {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone_number: string;
    address: string;
    date_of_birth?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await api.post('/customers/', customerData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to create customer');
    }
  }
);

export const updateCustomer = createAsyncThunk(
  'customer/updateCustomer',
  async ({ customerId, customerData }: { 
    customerId: number; 
    customerData: {
      first_name?: string;
      last_name?: string;
      email?: string;
      phone_number?: string;
      address?: string;
      date_of_birth?: string;
    }
  }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/customers/${customerId}/`, customerData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to update customer');
    }
  }
);

export const deleteCustomer = createAsyncThunk(
  'customer/deleteCustomer',
  async (customerId: number, { rejectWithValue }) => {
    try {
      await api.delete(`/customers/${customerId}/`);
      return customerId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete customer');
    }
  }
);

export const toggleCustomerStatus = createAsyncThunk(
  'customer/toggleCustomerStatus',
  async (customerId: number, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/customers/${customerId}/toggle-status/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to toggle customer status');
    }
  }
);

export const searchCustomers = createAsyncThunk(
  'customer/searchCustomers',
  async (searchTerm: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/customers/search/?q=${encodeURIComponent(searchTerm)}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search customers');
    }
  }
);

export const getCustomerPurchases = createAsyncThunk(
  'customer/getCustomerPurchases',
  async (customerId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/customers/${customerId}/purchases/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch customer purchases');
    }
  }
);

export const getCustomerServices = createAsyncThunk(
  'customer/getCustomerServices',
  async (customerId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/customers/${customerId}/services/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch customer services');
    }
  }
);

// Slice
const customerSlice = createSlice({
  name: 'customer',
  initialState,
  reducers: {
    clearCustomerError: (state) => {
      state.error = null;
    },
    clearCustomers: (state) => {
      state.customers = [];
      state.pagination = initialState.pagination;
    },
    setCurrentCustomer: (state, action: PayloadAction<Customer | null>) => {
      state.currentCustomer = action.payload;
    },
    updateCustomerInList: (state, action: PayloadAction<Customer>) => {
      const index = state.customers.findIndex(customer => customer.id === action.payload.id);
      if (index !== -1) {
        state.customers[index] = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    // Fetch Customers
    builder
      .addCase(fetchCustomers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCustomers.fulfilled, (state, action) => {
        state.loading = false;
        state.customers = action.payload.results || action.payload;
        if (action.payload.count !== undefined) {
          state.pagination = {
            page: action.payload.page || 1,
            totalPages: Math.ceil(action.payload.count / (action.payload.page_size || 10)),
            totalCount: action.payload.count,
            pageSize: action.payload.page_size || 10,
          };
        }
      })
      .addCase(fetchCustomers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Fetch Customer By ID
    builder
      .addCase(fetchCustomerById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCustomerById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCustomer = action.payload;
      })
      .addCase(fetchCustomerById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Create Customer
    builder
      .addCase(createCustomer.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createCustomer.fulfilled, (state, action) => {
        state.loading = false;
        state.customers.unshift(action.payload);
        state.pagination.totalCount += 1;
      })
      .addCase(createCustomer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Customer
    builder
      .addCase(updateCustomer.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateCustomer.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.customers.findIndex(customer => customer.id === action.payload.id);
        if (index !== -1) {
          state.customers[index] = action.payload;
        }
        if (state.currentCustomer?.id === action.payload.id) {
          state.currentCustomer = action.payload;
        }
      })
      .addCase(updateCustomer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete Customer
    builder
      .addCase(deleteCustomer.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteCustomer.fulfilled, (state, action) => {
        state.loading = false;
        state.customers = state.customers.filter(customer => customer.id !== action.payload);
        state.pagination.totalCount -= 1;
        if (state.currentCustomer?.id === action.payload) {
          state.currentCustomer = null;
        }
      })
      .addCase(deleteCustomer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Toggle Customer Status
    builder
      .addCase(toggleCustomerStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(toggleCustomerStatus.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.customers.findIndex(customer => customer.id === action.payload.id);
        if (index !== -1) {
          state.customers[index] = action.payload;
        }
        if (state.currentCustomer?.id === action.payload.id) {
          state.currentCustomer = action.payload;
        }
      })
      .addCase(toggleCustomerStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Search Customers
    builder
      .addCase(searchCustomers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchCustomers.fulfilled, (state, action) => {
        state.loading = false;
        state.customers = action.payload;
      })
      .addCase(searchCustomers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Customer Purchases
    builder
      .addCase(getCustomerPurchases.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCustomerPurchases.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(getCustomerPurchases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Customer Services
    builder
      .addCase(getCustomerServices.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCustomerServices.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(getCustomerServices.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearCustomerError, 
  clearCustomers, 
  setCurrentCustomer, 
  updateCustomerInList 
} = customerSlice.actions;

export default customerSlice.reducer;