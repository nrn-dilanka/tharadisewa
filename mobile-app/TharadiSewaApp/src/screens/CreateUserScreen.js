import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../contexts/AuthContext';
import { colors } from '../constants/colors';
import { validateEmail, validatePassword } from '../utils/validation';

const CreateUserScreen = ({ navigation, route }) => {
  const { adminCreateUser, adminUpdateUser } = useAuth();
  const editUser = route.params?.user; // Get user data if editing
  const isEditMode = !!editUser; // Determine if we're in edit mode
  
  console.log('Edit mode:', editUser);
  

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    role: 'customer',
    phone_number: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Pre-populate form data if editing
  useEffect(() => {
    if (isEditMode && editUser) {
      console.log('🔧 Edit mode detected, pre-populating form:', editUser);
      setFormData({
        username: editUser.username || '',
        email: editUser.email || '',
        password: '', // Don't pre-fill password for security
        confirmPassword: '', // Don't pre-fill password confirmation
        first_name: editUser.first_name || '',
        last_name: editUser.last_name || '',
        role: editUser.role || 'customer',
        phone_number: editUser.phone_number || '',
      });
    }
  }, [isEditMode, editUser]);

  const roles = [
    { label: 'Customer', value: 'customer' },
    { label: 'Staff', value: 'staff' },
    { label: 'Manager', value: 'manager' },
    { label: 'Technician', value: 'technician' },
    { label: 'Sales Representative', value: 'sales' },
    { label: 'Support Staff', value: 'support' },
  ];

  // stable input change handler
  const handleInputChange = useCallback((field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setErrors(prev => {
      if (prev[field]) {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      }
      return prev;
    });
  }, []);

  // Memoized handlers
  const handleUsernameChange = useCallback((value) => handleInputChange('username', value), [handleInputChange]);
  const handleEmailChange = useCallback((value) => handleInputChange('email', value), [handleInputChange]);
  const handleFirstNameChange = useCallback((value) => handleInputChange('first_name', value), [handleInputChange]);
  const handleLastNameChange = useCallback((value) => handleInputChange('last_name', value), [handleInputChange]);
  const handlePhoneChange = useCallback((value) => handleInputChange('phone_number', value), [handleInputChange]);
  const handlePasswordChange = useCallback((value) => handleInputChange('password', value), [handleInputChange]);
  const handleConfirmPasswordChange = useCallback((value) => handleInputChange('confirmPassword', value), [handleInputChange]);
  const handleRoleChange = useCallback((value) => handleInputChange('role', value), [handleInputChange]);

  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation (only required for new users)
    if (!isEditMode) {
      // Creating new user - password is required
      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (!validatePassword(formData.password)) {
        newErrors.password = 'Password must be at least 8 characters with uppercase, lowercase, number and special character';
      }

      // Confirm password validation (only for new users)
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    } else {
      // Editing user - password is optional, but if provided must be valid
      if (formData.password && !validatePassword(formData.password)) {
        newErrors.password = 'Password must be at least 8 characters with uppercase, lowercase, number and special character';
      }
      
      // If password is provided, confirmation is required
      if (formData.password && !formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm password';
      } else if (formData.password && formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    // Name validation
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }

    console.log('Validation errors:', newErrors); // Debug log
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    console.log('🚀 handleSubmit called'); // Debug log
    console.log('Edit Mode:', isEditMode); // Debug log
    console.log('Form Data:', formData); // Debug log
    console.log('Current errors before validation:', errors); // Debug log
    
    // const isValid = validateForm();
    // console.log('Validation result:', isValid); // Debug log
    // console.log('Errors after validation:', errors); // Debug log
    
    // if (!isValid) {
    //   console.log('❌ Form validation failed, stopping submission'); // Debug log
    //   return;
    // }
    console.log('✅ Form is valid, proceeding with submission...'); // Debug log
    
    setLoading(true);
    console.log('⏳ Loading set to true'); // Debug log

    try {
      const userData = {
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        role: formData.role,
        phone_number: formData.phone_number.trim(),
      };

      // Only include password fields if provided (for both create and edit)
      if (formData.password) {
        userData.password = formData.password;
        userData.password_confirm = formData.confirmPassword;
      }

      console.log('Sending userData:', userData); // Debug log
      
      let result;
      if (isEditMode) {
        // Update existing user
        result = await adminUpdateUser(editUser.id, userData);
      } else {
        // Create new user
        result = await adminCreateUser(userData);
      }
      console.log('API Result:', result); // Debug log

      if (result.success) {
        console.log(`✅ User ${isEditMode ? 'updated' : 'created'} successfully`); // Debug log
        Alert.alert(
          'Success',
          result.message || `User ${isEditMode ? 'updated' : 'created'} successfully`,
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack(),
            },
          ]
        );
      } else {
        console.log('❌ API call failed:', result.error); // Debug log
        const errorMessage = result.error?.message || `Failed to ${isEditMode ? 'update' : 'create'} user`;
        Alert.alert('Error', errorMessage);

        // Handle field-specific errors
        if (result.error && typeof result.error === 'object') {
          const fieldErrors = {};
          Object.keys(result.error).forEach(key => {
            let errorKey = key;
            // Map API field names to form field names
            if (key === 'password_confirm') {
              errorKey = 'confirmPassword';
            }
            
            if (Array.isArray(result.error[key])) {
              fieldErrors[errorKey] = result.error[key][0];
            } else if (typeof result.error[key] === 'string') {
              fieldErrors[errorKey] = result.error[key];
            }
          });
          console.log('Setting API field errors:', fieldErrors); // Debug log
          setErrors(fieldErrors);
        }
      }
    } catch (error) {
      console.log('🚨 Exception in handleSubmit:', error); // Debug log
      Alert.alert('Error', 'An unexpected error occurred');
    } finally {
      console.log('🏁 handleSubmit completed, loading:', false); // Debug log
      setLoading(false);
    }
  };



  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardContainer}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Text style={styles.backButton}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>{isEditMode ? 'Edit User' : 'Create New User'}</Text>
        </View>

        <ScrollView
          style={styles.form}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="none"
          nestedScrollEnabled={false}
          scrollEnabled={true}
        >
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Username</Text>
            <TextInput
              style={[
                styles.input,
                errors.username && styles.inputError,
              ]}
              value={formData.username}
              onChangeText={handleUsernameChange}
              placeholder="Enter username"
              placeholderTextColor={colors.text.secondary}
              autoCapitalize="none"
              autoCorrect={false}
              returnKeyType="next"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.username && (
              <Text style={styles.errorText}>{errors.username}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Email</Text>
            <TextInput
              style={[
                styles.input,
                errors.email && styles.inputError,
              ]}
              value={formData.email}
              onChangeText={handleEmailChange}
              placeholder="Enter email address"
              placeholderTextColor={colors.text.secondary}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              returnKeyType="next"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.email && (
              <Text style={styles.errorText}>{errors.email}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>First Name</Text>
            <TextInput
              style={[
                styles.input,
                errors.first_name && styles.inputError,
              ]}
              value={formData.first_name}
              onChangeText={handleFirstNameChange}
              placeholder="Enter first name"
              placeholderTextColor={colors.text.secondary}
              autoCapitalize="words"
              returnKeyType="next"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.first_name && (
              <Text style={styles.errorText}>{errors.first_name}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Last Name</Text>
            <TextInput
              style={[
                styles.input,
                errors.last_name && styles.inputError,
              ]}
              value={formData.last_name}
              onChangeText={handleLastNameChange}
              placeholder="Enter last name"
              placeholderTextColor={colors.text.secondary}
              autoCapitalize="words"
              returnKeyType="next"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.last_name && (
              <Text style={styles.errorText}>{errors.last_name}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Phone Number (Optional)</Text>
            <TextInput
              style={[
                styles.input,
                errors.phone_number && styles.inputError,
              ]}
              value={formData.phone_number}
              onChangeText={handlePhoneChange}
              placeholder="Enter phone number"
              placeholderTextColor={colors.text.secondary}
              keyboardType="phone-pad"
              returnKeyType="next"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.phone_number && (
              <Text style={styles.errorText}>{errors.phone_number}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Role</Text>
            <View style={[styles.pickerContainer, errors.role && styles.inputError]}>
              <Picker
                selectedValue={formData.role}
                style={styles.picker}
                onValueChange={handleRoleChange}
              >
                {roles.map((role) => (
                  <Picker.Item
                    key={role.value}
                    label={role.label}
                    value={role.value}
                  />
                ))}
              </Picker>
            </View>
            {errors.role && (
              <Text style={styles.errorText}>{errors.role}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Password</Text>
            <TextInput
              style={[
                styles.input,
                errors.password && styles.inputError,
              ]}
              value={formData.password}
              onChangeText={handlePasswordChange}
              placeholder={isEditMode ? "Enter new password (leave blank to keep current)" : "Enter password"}
              placeholderTextColor={colors.text.secondary}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
              returnKeyType="next"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.password && (
              <Text style={styles.errorText}>{errors.password}</Text>
            )}
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Confirm Password</Text>
            <TextInput
              style={[
                styles.input,
                errors.confirmPassword && styles.inputError,
              ]}
              value={formData.confirmPassword}
              onChangeText={handleConfirmPasswordChange}
              placeholder={isEditMode ? "Confirm new password" : "Confirm password"}
              placeholderTextColor={colors.text.secondary}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
              returnKeyType="done"
              blurOnSubmit={false}
              enablesReturnKeyAutomatically={false}
              clearButtonMode="never"
            />
            {errors.confirmPassword && (
              <Text style={styles.errorText}>{errors.confirmPassword}</Text>
            )}
          </View>

          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={[styles.submitButton, loading && styles.submitButtonDisabled]}
              onPress={handleSubmit}
              disabled={loading}
            >
              <Text style={styles.submitButtonText}>
                {loading ? (isEditMode ? 'Updating User...' : 'Creating User...') : (isEditMode ? 'Update User' : 'Create User')}
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  keyboardContainer: {
    flex: 1,
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    color: colors.primary,
    fontSize: 16,
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text.primary,
  },
  form: {
    flex: 1,
    padding: 20,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text.primary,
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    color: colors.text.primary,
    backgroundColor: colors.surface,
  },
  inputError: {
    borderColor: colors.error,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    backgroundColor: colors.surface,
  },
  picker: {
    height: 50,
    color: colors.text.primary,
  },
  errorText: {
    color: colors.error,
    fontSize: 14,
    marginTop: 5,
    marginLeft: 2,
    fontWeight: '500',
  },
  buttonContainer: {
    marginTop: 20,
    marginBottom: 40,
  },
  submitButton: {
    backgroundColor: colors.primary,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: colors.text.secondary,
  },
  submitButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
});

export default CreateUserScreen;
