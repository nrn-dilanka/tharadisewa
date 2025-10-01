# TharadiSewa Mobile App

A React Native mobile application built with Expo for the TharadiSewa system. This app provides user authentication, registration, and dashboard functionality that connects to the Django backend.

## 🚀 Features

### Authentication
- **User Registration**: Create new user accounts with form validation
- **User Login**: Secure login with JWT token authentication  
- **Persistent Sessions**: Automatic login persistence using AsyncStorage
- **Token Management**: Automatic token refresh and session management
- **Role-based Access**: Support for different user roles (customer, staff, admin, etc.)

### User Interface
- **Modern Design**: Clean, Material Design-inspired UI
- **Form Validation**: Real-time form validation with helpful error messages
- **Loading States**: Smooth loading indicators and transitions
- **Error Handling**: Comprehensive error boundary and error handling
- **Responsive Layout**: Works on various screen sizes

### Technical Features
- **TypeScript Support**: Ready for TypeScript migration
- **Configuration Management**: Centralized app configuration
- **Session Management**: Advanced session handling with automatic cleanup
- **API Integration**: Full integration with Django REST API
- **Error Boundary**: Crash protection and error reporting

## 📱 Screens

### Authentication Flow
1. **Login Screen**: Username/password authentication
2. **Register Screen**: New user registration with role selection
3. **Dashboard Screen**: User profile and quick actions

### Components
- **CustomTextInput**: Reusable form input component
- **CustomButton**: Configurable button component with loading states
- **LoadingScreen**: Various loading state components
- **ErrorBoundary**: Error handling and recovery

## 🛠️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── CustomButton.js
│   ├── CustomTextInput.js
│   ├── ErrorBoundary.js
│   └── LoadingScreen.js
├── config/             # App configuration
│   └── app.js
├── contexts/           # React Context providers
│   └── AuthContext.js
├── navigation/         # Navigation configuration
│   ├── AuthNavigator.js
│   ├── AppNavigator.js
│   └── NavigationController.js
├── screens/           # Screen components
│   ├── LoginScreen.js
│   ├── RegisterScreen.js
│   └── DashboardScreen.js
├── services/          # API and external services
│   ├── api.js
│   └── authService.js
├── types/             # TypeScript type definitions (future)
└── utils/             # Utility functions
    ├── sessionManager.js
    └── validation.js
```

## 🔧 Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Expo CLI
- iOS Simulator or Android Emulator (optional)
- Expo Go app on your phone (for testing)

### Installation Steps

1. **Navigate to the app directory**:
   ```bash
   cd mobile-app/TharadiSewaApp
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npx expo start
   ```

4. **Run on device/simulator**:
   - Scan QR code with Expo Go (Android) or Camera (iOS)
   - Press `a` for Android emulator
   - Press `i` for iOS simulator

## ⚙️ Configuration

### API Configuration
Update the API base URL in `src/config/app.js`:

```javascript
API: {
  BASE_URL: __DEV__ ? 'http://127.0.0.1:8000' : 'https://your-production-url.com',
  // ... other config
}
```

### Environment Variables
The app supports different configurations for development and production through the `__DEV__` flag.

## 🔐 Authentication Flow

1. **Login Process**:
   - User enters credentials
   - App validates form data
   - Sends login request to Django backend
   - Receives JWT tokens (access & refresh)
   - Stores tokens securely in AsyncStorage
   - Navigates to authenticated screens

2. **Registration Process**:
   - User fills registration form
   - Validates all required fields
   - Sends registration data to backend
   - Shows success message
   - Redirects to login screen

3. **Session Management**:
   - Automatically checks token validity on app start
   - Refreshes tokens when needed (5 minutes before expiry)
   - Handles token expiration gracefully
   - Clears session data on logout

## 🌐 API Integration

### Endpoints Used
- `POST /api/auth/login/` - User authentication
- `POST /api/auth/token/refresh/` - Token refresh  
- `POST /api/users/` - User registration
- `GET /api/users/profile/` - Get current user profile
- `POST /api/auth/logout/` - User logout

### Request/Response Format
All API requests include:
- `Content-Type: application/json`
- `Authorization: Bearer <token>` (for authenticated requests)

## 🧪 Testing

### Manual Testing
1. Start the Django backend server
2. Start the Expo development server
3. Test the following flows:
   - User registration
   - User login
   - Dashboard navigation
   - Token refresh
   - Logout

### Automated Testing (Future)
The app structure supports adding:
- Unit tests with Jest
- Component tests with React Native Testing Library
- E2E tests with Detox

## 🚦 Error Handling

### Error Boundary
Catches JavaScript errors anywhere in the component tree and displays a fallback UI.

### API Error Handling
- Network connectivity issues
- Authentication failures
- Validation errors
- Server errors

### User Feedback
- Loading indicators during API calls
- Success/error messages
- Form validation feedback

## 📚 Dependencies

### Main Dependencies
- `@react-navigation/native` - Navigation
- `@react-navigation/native-stack` - Stack navigation
- `axios` - HTTP client
- `@react-native-async-storage/async-storage` - Local storage
- `react-hook-form` - Form handling
- `@hookform/resolvers` - Form validation
- `yup` - Schema validation
- `@react-native-picker/picker` - Picker component

### Development Dependencies
- `@babel/core` - JavaScript compiler
- `eslint` - Code linting

## 🔮 Future Enhancements

### Planned Features
- [ ] Biometric authentication (Face ID/Touch ID)
- [ ] Push notifications
- [ ] Offline support
- [ ] Dark theme support
- [ ] Multi-language support
- [ ] Profile image upload
- [ ] Advanced user management screens
- [ ] Service booking functionality
- [ ] Order history
- [ ] Payment integration

### Technical Improvements
- [ ] TypeScript migration
- [ ] State management with Redux Toolkit
- [ ] Automated testing suite
- [ ] Performance optimization
- [ ] Code splitting and lazy loading
- [ ] Accessibility improvements

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler cache issues**:
   ```bash
   npx expo start --clear
   ```

2. **Network connectivity issues**:
   - Ensure Django backend is running on `http://127.0.0.1:8000`
   - Check that your device/emulator can reach the backend

3. **AsyncStorage issues**:
   - Clear app data in development
   - Restart the app

4. **Navigation issues**:
   - Ensure all screens are properly imported
   - Check navigation params

## 📄 License

This project is part of the TharadiSewa system. Please refer to the main project license.

## 👥 Contributing

1. Follow the existing code structure
2. Use meaningful component and function names
3. Add proper error handling
4. Test your changes thoroughly
5. Update documentation as needed

## 📞 Support

For technical support or questions about the mobile app, please contact the development team or create an issue in the project repository.