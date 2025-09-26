import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface PurchaseItem {
  id?: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: string;
  total_price?: string;
}

interface Purchase {
  id: number;
  purchase_date: string;
  supplier_name: string;
  total_amount: string;
  notes?: string;
  items: PurchaseItem[];
  created_at: string;
  updated_at: string;
}

interface PurchaseState {
  purchases: Purchase[];
  currentPurchase: Purchase | null;
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  hasNextPage: boolean;
}

const initialState: PurchaseState = {
  purchases: [],
  currentPurchase: null,
  isLoading: false,
  error: null,
  totalCount: 0,
  hasNextPage: false,
};

// Async thunks for purchase operations
export const fetchPurchases = createAsyncThunk(
  'purchases/fetchPurchases',
  async (params: { page?: number; search?: string; date_from?: string; date_to?: string; limit?: number } = {}, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: { token: string } };
      const token = state.auth.token;

      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.search) queryParams.append('search', params.search);
      if (params.date_from) queryParams.append('date_from', params.date_from);
      if (params.date_to) queryParams.append('date_to', params.date_to);
      if (params.limit) queryParams.append('limit', params.limit.toString());

      const response = await fetch(`http://localhost:8000/api/purchases/?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.message || 'Failed to fetch purchases');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue('Network error occurred');
    }
  }
);

export const fetchPurchaseById = createAsyncThunk(
  'purchases/fetchPurchaseById',
  async (id: number, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: { token: string } };
      const token = state.auth.token;

      const response = await fetch(`http://localhost:8000/api/purchases/${id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.message || 'Failed to fetch purchase');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue('Network error occurred');
    }
  }
);

export const createPurchase = createAsyncThunk(
  'purchases/createPurchase',
  async (purchaseData: {
    purchase_date: string;
    supplier_name: string;
    notes?: string;
    items: Omit<PurchaseItem, 'id' | 'total_price'>[];
  }, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: { token: string } };
      const token = state.auth.token;

      const response = await fetch('http://localhost:8000/api/purchases/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(purchaseData),
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.message || 'Failed to create purchase');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue('Network error occurred');
    }
  }
);

export const updatePurchase = createAsyncThunk(
  'purchases/updatePurchase',
  async ({ id, purchaseData }: { 
    id: number; 
    purchaseData: Partial<Purchase> 
  }, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: { token: string } };
      const token = state.auth.token;

      const response = await fetch(`http://localhost:8000/api/purchases/${id}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(purchaseData),
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.message || 'Failed to update purchase');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue('Network error occurred');
    }
  }
);

export const deletePurchase = createAsyncThunk(
  'purchases/deletePurchase',
  async (id: number, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: { token: string } };
      const token = state.auth.token;

      const response = await fetch(`http://localhost:8000/api/purchases/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.message || 'Failed to delete purchase');
      }

      return id;
    } catch (error) {
      return rejectWithValue('Network error occurred');
    }
  }
);

export const fetchPurchaseReports = createAsyncThunk(
  'purchases/fetchReports',
  async (params: { 
    date_from?: string; 
    date_to?: string; 
    report_type?: 'summary' | 'detailed' 
  } = {}, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: { token: string } };
      const token = state.auth.token;

      const queryParams = new URLSearchParams();
      if (params.date_from) queryParams.append('date_from', params.date_from);
      if (params.date_to) queryParams.append('date_to', params.date_to);
      if (params.report_type) queryParams.append('report_type', params.report_type);

      const response = await fetch(`http://localhost:8000/api/purchases/reports/?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.message || 'Failed to fetch purchase reports');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue('Network error occurred');
    }
  }
);

const purchaseSlice = createSlice({
  name: 'purchases',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentPurchase: (state, action: PayloadAction<Purchase | null>) => {
      state.currentPurchase = action.payload;
    },
    clearPurchases: (state) => {
      state.purchases = [];
      state.totalCount = 0;
      state.hasNextPage = false;
    },
    addPurchaseItem: (state, action: PayloadAction<PurchaseItem>) => {
      if (state.currentPurchase) {
        state.currentPurchase.items.push(action.payload);
      }
    },
    removePurchaseItem: (state, action: PayloadAction<number>) => {
      if (state.currentPurchase) {
        state.currentPurchase.items = state.currentPurchase.items.filter(
          (_: PurchaseItem, index: number) => index !== action.payload
        );
      }
    },
    updatePurchaseItem: (state, action: PayloadAction<{ index: number; item: PurchaseItem }>) => {
      if (state.currentPurchase) {
        const { index, item } = action.payload;
        if (state.currentPurchase.items[index]) {
          state.currentPurchase.items[index] = item;
        }
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch purchases
      .addCase(fetchPurchases.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPurchases.fulfilled, (state, action) => {
        state.isLoading = false;
        state.purchases = action.payload.results || action.payload;
        state.totalCount = action.payload.count || action.payload.length;
        state.hasNextPage = !!action.payload.next;
        state.error = null;
      })
      .addCase(fetchPurchases.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch purchase by ID
      .addCase(fetchPurchaseById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPurchaseById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentPurchase = action.payload;
        state.error = null;
      })
      .addCase(fetchPurchaseById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Create purchase
      .addCase(createPurchase.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createPurchase.fulfilled, (state, action) => {
        state.isLoading = false;
        state.purchases.unshift(action.payload);
        state.totalCount += 1;
        state.error = null;
      })
      .addCase(createPurchase.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update purchase
      .addCase(updatePurchase.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updatePurchase.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.purchases.findIndex((purchase: Purchase) => purchase.id === action.payload.id);
        if (index !== -1) {
          state.purchases[index] = action.payload;
        }
        if (state.currentPurchase?.id === action.payload.id) {
          state.currentPurchase = action.payload;
        }
        state.error = null;
      })
      .addCase(updatePurchase.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Delete purchase
      .addCase(deletePurchase.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deletePurchase.fulfilled, (state, action) => {
        state.isLoading = false;
        state.purchases = state.purchases.filter((purchase: Purchase) => purchase.id !== action.payload);
        if (state.currentPurchase?.id === action.payload) {
          state.currentPurchase = null;
        }
        state.totalCount = Math.max(0, state.totalCount - 1);
        state.error = null;
      })
      .addCase(deletePurchase.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch purchase reports
      .addCase(fetchPurchaseReports.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPurchaseReports.fulfilled, (state) => {
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchPurchaseReports.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearError, 
  setCurrentPurchase, 
  clearPurchases, 
  addPurchaseItem, 
  removePurchaseItem, 
  updatePurchaseItem 
} = purchaseSlice.actions;
export default purchaseSlice.reducer;