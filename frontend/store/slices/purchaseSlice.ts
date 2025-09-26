import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../../services/api';

// Types
export interface PurchaseItem {
  id: number;
  product: {
    id: number;
    name: string;
    brand: string;
    model: string;
    price: string;
  };
  quantity: number;
  unit_price: string;
  total_price: string;
}

export interface Purchase {
  id: number;
  purchase_id: string;
  customer: {
    id: number;
    customer_id: string;
    user: {
      first_name: string;
      last_name: string;
      phone_number: string;
    };
  };
  shop: {
    id: number;
    name: string;
  };
  items: PurchaseItem[];
  total_amount: string;
  tax_amount: string;
  discount_amount: string;
  final_amount: string;
  payment_method: string;
  payment_status: string;
  notes?: string;
  purchase_date: string;
  created_at: string;
  updated_at: string;
}

export interface PurchaseState {
  purchases: Purchase[];
  currentPurchase: Purchase | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
    pageSize: number;
  };
  statistics: {
    totalSales: string;
    todaySales: string;
    monthSales: string;
    totalOrders: number;
    pendingOrders: number;
  };
}

const initialState: PurchaseState = {
  purchases: [],
  currentPurchase: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    totalPages: 0,
    totalCount: 0,
    pageSize: 10,
  },
  statistics: {
    totalSales: '0.00',
    todaySales: '0.00',
    monthSales: '0.00',
    totalOrders: 0,
    pendingOrders: 0,
  },
};

// Async Thunks
export const fetchPurchases = createAsyncThunk(
  'purchase/fetchPurchases',
  async (params: { 
    page?: number; 
    search?: string; 
    customer?: number;
    shop?: number;
    payment_status?: string;
    start_date?: string;
    end_date?: string;
  } = {}, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.search) queryParams.append('search', params.search);
      if (params.customer) queryParams.append('customer', params.customer.toString());
      if (params.shop) queryParams.append('shop', params.shop.toString());
      if (params.payment_status) queryParams.append('payment_status', params.payment_status);
      if (params.start_date) queryParams.append('start_date', params.start_date);
      if (params.end_date) queryParams.append('end_date', params.end_date);

      const response = await api.get(`/purchases/?${queryParams.toString()}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch purchases');
    }
  }
);

export const fetchPurchaseById = createAsyncThunk(
  'purchase/fetchPurchaseById',
  async (purchaseId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/purchases/${purchaseId}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch purchase');
    }
  }
);

export const createPurchase = createAsyncThunk(
  'purchase/createPurchase',
  async (purchaseData: {
    customer: number;
    shop: number;
    items: Array<{
      product: number;
      quantity: number;
      unit_price: string;
    }>;
    payment_method: string;
    discount_amount?: string;
    notes?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await api.post('/purchases/', purchaseData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to create purchase');
    }
  }
);

export const updatePurchase = createAsyncThunk(
  'purchase/updatePurchase',
  async ({ purchaseId, purchaseData }: { 
    purchaseId: number; 
    purchaseData: Partial<Purchase>
  }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/purchases/${purchaseId}/`, purchaseData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to update purchase');
    }
  }
);

export const deletePurchase = createAsyncThunk(
  'purchase/deletePurchase',
  async (purchaseId: number, { rejectWithValue }) => {
    try {
      await api.delete(`/purchases/${purchaseId}/`);
      return purchaseId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete purchase');
    }
  }
);

export const updatePaymentStatus = createAsyncThunk(
  'purchase/updatePaymentStatus',
  async ({ purchaseId, status }: { purchaseId: number; status: string }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/purchases/${purchaseId}/update-payment-status/`, {
        payment_status: status
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update payment status');
    }
  }
);

export const generateInvoice = createAsyncThunk(
  'purchase/generateInvoice',
  async (purchaseId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/purchases/${purchaseId}/generate-invoice/`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to generate invoice');
    }
  }
);

export const getPurchaseStatistics = createAsyncThunk(
  'purchase/getPurchaseStatistics',
  async (params: { shop?: number; period?: string } = {}, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.shop) queryParams.append('shop', params.shop.toString());
      if (params.period) queryParams.append('period', params.period);

      const response = await api.get(`/purchases/statistics/?${queryParams.toString()}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch purchase statistics');
    }
  }
);

export const searchPurchases = createAsyncThunk(
  'purchase/searchPurchases',
  async (searchTerm: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/purchases/search/?q=${encodeURIComponent(searchTerm)}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search purchases');
    }
  }
);

export const getCustomerPurchases = createAsyncThunk(
  'purchase/getCustomerPurchases',
  async (customerId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/purchases/customer/${customerId}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch customer purchases');
    }
  }
);

// Slice
const purchaseSlice = createSlice({
  name: 'purchase',
  initialState,
  reducers: {
    clearPurchaseError: (state) => {
      state.error = null;
    },
    clearPurchases: (state) => {
      state.purchases = [];
      state.pagination = initialState.pagination;
    },
    setCurrentPurchase: (state, action: PayloadAction<Purchase | null>) => {
      state.currentPurchase = action.payload;
    },
    updatePurchaseInList: (state, action: PayloadAction<Purchase>) => {
      const index = state.purchases.findIndex(purchase => purchase.id === action.payload.id);
      if (index !== -1) {
        state.purchases[index] = action.payload;
      }
    },
    addPurchaseToList: (state, action: PayloadAction<Purchase>) => {
      state.purchases.unshift(action.payload);
      state.pagination.totalCount += 1;
    },
    removePurchaseFromList: (state, action: PayloadAction<number>) => {
      state.purchases = state.purchases.filter(purchase => purchase.id !== action.payload);
      state.pagination.totalCount -= 1;
    },
  },
  extraReducers: (builder) => {
    // Fetch Purchases
    builder
      .addCase(fetchPurchases.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPurchases.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases = action.payload.results || action.payload;
        if (action.payload.count !== undefined) {
          state.pagination = {
            page: action.payload.page || 1,
            totalPages: Math.ceil(action.payload.count / (action.payload.page_size || 10)),
            totalCount: action.payload.count,
            pageSize: action.payload.page_size || 10,
          };
        }
      })
      .addCase(fetchPurchases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Fetch Purchase By ID
    builder
      .addCase(fetchPurchaseById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPurchaseById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPurchase = action.payload;
      })
      .addCase(fetchPurchaseById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Create Purchase
    builder
      .addCase(createPurchase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createPurchase.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases.unshift(action.payload);
        state.pagination.totalCount += 1;
      })
      .addCase(createPurchase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Purchase
    builder
      .addCase(updatePurchase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updatePurchase.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.purchases.findIndex(purchase => purchase.id === action.payload.id);
        if (index !== -1) {
          state.purchases[index] = action.payload;
        }
        if (state.currentPurchase?.id === action.payload.id) {
          state.currentPurchase = action.payload;
        }
      })
      .addCase(updatePurchase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete Purchase
    builder
      .addCase(deletePurchase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deletePurchase.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases = state.purchases.filter(purchase => purchase.id !== action.payload);
        state.pagination.totalCount -= 1;
        if (state.currentPurchase?.id === action.payload) {
          state.currentPurchase = null;
        }
      })
      .addCase(deletePurchase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Payment Status
    builder
      .addCase(updatePaymentStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updatePaymentStatus.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.purchases.findIndex(purchase => purchase.id === action.payload.id);
        if (index !== -1) {
          state.purchases[index] = action.payload;
        }
        if (state.currentPurchase?.id === action.payload.id) {
          state.currentPurchase = action.payload;
        }
      })
      .addCase(updatePaymentStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Generate Invoice
    builder
      .addCase(generateInvoice.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateInvoice.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(generateInvoice.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Purchase Statistics
    builder
      .addCase(getPurchaseStatistics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getPurchaseStatistics.fulfilled, (state, action) => {
        state.loading = false;
        state.statistics = action.payload;
      })
      .addCase(getPurchaseStatistics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Search Purchases
    builder
      .addCase(searchPurchases.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchPurchases.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases = action.payload;
      })
      .addCase(searchPurchases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Customer Purchases
    builder
      .addCase(getCustomerPurchases.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCustomerPurchases.fulfilled, (state, action) => {
        state.loading = false;
        // Could store in a separate field if needed
      })
      .addCase(getCustomerPurchases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearPurchaseError, 
  clearPurchases, 
  setCurrentPurchase, 
  updatePurchaseInList,
  addPurchaseToList,
  removePurchaseFromList
} = purchaseSlice.actions;

export default purchaseSlice.reducer;