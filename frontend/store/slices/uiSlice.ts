import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Types
export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  timestamp: number;
}

export interface ModalState {
  isOpen: boolean;
  type: string;
  data?: any;
}

export interface UIState {
  // Navigation
  sidebarOpen: boolean;
  currentScreen: string;
  
  // Loading states
  globalLoading: boolean;
  loadingMessage?: string;
  
  // Notifications
  notifications: NotificationState[];
  
  // Modals
  modal: ModalState;
  
  // Theme
  theme: 'light' | 'dark';
  
  // Network
  isOnline: boolean;
  
  // Screen orientation and size
  screenSize: 'sm' | 'md' | 'lg' | 'xl';
  orientation: 'portrait' | 'landscape';
  
  // Search
  globalSearchQuery: string;
  searchHistory: string[];
  
  // Filters
  activeFilters: Record<string, any>;
  
  // Refresh control
  refreshing: boolean;
}

const initialState: UIState = {
  sidebarOpen: false,
  currentScreen: 'Dashboard',
  globalLoading: false,
  loadingMessage: undefined,
  notifications: [],
  modal: {
    isOpen: false,
    type: '',
    data: undefined,
  },
  theme: 'light',
  isOnline: true,
  screenSize: 'lg',
  orientation: 'portrait',
  globalSearchQuery: '',
  searchHistory: [],
  activeFilters: {},
  refreshing: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Navigation
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setCurrentScreen: (state, action: PayloadAction<string>) => {
      state.currentScreen = action.payload;
    },

    // Loading
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.globalLoading = action.payload;
      if (!action.payload) {
        state.loadingMessage = undefined;
      }
    },
    setLoadingMessage: (state, action: PayloadAction<string>) => {
      state.loadingMessage = action.payload;
      state.globalLoading = true;
    },

    // Notifications
    addNotification: (state, action: PayloadAction<Omit<NotificationState, 'id' | 'timestamp'>>) => {
      const notification: NotificationState = {
        ...action.payload,
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        timestamp: Date.now(),
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
    },

    // Modals
    openModal: (state, action: PayloadAction<{ type: string; data?: any }>) => {
      state.modal = {
        isOpen: true,
        type: action.payload.type,
        data: action.payload.data,
      };
    },
    closeModal: (state) => {
      state.modal = {
        isOpen: false,
        type: '',
        data: undefined,
      };
    },

    // Theme
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },

    // Network
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },

    // Screen
    setScreenSize: (state, action: PayloadAction<'sm' | 'md' | 'lg' | 'xl'>) => {
      state.screenSize = action.payload;
    },
    setOrientation: (state, action: PayloadAction<'portrait' | 'landscape'>) => {
      state.orientation = action.payload;
    },

    // Search
    setGlobalSearchQuery: (state, action: PayloadAction<string>) => {
      state.globalSearchQuery = action.payload;
    },
    addToSearchHistory: (state, action: PayloadAction<string>) => {
      const query = action.payload.trim();
      if (query && !state.searchHistory.includes(query)) {
        state.searchHistory.unshift(query);
        // Keep only last 10 searches
        state.searchHistory = state.searchHistory.slice(0, 10);
      }
    },
    clearSearchHistory: (state) => {
      state.searchHistory = [];
    },
    removeFromSearchHistory: (state, action: PayloadAction<string>) => {
      state.searchHistory = state.searchHistory.filter(
        query => query !== action.payload
      );
    },

    // Filters
    setFilter: (state, action: PayloadAction<{ key: string; value: any }>) => {
      state.activeFilters[action.payload.key] = action.payload.value;
    },
    removeFilter: (state, action: PayloadAction<string>) => {
      delete state.activeFilters[action.payload];
    },
    clearFilters: (state) => {
      state.activeFilters = {};
    },
    setFilters: (state, action: PayloadAction<Record<string, any>>) => {
      state.activeFilters = action.payload;
    },

    // Refresh
    setRefreshing: (state, action: PayloadAction<boolean>) => {
      state.refreshing = action.payload;
    },

    // Utility actions
    resetUI: (state) => {
      return {
        ...initialState,
        theme: state.theme, // Preserve theme
        searchHistory: state.searchHistory, // Preserve search history
      };
    },

    // Batch actions for better performance
    updateUIState: (state, action: PayloadAction<Partial<UIState>>) => {
      Object.assign(state, action.payload);
    },
  },
});

// Action creators for common notification patterns
export const showSuccessNotification = (title: string, message?: string) => 
  uiSlice.actions.addNotification({
    type: 'success',
    title,
    message,
    duration: 3000,
  });

export const showErrorNotification = (title: string, message?: string) => 
  uiSlice.actions.addNotification({
    type: 'error',
    title,
    message,
    duration: 5000,
  });

export const showWarningNotification = (title: string, message?: string) => 
  uiSlice.actions.addNotification({
    type: 'warning',
    title,
    message,
    duration: 4000,
  });

export const showInfoNotification = (title: string, message?: string) => 
  uiSlice.actions.addNotification({
    type: 'info',
    title,
    message,
    duration: 3000,
  });

export const {
  // Navigation
  setSidebarOpen,
  toggleSidebar,
  setCurrentScreen,

  // Loading
  setGlobalLoading,
  setLoadingMessage,

  // Notifications
  addNotification,
  removeNotification,
  clearAllNotifications,

  // Modals
  openModal,
  closeModal,

  // Theme
  setTheme,
  toggleTheme,

  // Network
  setOnlineStatus,

  // Screen
  setScreenSize,
  setOrientation,

  // Search
  setGlobalSearchQuery,
  addToSearchHistory,
  clearSearchHistory,
  removeFromSearchHistory,

  // Filters
  setFilter,
  removeFilter,
  clearFilters,
  setFilters,

  // Refresh
  setRefreshing,

  // Utility
  resetUI,
  updateUIState,
} = uiSlice.actions;

export default uiSlice.reducer;