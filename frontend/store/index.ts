import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import { StorageService } from '../services/api';

// Import reducers
import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';
import customerReducer from './slices/customerSlice';
import shopReducer from './slices/shopSlice';
import productReducer from './slices/productSlice';
import purchaseReducer from './slices/purchaseSlice';
import uiReducer from './slices/uiSlice';

const persistConfig = {
  key: 'root',
  storage: StorageService,
  whitelist: ['auth', 'ui'], // Only persist auth and ui state
};

const rootReducer = combineReducers({
  auth: authReducer,
  user: userReducer,
  customer: customerReducer,
  shop: shopReducer,
  product: productReducer,
  purchase: purchaseReducer,
  ui: uiReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;