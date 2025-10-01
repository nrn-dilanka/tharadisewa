import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../contexts/AuthContext';
import { registrationValidationSchema } from '../utils/validation';
import CustomTextInput from '../components/CustomTextInput';
import CustomButton from '../components/CustomButton';
import ConnectionTest from '../components/ConnectionTest';

const RegisterScreen = ({ navigation }) => {
  const { register, isLoading, error, clearError, registrationEnabled, checkRegistrationStatus } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [debugInfo, setDebugInfo] = useState(false);

  // Check registration status on component mount
  useEffect(() => {
    console.log('RegisterScreen mounted, checking registration status...');
    checkRegistrationStatus();
  }, []);

  // If registration is disabled, show message and redirect to login
  useEffect(() => {
    console.log('Registration enabled status changed:', registrationEnabled);
    if (registrationEnabled === false) {
      Alert.alert(
        'Registration Disabled',
        'Registration is currently disabled. An administrator already exists. Please contact the administrator for account creation.',
        [
          {
            text: 'Go to Login',
            onPress: () => navigation.replace('Login'),
          },
        ]
      );
    }
  }, [registrationEnabled, navigation]);

  const {
    control,
    handleSubmit,
    formState: { errors, isValid, isDirty },
    reset,
    watch,
    trigger,
  } = useForm({
    resolver: yupResolver(registrationValidationSchema),
    mode: 'onChange',
    defaultValues: {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      password_confirm: '',
      phone_number: '',
      role: 'admin', // First user will be admin
    },
  });

  const formValues = watch();
  const password = watch('password');

  // Debug logging for form state
  useEffect(() => {
    console.log('Form state changed:', {
      isValid,
      isDirty,
      hasErrors: Object.keys(errors).length > 0,
      errors: errors,
      formValues: formValues,
      registrationEnabled,
    });
  }, [isValid, isDirty, errors, formValues, registrationEnabled]);

  const onSubmit = async (data) => {
    console.log('Form submission started with data:', data);
    clearError();
    
    try {
      const result = await register(data);
      console.log('Registration result:', result);
      
      if (result.success) {
        const message = result.isFirstAdmin 
          ? 'Admin account created successfully! You are now the system administrator and can manage users.'
          : 'Registration successful!';
        
        Alert.alert(
          'Registration Successful',
          message,
          [
            {
              text: 'OK',
              onPress: () => {
                reset();
                // If user was automatically logged in (first admin), go to dashboard
                if (result.isFirstAdmin) {
                  navigation.replace('AdminDashboard');
                } else {
                  navigation.navigate('Login');
                }
              },
            },
          ]
        );
      } else {
        console.error('Registration failed:', result);
        let errorMessage = result.message || 'Registration failed. Please try again.';
        
        if (result.error) {
          if (typeof result.error === 'string') {
            errorMessage = result.error;
          } else if (result.error.username) {
            errorMessage = `Username: ${result.error.username[0]}`;
          } else if (result.error.email) {
            errorMessage = `Email: ${result.error.email[0]}`;
          } else if (result.error.message) {
            errorMessage = result.error.message;
          } else if (result.error.detail) {
            errorMessage = result.error.detail;
          }
        }
        
        Alert.alert('Registration Failed', errorMessage);
      }
    } catch (error) {
      console.error('Registration submission error:', error);
      Alert.alert('Registration Error', 'An unexpected error occurred. Please try again.');
    }
  };

  // Check if form is ready for submission
  const isFormReady = () => {
    const requiredFields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm'];
    const hasAllRequiredFields = requiredFields.every(field => 
      formValues[field] && formValues[field].trim() !== ''
    );
    const noValidationErrors = Object.keys(errors).length === 0;
    const passwordsMatch = formValues.password === formValues.password_confirm;
    
    console.log('Form readiness check:', {
      hasAllRequiredFields,
      noValidationErrors,
      passwordsMatch,
      registrationEnabled,
      isLoading
    });
    
    return hasAllRequiredFields && noValidationErrors && passwordsMatch && registrationEnabled && !isLoading;
  };

  // Show loading or registration disabled message if needed
  if (registrationEnabled === false) {
    return (
      <View style={[styles.container, styles.centeredContainer]}>
        <Text style={styles.disabledTitle}>Registration Disabled</Text>
        <Text style={styles.disabledMessage}>
          Registration is currently disabled. An administrator already exists. 
          Please contact the administrator for account creation.
        </Text>
        <TouchableOpacity 
          style={styles.backToLoginButton} 
          onPress={() => navigation.replace('Login')}
        >
          <Text style={styles.backToLoginText}>Go to Login</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <Text style={styles.title}>Create Admin Account</Text>
          <Text style={styles.description}>
            Create the first administrator account for TharadiSewa system
          </Text>
          
          {__DEV__ && (
            <TouchableOpacity 
              style={styles.debugToggle}
              onPress={() => setDebugInfo(!debugInfo)}
            >
              <Text style={styles.debugToggleText}>
                {debugInfo ? 'Hide' : 'Show'} Debug Info
              </Text>
            </TouchableOpacity>
          )}
          
          {__DEV__ && debugInfo && (
            <View style={styles.debugContainer}>
              <Text style={styles.debugTitle}>Debug Information:</Text>
              <Text style={styles.debugText}>Registration Enabled: {String(registrationEnabled)}</Text>
              <Text style={styles.debugText}>Form Valid: {String(isValid)}</Text>
              <Text style={styles.debugText}>Form Dirty: {String(isDirty)}</Text>
              <Text style={styles.debugText}>Errors: {Object.keys(errors).length}</Text>
              <Text style={styles.debugText}>Is Loading: {String(isLoading)}</Text>
              <Text style={styles.debugText}>Form Ready: {String(isFormReady())}</Text>
              {Object.keys(errors).length > 0 && (
                <Text style={styles.debugText}>Error Fields: {Object.keys(errors).join(', ')}</Text>
              )}
              
              {/* Connection Test Component */}
              <ConnectionTest />
            </View>
          )}
        </View>

        <View style={styles.form}>
          <Controller
            control={control}
            name="username"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Username *"
                placeholder="Choose a username"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('username'); // Trigger validation
                }}
                onBlur={onBlur}
                error={errors.username?.message}
                touched={!!errors.username}
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="next"
                blurOnSubmit={false}
              />
            )}
          />

          <View style={styles.nameContainer}>
            <View style={styles.nameField}>
              <Controller
                control={control}
                name="first_name"
                render={({ field: { onChange, onBlur, value } }) => (
                  <CustomTextInput
                    label="First Name *"
                    placeholder="Your first name"
                    value={value}
                    onChangeText={(text) => {
                      onChange(text);
                      trigger('first_name');
                    }}
                    onBlur={onBlur}
                    error={errors.first_name?.message}
                    touched={!!errors.first_name}
                    autoCapitalize="words"
                    returnKeyType="next"
                    blurOnSubmit={false}
                  />
                )}
              />
            </View>
            <View style={styles.nameField}>
              <Controller
                control={control}
                name="last_name"
                render={({ field: { onChange, onBlur, value } }) => (
                  <CustomTextInput
                    label="Last Name *"
                    placeholder="Your last name"
                    value={value}
                    onChangeText={(text) => {
                      onChange(text);
                      trigger('last_name');
                    }}
                    onBlur={onBlur}
                    error={errors.last_name?.message}
                    touched={!!errors.last_name}
                    autoCapitalize="words"
                    returnKeyType="next"
                    blurOnSubmit={false}
                  />
                )}
              />
            </View>
          </View>

          <Controller
            control={control}
            name="email"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Email *"
                placeholder="your.email@example.com"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('email');
                }}
                onBlur={onBlur}
                error={errors.email?.message}
                touched={!!errors.email}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="next"
                blurOnSubmit={false}
              />
            )}
          />

          <Controller
            control={control}
            name="phone_number"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Phone Number"
                placeholder="0771234567 or +94771234567"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('phone_number');
                }}
                onBlur={onBlur}
                error={errors.phone_number?.message}
                touched={!!errors.phone_number}
                keyboardType="phone-pad"
                returnKeyType="next"
                blurOnSubmit={false}
              />
            )}
          />

          {/* Role is automatically set to admin for first user */}
          <View style={styles.infoContainer}>
            <Text style={styles.infoText}>
              You will be registered as the system administrator with full access to manage users and system settings.
            </Text>
          </View>

          <Controller
            control={control}
            name="password"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Password *"
                placeholder="Choose a strong password"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('password');
                  // Also trigger password_confirm validation if it has a value
                  if (formValues.password_confirm) {
                    trigger('password_confirm');
                  }
                }}
                onBlur={onBlur}
                error={errors.password?.message}
                touched={!!errors.password}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="next"
                blurOnSubmit={false}
              />
            )}
          />

          <TouchableOpacity
            style={styles.showPasswordContainer}
            onPress={() => setShowPassword(!showPassword)}
          >
            <Text style={styles.showPasswordText}>
              {showPassword ? 'Hide Password' : 'Show Password'}
            </Text>
          </TouchableOpacity>

          <Controller
            control={control}
            name="password_confirm"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Confirm Password *"
                placeholder="Re-enter your password"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('password_confirm');
                }}
                onBlur={onBlur}
                error={errors.password_confirm?.message}
                touched={!!errors.password_confirm}
                secureTextEntry={!showConfirmPassword}
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="done"
                blurOnSubmit={false}
              />
            )}
          />

          <TouchableOpacity
            style={styles.showPasswordContainer}
            onPress={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            <Text style={styles.showPasswordText}>
              {showConfirmPassword ? 'Hide Password' : 'Show Password'}
            </Text>
          </TouchableOpacity>

          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>
                {typeof error === 'string' ? error : error.message || 'Registration failed'}
              </Text>
            </View>
          )}

          {/* Form validation status */}
          {__DEV__ && debugInfo && (
            <View style={styles.validationStatus}>
              <Text style={styles.validationTitle}>Form Validation Status:</Text>
              {Object.keys(formValues).map(field => (
                <Text key={field} style={[
                  styles.validationText,
                  errors[field] ? styles.validationError : styles.validationSuccess
                ]}>
                  {field}: {formValues[field] ? '✓' : '✗'} 
                  {errors[field] ? ` (${errors[field].message})` : ''}
                </Text>
              ))}
            </View>
          )}

          <CustomButton
            title="Create Account"
            onPress={handleSubmit(onSubmit)}
            loading={isLoading}
            disabled={!isFormReady()}
            variant="primary"
            size="large"
            style={styles.registerButton}
          />

          {/* Button status indicator */}
          <View style={styles.buttonStatus}>
            <Text style={styles.buttonStatusText}>
              Button Status: {isFormReady() ? '✓ Ready' : '✗ Disabled'}
            </Text>
            {!isFormReady() && (
              <Text style={styles.buttonStatusReason}>
                Reason: {
                  !registrationEnabled ? 'Registration disabled' :
                  isLoading ? 'Loading...' :
                  Object.keys(errors).length > 0 ? `Form errors: ${Object.keys(errors).join(', ')}` :
                  'Fill all required fields'
                }
              </Text>
            )}
          </View>

          <View style={styles.loginContainer}>
            <Text style={styles.loginText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => navigation.navigate('Login')}>
              <Text style={styles.loginLink}>Sign In</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingVertical: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
    marginTop: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  form: {
    backgroundColor: '#fff',
    padding: 24,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  nameContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: -8,
  },
  nameField: {
    flex: 1,
    marginHorizontal: 8,
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  picker: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    backgroundColor: '#fff',
  },
  pickerStyle: {
    height: 50,
  },
  showPasswordContainer: {
    alignSelf: 'flex-end',
    marginTop: -8,
    marginBottom: 16,
  },
  showPasswordText: {
    color: '#007bff',
    fontSize: 14,
    fontWeight: '500',
  },
  errorContainer: {
    backgroundColor: '#fdf2f2',
    padding: 12,
    borderRadius: 6,
    borderLeftWidth: 4,
    borderLeftColor: '#e74c3c',
    marginBottom: 16,
  },
  errorText: {
    color: '#e74c3c',
    fontSize: 14,
    fontWeight: '500',
  },
  infoContainer: {
    backgroundColor: '#e3f2fd',
    padding: 15,
    borderRadius: 8,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#2196f3',
  },
  infoText: {
    color: '#1976d2',
    fontSize: 14,
    fontWeight: '500',
    textAlign: 'center',
  },
  centeredContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  disabledTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#e74c3c',
    marginBottom: 16,
    textAlign: 'center',
  },
  disabledMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  backToLoginButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backToLoginText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  registerButton: {
    marginBottom: 24,
  },
  debugToggle: {
    backgroundColor: '#17a2b8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
    marginTop: 10,
  },
  debugToggleText: {
    color: 'white',
    fontSize: 12,
    textAlign: 'center',
  },
  debugContainer: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    marginTop: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#17a2b8',
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  debugText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  validationStatus: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    marginBottom: 16,
    borderLeftWidth: 3,
    borderLeftColor: '#28a745',
  },
  validationTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  validationText: {
    fontSize: 12,
    marginBottom: 2,
  },
  validationSuccess: {
    color: '#28a745',
  },
  validationError: {
    color: '#dc3545',
  },
  buttonStatus: {
    backgroundColor: '#e9ecef',
    padding: 10,
    borderRadius: 6,
    marginBottom: 16,
    alignItems: 'center',
  },
  buttonStatusText: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  buttonStatusReason: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginText: {
    fontSize: 16,
    color: '#666',
  },
  loginLink: {
    fontSize: 16,
    color: '#007bff',
    fontWeight: '600',
  },
});

export default RegisterScreen;