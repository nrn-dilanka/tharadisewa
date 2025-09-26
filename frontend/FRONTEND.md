# TharadiSewa Frontend

A modern React-based business management frontend application built with Vite, TypeScript, Redux Toolkit, and Tailwind CSS.

## Features

- 🔐 **Authentication System**: Login/Register with JWT token management
- 📊 **Dashboard**: Business overview with key metrics and statistics  
- 👥 **Customer Management**: Create, read, update, delete customer records
- 📦 **Product Management**: Inventory tracking with stock management
- 🛒 **Purchase Management**: Track supplier purchases and costs
- 💰 **Sales Management**: Record sales transactions
- 📈 **Financial Reports**: Business analytics and reporting
- 📱 **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- 🎨 **Modern UI**: Clean, professional interface design

## Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite 7.1.7 for fast development and building
- **State Management**: Redux Toolkit with Redux Persist
- **Routing**: React Router DOM v6
- **Styling**: Tailwind CSS with PostCSS
- **HTTP Client**: Axios for API communication
- **Authentication**: JWT tokens with automatic refresh

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main application layout
│   │   └── ProtectedRoute.tsx # Route protection wrapper
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx    # Authentication pages
│   │   ├── RegisterPage.tsx
│   │   └── DashboardPage.tsx # Main dashboard
│   ├── store/               # Redux store and slices
│   │   ├── index.ts         # Store configuration
│   │   └── slices/          # Feature-specific state slices
│   │       ├── authSlice.ts
│   │       ├── customerSlice.ts
│   │       ├── productSlice.ts
│   │       └── purchaseSlice.ts
│   ├── services/            # API service layer
│   │   └── api.ts           # Axios configuration and API calls
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # Shared interfaces and types
│   ├── App.tsx              # Main application component
│   └── main.tsx             # Application entry point
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Django backend API running on port 8000

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**: http://localhost:5173

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality
- `npm run type-check` - Run TypeScript compiler check

## Current Status

✅ **Completed**:
- ✅ Django backend with 11 apps and comprehensive API endpoints
- ✅ Authentication system with JWT token management
- ✅ Redux store with auth, customer, product, purchase slices  
- ✅ Protected route handling and navigation
- ✅ Modern responsive layout with sidebar navigation
- ✅ Login and registration pages with form validation
- ✅ Dashboard foundation with stats cards and quick actions
- ✅ API service layer with comprehensive endpoint coverage
- ✅ TypeScript types for all data models and API responses
- ✅ Tailwind CSS styling with professional UI design

🚧 **In Progress**:
- 🔄 Customer management pages (CRUD operations)
- 🔄 Product inventory pages with stock management
- 🔄 Purchase recording interface with item selection
- 🔄 Sales transaction handling and invoice generation
- 🔄 Financial reporting dashboard with charts

📋 **Next Steps**:
1. Complete CRUD pages for customers, products, purchases
2. Add data visualization with charts and graphs
3. Implement search, filtering, and pagination
4. Add export/import functionality for data
5. Performance optimization and comprehensive testing
6. Add real-time notifications and updates

## Development Server

The frontend is currently running at: **http://localhost:5173**

Connect to Django backend at: **http://localhost:8000/api**

## Architecture Highlights

### State Management
- Redux Toolkit with RTK Query for efficient data fetching
- Redux Persist for authentication state persistence
- Optimistic UI updates for better user experience
- Centralized error handling across all slices

### Authentication Flow
- JWT access/refresh token system
- Automatic token refresh on API calls
- Protected routes with seamless redirects
- Persistent login state across browser sessions

### API Integration
- Axios interceptors for request/response handling
- Automatic error handling and user feedback
- Consistent API client configuration
- Type-safe API calls with TypeScript

### UI/UX Design
- Mobile-first responsive design
- Consistent design system with Tailwind CSS
- Loading states and error boundaries
- Accessible navigation and form controls
- Professional business application styling

This frontend provides a solid foundation for a comprehensive business management system with room for future enhancements and scalability.