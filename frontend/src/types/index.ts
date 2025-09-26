import React from 'react';

// Auth types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined?: string;
  last_login?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

// Customer types
export interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerFormData {
  name: string;
  email: string;
  phone: string;
  address: string;
}

// Product types
export interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  quantity: number;
  category: string;
  sku: string;
  created_at: string;
  updated_at: string;
}

export interface ProductFormData {
  name: string;
  description: string;
  price: string;
  quantity: number;
  category: string;
  sku: string;
}

// Purchase types
export interface PurchaseItem {
  id?: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: string;
  total_price?: string;
}

export interface Purchase {
  id: number;
  purchase_date: string;
  supplier_name: string;
  total_amount: string;
  notes?: string;
  items: PurchaseItem[];
  created_at: string;
  updated_at: string;
}

export interface PurchaseFormData {
  purchase_date: string;
  supplier_name: string;
  notes?: string;
  items: Omit<PurchaseItem, 'id' | 'total_price' | 'product_name'>[];
}

// Sales types
export interface SaleItem {
  id?: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price: string;
  total_price?: string;
}

export interface Sale {
  id: number;
  sale_date: string;
  customer?: number;
  customer_name?: string;
  total_amount: string;
  items: SaleItem[];
  created_at: string;
  updated_at: string;
}

export interface SaleFormData {
  sale_date: string;
  customer?: number;
  items: Omit<SaleItem, 'id' | 'total_price' | 'product_name'>[];
}

// Inventory types
export interface InventoryItem {
  id: number;
  product: Product;
  current_stock: number;
  minimum_stock: number;
  maximum_stock: number;
  reorder_point: number;
  last_restocked: string;
  created_at: string;
  updated_at: string;
}

export interface StockUpdate {
  quantity: number;
  notes?: string;
}

export interface StockHistory {
  id: number;
  product: number;
  change_type: 'purchase' | 'sale' | 'adjustment' | 'return';
  quantity_changed: number;
  previous_quantity: number;
  new_quantity: number;
  reference_id?: number;
  notes?: string;
  created_at: string;
}

// Financial types
export interface Expense {
  id: number;
  date: string;
  amount: string;
  description: string;
  category: string;
  created_at: string;
  updated_at: string;
}

export interface ExpenseFormData {
  date: string;
  amount: string;
  description: string;
  category: string;
}

export interface FinancialReport {
  period: {
    start_date: string;
    end_date: string;
  };
  revenue: {
    total_sales: string;
    total_transactions: number;
    average_sale: string;
  };
  expenses: {
    total_purchases: string;
    total_expenses: string;
    total_cost: string;
  };
  profit: {
    gross_profit: string;
    net_profit: string;
    profit_margin: string;
  };
  inventory: {
    current_value: string;
    low_stock_items: number;
    total_products: number;
  };
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status: number;
}

// Form and UI types
export interface FormField {
  label: string;
  name: string;
  type: 'text' | 'email' | 'password' | 'number' | 'date' | 'textarea' | 'select';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export interface FilterConfig {
  field: string;
  value: any;
  operator: 'equals' | 'contains' | 'gt' | 'lt' | 'gte' | 'lte';
}

// Search and pagination types
export interface SearchParams {
  query?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}

export interface PaginationInfo {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// Dashboard types
export interface DashboardStats {
  customers: {
    total: number;
    new_this_month: number;
  };
  products: {
    total: number;
    low_stock: number;
    out_of_stock: number;
  };
  sales: {
    total_today: string;
    total_this_month: string;
    transactions_today: number;
  };
  purchases: {
    total_this_month: string;
    transactions_this_month: number;
  };
  inventory_value: string;
}

export interface RecentActivity {
  id: number;
  type: 'sale' | 'purchase' | 'customer' | 'product';
  description: string;
  amount?: string;
  timestamp: string;
}

