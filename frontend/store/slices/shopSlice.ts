import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../../services/api';

// Types
export interface Shop {
  id: number;
  name: string;
  description: string;
  address: string;
  phone_number: string;
  email: string;
  owner_name: string;
  license_number: string;
  registration_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ShopState {
  shops: Shop[];
  currentShop: Shop | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
    pageSize: number;
  };
}

const initialState: ShopState = {
  shops: [],
  currentShop: null,
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
export const fetchShops = createAsyncThunk(
  'shop/fetchShops',
  async (params: { page?: number; search?: string; is_active?: boolean } = {}, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.search) queryParams.append('search', params.search);
      if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());

      const response = await api.get(`/shops/?${queryParams.toString()}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch shops');
    }
  }
);

export const fetchShopById = createAsyncThunk(
  'shop/fetchShopById',
  async (shopId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/shops/${shopId}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch shop');
    }
  }
);

export const createShop = createAsyncThunk(
  'shop/createShop',
  async (shopData: Partial<Shop>, { rejectWithValue }) => {
    try {
      const response = await api.post('/shops/', shopData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to create shop');
    }
  }
);

export const updateShop = createAsyncThunk(
  'shop/updateShop',
  async ({ shopId, shopData }: { shopId: number; shopData: Partial<Shop> }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/shops/${shopId}/`, shopData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to update shop');
    }
  }
);

export const deleteShop = createAsyncThunk(
  'shop/deleteShop',
  async (shopId: number, { rejectWithValue }) => {
    try {
      await api.delete(`/shops/${shopId}/`);
      return shopId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete shop');
    }
  }
);

export const toggleShopStatus = createAsyncThunk(
  'shop/toggleShopStatus',
  async (shopId: number, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/shops/${shopId}/toggle-status/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to toggle shop status');
    }
  }
);

export const searchShops = createAsyncThunk(
  'shop/searchShops',
  async (searchTerm: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/shops/search/?q=${encodeURIComponent(searchTerm)}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search shops');
    }
  }
);

export const getShopProducts = createAsyncThunk(
  'shop/getShopProducts',
  async (shopId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/shops/${shopId}/products/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch shop products');
    }
  }
);

export const getShopServices = createAsyncThunk(
  'shop/getShopServices',
  async (shopId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/shops/${shopId}/services/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch shop services');
    }
  }
);

export const getShopStatistics = createAsyncThunk(
  'shop/getShopStatistics',
  async (shopId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/shops/${shopId}/statistics/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch shop statistics');
    }
  }
);

// Slice
const shopSlice = createSlice({
  name: 'shop',
  initialState,
  reducers: {
    clearShopError: (state) => {
      state.error = null;
    },
    clearShops: (state) => {
      state.shops = [];
      state.pagination = initialState.pagination;
    },
    setCurrentShop: (state, action: PayloadAction<Shop | null>) => {
      state.currentShop = action.payload;
    },
    updateShopInList: (state, action: PayloadAction<Shop>) => {
      const index = state.shops.findIndex(shop => shop.id === action.payload.id);
      if (index !== -1) {
        state.shops[index] = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    // Fetch Shops
    builder
      .addCase(fetchShops.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchShops.fulfilled, (state, action) => {
        state.loading = false;
        state.shops = action.payload.results || action.payload;
        if (action.payload.count !== undefined) {
          state.pagination = {
            page: action.payload.page || 1,
            totalPages: Math.ceil(action.payload.count / (action.payload.page_size || 10)),
            totalCount: action.payload.count,
            pageSize: action.payload.page_size || 10,
          };
        }
      })
      .addCase(fetchShops.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Fetch Shop By ID
    builder
      .addCase(fetchShopById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchShopById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentShop = action.payload;
      })
      .addCase(fetchShopById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Create Shop
    builder
      .addCase(createShop.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createShop.fulfilled, (state, action) => {
        state.loading = false;
        state.shops.unshift(action.payload);
        state.pagination.totalCount += 1;
      })
      .addCase(createShop.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Shop
    builder
      .addCase(updateShop.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateShop.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.shops.findIndex(shop => shop.id === action.payload.id);
        if (index !== -1) {
          state.shops[index] = action.payload;
        }
        if (state.currentShop?.id === action.payload.id) {
          state.currentShop = action.payload;
        }
      })
      .addCase(updateShop.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete Shop
    builder
      .addCase(deleteShop.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteShop.fulfilled, (state, action) => {
        state.loading = false;
        state.shops = state.shops.filter(shop => shop.id !== action.payload);
        state.pagination.totalCount -= 1;
        if (state.currentShop?.id === action.payload) {
          state.currentShop = null;
        }
      })
      .addCase(deleteShop.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Toggle Shop Status
    builder
      .addCase(toggleShopStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(toggleShopStatus.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.shops.findIndex(shop => shop.id === action.payload.id);
        if (index !== -1) {
          state.shops[index] = action.payload;
        }
        if (state.currentShop?.id === action.payload.id) {
          state.currentShop = action.payload;
        }
      })
      .addCase(toggleShopStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Search Shops
    builder
      .addCase(searchShops.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchShops.fulfilled, (state, action) => {
        state.loading = false;
        state.shops = action.payload;
      })
      .addCase(searchShops.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Shop Products
    builder
      .addCase(getShopProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getShopProducts.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(getShopProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Shop Services
    builder
      .addCase(getShopServices.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getShopServices.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(getShopServices.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Shop Statistics
    builder
      .addCase(getShopStatistics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getShopStatistics.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(getShopStatistics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearShopError, 
  clearShops, 
  setCurrentShop, 
  updateShopInList 
} = shopSlice.actions;

export default shopSlice.reducer;