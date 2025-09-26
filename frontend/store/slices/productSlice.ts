import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../../services/api';

// Types
export interface Product {
  id: number;
  name: string;
  brand: string;
  model: string;
  category: string;
  description: string;
  price: string;
  stock_quantity: number;
  sku: string;
  barcode?: string;
  warranty_period: number;
  shop: {
    id: number;
    name: string;
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductState {
  products: Product[];
  currentProduct: Product | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
    pageSize: number;
  };
  categories: string[];
  brands: string[];
}

const initialState: ProductState = {
  products: [],
  currentProduct: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    totalPages: 0,
    totalCount: 0,
    pageSize: 10,
  },
  categories: [],
  brands: [],
};

// Async Thunks
export const fetchProducts = createAsyncThunk(
  'product/fetchProducts',
  async (params: { 
    page?: number; 
    search?: string; 
    category?: string;
    brand?: string;
    shop?: number;
    is_active?: boolean;
    min_price?: number;
    max_price?: number;
  } = {}, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.search) queryParams.append('search', params.search);
      if (params.category) queryParams.append('category', params.category);
      if (params.brand) queryParams.append('brand', params.brand);
      if (params.shop) queryParams.append('shop', params.shop.toString());
      if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());
      if (params.min_price) queryParams.append('min_price', params.min_price.toString());
      if (params.max_price) queryParams.append('max_price', params.max_price.toString());

      const response = await api.get(`/products/?${queryParams.toString()}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch products');
    }
  }
);

export const fetchProductById = createAsyncThunk(
  'product/fetchProductById',
  async (productId: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/products/${productId}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch product');
    }
  }
);

export const createProduct = createAsyncThunk(
  'product/createProduct',
  async (productData: Partial<Product>, { rejectWithValue }) => {
    try {
      const response = await api.post('/products/', productData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to create product');
    }
  }
);

export const updateProduct = createAsyncThunk(
  'product/updateProduct',
  async ({ productId, productData }: { productId: number; productData: Partial<Product> }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/products/${productId}/`, productData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Failed to update product');
    }
  }
);

export const deleteProduct = createAsyncThunk(
  'product/deleteProduct',
  async (productId: number, { rejectWithValue }) => {
    try {
      await api.delete(`/products/${productId}/`);
      return productId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete product');
    }
  }
);

export const toggleProductStatus = createAsyncThunk(
  'product/toggleProductStatus',
  async (productId: number, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/products/${productId}/toggle-status/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to toggle product status');
    }
  }
);

export const updateStock = createAsyncThunk(
  'product/updateStock',
  async ({ productId, quantity, operation }: { productId: number; quantity: number; operation: 'add' | 'subtract' }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/products/${productId}/update-stock/`, {
        quantity,
        operation
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update stock');
    }
  }
);

export const searchProducts = createAsyncThunk(
  'product/searchProducts',
  async (searchTerm: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/products/search/?q=${encodeURIComponent(searchTerm)}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search products');
    }
  }
);

export const getProductCategories = createAsyncThunk(
  'product/getProductCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/products/categories/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch categories');
    }
  }
);

export const getProductBrands = createAsyncThunk(
  'product/getProductBrands',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/products/brands/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch brands');
    }
  }
);

export const getLowStockProducts = createAsyncThunk(
  'product/getLowStockProducts',
  async (threshold: number = 10, { rejectWithValue }) => {
    try {
      const response = await api.get(`/products/low-stock/?threshold=${threshold}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch low stock products');
    }
  }
);

// Slice
const productSlice = createSlice({
  name: 'product',
  initialState,
  reducers: {
    clearProductError: (state) => {
      state.error = null;
    },
    clearProducts: (state) => {
      state.products = [];
      state.pagination = initialState.pagination;
    },
    setCurrentProduct: (state, action: PayloadAction<Product | null>) => {
      state.currentProduct = action.payload;
    },
    updateProductInList: (state, action: PayloadAction<Product>) => {
      const index = state.products.findIndex(product => product.id === action.payload.id);
      if (index !== -1) {
        state.products[index] = action.payload;
      }
    },
    addProductToList: (state, action: PayloadAction<Product>) => {
      state.products.unshift(action.payload);
      state.pagination.totalCount += 1;
    },
    removeProductFromList: (state, action: PayloadAction<number>) => {
      state.products = state.products.filter(product => product.id !== action.payload);
      state.pagination.totalCount -= 1;
    },
  },
  extraReducers: (builder) => {
    // Fetch Products
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload.results || action.payload;
        if (action.payload.count !== undefined) {
          state.pagination = {
            page: action.payload.page || 1,
            totalPages: Math.ceil(action.payload.count / (action.payload.page_size || 10)),
            totalCount: action.payload.count,
            pageSize: action.payload.page_size || 10,
          };
        }
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Fetch Product By ID
    builder
      .addCase(fetchProductById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProduct = action.payload;
      })
      .addCase(fetchProductById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Create Product
    builder
      .addCase(createProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.products.unshift(action.payload);
        state.pagination.totalCount += 1;
      })
      .addCase(createProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Product
    builder
      .addCase(updateProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProduct.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.products.findIndex(product => product.id === action.payload.id);
        if (index !== -1) {
          state.products[index] = action.payload;
        }
        if (state.currentProduct?.id === action.payload.id) {
          state.currentProduct = action.payload;
        }
      })
      .addCase(updateProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete Product
    builder
      .addCase(deleteProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.products = state.products.filter(product => product.id !== action.payload);
        state.pagination.totalCount -= 1;
        if (state.currentProduct?.id === action.payload) {
          state.currentProduct = null;
        }
      })
      .addCase(deleteProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Toggle Product Status
    builder
      .addCase(toggleProductStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(toggleProductStatus.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.products.findIndex(product => product.id === action.payload.id);
        if (index !== -1) {
          state.products[index] = action.payload;
        }
        if (state.currentProduct?.id === action.payload.id) {
          state.currentProduct = action.payload;
        }
      })
      .addCase(toggleProductStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Stock
    builder
      .addCase(updateStock.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateStock.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.products.findIndex(product => product.id === action.payload.id);
        if (index !== -1) {
          state.products[index] = action.payload;
        }
        if (state.currentProduct?.id === action.payload.id) {
          state.currentProduct = action.payload;
        }
      })
      .addCase(updateStock.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Search Products
    builder
      .addCase(searchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(searchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Get Product Categories
    builder
      .addCase(getProductCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      });

    // Get Product Brands
    builder
      .addCase(getProductBrands.fulfilled, (state, action) => {
        state.brands = action.payload;
      });

    // Get Low Stock Products
    builder
      .addCase(getLowStockProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getLowStockProducts.fulfilled, (state, action) => {
        state.loading = false;
        // Could store in a separate field if needed
      })
      .addCase(getLowStockProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearProductError, 
  clearProducts, 
  setCurrentProduct, 
  updateProductInList,
  addProductToList,
  removeProductFromList
} = productSlice.actions;

export default productSlice.reducer;