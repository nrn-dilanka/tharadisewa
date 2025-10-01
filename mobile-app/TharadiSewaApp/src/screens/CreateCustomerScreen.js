import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

import { colors } from '../constants/colors';
import customerService from '../services/customerService';

const CreateCustomerScreen = ({ navigation, route }) => {
  // Check if we're in edit mode and have customer data
  const isEditMode = route?.params?.customer ? true : false;
  const existingCustomer = route?.params?.customer || null;

  // Form state
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    nic: '',
    address: '',
    is_verified: false,
    is_active: true,
  });

  // UI state
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Initialize form data on component mount
  useEffect(() => {
    if (isEditMode && existingCustomer) {
      setFormData({
        first_name: existingCustomer.first_name || '',
        last_name: existingCustomer.last_name || '',
        email: existingCustomer.email || '',
        phone_number: existingCustomer.phone_number || '',
        nic: existingCustomer.nic || '',
        address: existingCustomer.address || '',
        is_verified: existingCustomer.is_verified !== undefined ? existingCustomer.is_verified : false,
        is_active: existingCustomer.is_active !== undefined ? existingCustomer.is_active : true,
      });
    }
  }, [isEditMode, existingCustomer]);

  // Memoized validation function
  const validateForm = useCallback((data) => {
    const newErrors = {};

    // First name validation
    if (!data.first_name || data.first_name.trim().length === 0) {
      newErrors.first_name = 'First name is required';
    } else if (data.first_name.trim().length < 2) {
      newErrors.first_name = 'First name must be at least 2 characters';
    } else if (data.first_name.trim().length > 30) {
      newErrors.first_name = 'First name must be less than 30 characters';
    }

    // Last name validation
    if (!data.last_name || data.last_name.trim().length === 0) {
      newErrors.last_name = 'Last name is required';
    } else if (data.last_name.trim().length < 2) {
      newErrors.last_name = 'Last name must be at least 2 characters';
    } else if (data.last_name.trim().length > 30) {
      newErrors.last_name = 'Last name must be less than 30 characters';
    }

    // Email validation
    if (!data.email || data.email.trim().length === 0) {
      newErrors.email = 'Email is required';
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.email.trim())) {
        newErrors.email = 'Please enter a valid email address';
      }
    }

    // NIC validation
    if (!data.nic || data.nic.trim().length === 0) {
      newErrors.nic = 'NIC is required';
    } else {
      const nicRegex = /^(?:\d{9}[vVxX]|\d{12})$/;
      if (!nicRegex.test(data.nic.trim())) {
        newErrors.nic = 'NIC must be in format: 123456789V or 123456789012';
      }
    }

    // Phone number validation (optional but if provided must be valid)
    if (data.phone_number && data.phone_number.trim() !== '') {
      const phoneRegex = /^\+?1?\d{9,15}$/;
      if (!phoneRegex.test(data.phone_number.replace(/\s/g, ''))) {
        newErrors.phone_number = 'Please enter a valid phone number';
      }
    }

    // Address validation (optional)
    if (data.address && data.address.length > 500) {
      newErrors.address = 'Address must be less than 500 characters';
    }

    return newErrors;
  }, []);

  // Memoized form change handler
  const handleInputChange = useCallback((field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, [errors]);

  // Form submission handler
  const handleSubmit = useCallback(async () => {
    console.log('CreateCustomerScreen handleSubmit - Form data:', formData);
    
    const validationErrors = validateForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      Alert.alert('Validation Error', 'Please correct the errors in the form');
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      // Prepare data for API
      const customerData = {
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim().toLowerCase(),
        nic: formData.nic.trim().toUpperCase(),
        is_active: formData.is_active,
        is_verified: formData.is_verified,
      };

      // Add optional fields only if they have values
      if (formData.phone_number && formData.phone_number.trim()) {
        customerData.phone_number = formData.phone_number.trim();
      }

      if (formData.address && formData.address.trim()) {
        customerData.address = formData.address.trim();
      }

      console.log('CreateCustomerScreen - Sending customer data:', customerData);

      let result;
      if (isEditMode) {
        result = await customerService.updateCustomer(existingCustomer.id, customerData);
      } else {
        result = await customerService.createCustomer(customerData);
      }

      console.log('CreateCustomerScreen - API result:', result);

      if (result.success) {
        Alert.alert(
          'Success', 
          isEditMode ? 'Customer updated successfully!' : 'Customer created successfully!',
          [
            { 
              text: 'OK', 
              onPress: () => {
                navigation.goBack();
              }
            }
          ]
        );
      } else {
        // Handle API errors
        const errorMessage = result.message || result.error?.message || 'Operation failed';
        Alert.alert('Error', errorMessage);
        
        // If there are field-specific errors, set them
        if (result.error?.errors) {
          setErrors(result.error.errors);
        }
      }
    } catch (error) {
      console.error('Submit customer error:', error);
      Alert.alert('Error', 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [formData, validateForm, errors, isEditMode, existingCustomer, navigation]);

  // Memoized form validity check
  const isFormValid = useMemo(() => {
    const validationErrors = validateForm(formData);
    return Object.keys(validationErrors).length === 0 && 
           formData.first_name.trim() !== '' && 
           formData.last_name.trim() !== '' && 
           formData.email.trim() !== '' && 
           formData.nic.trim() !== '';
  }, [formData, validateForm]);

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.goBack()}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <MaterialIcons name="arrow-back" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        
        <View style={styles.headerContent}>
          <Text style={styles.title}>
            {isEditMode ? 'Edit Customer' : 'Create New Customer'}
          </Text>
          <Text style={styles.subtitle}>
            {isEditMode ? 'Update customer information' : 'Add a new customer to your system'}
          </Text>
        </View>
      </View>

      {/* Form */}
      <ScrollView 
        style={styles.form}
        contentContainerStyle={styles.formContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* Name Fields */}
        <View style={styles.rowContainer}>
          <View style={styles.halfInput}>
            <Text style={styles.inputLabel}>First Name *</Text>
            <TextInput
              style={[
                styles.textInput,
                errors.first_name && styles.textInputError
              ]}
              placeholder="Enter first name"
              placeholderTextColor={colors.text.secondary}
              value={formData.first_name}
              onChangeText={(value) => handleInputChange('first_name', value)}
              autoCapitalize="words"
              returnKeyType="next"
              blurOnSubmit={false}
            />
            {errors.first_name && <Text style={styles.errorText}>{errors.first_name}</Text>}
          </View>

          <View style={styles.halfInput}>
            <Text style={styles.inputLabel}>Last Name *</Text>
            <TextInput
              style={[
                styles.textInput,
                errors.last_name && styles.textInputError
              ]}
              placeholder="Enter last name"
              placeholderTextColor={colors.text.secondary}
              value={formData.last_name}
              onChangeText={(value) => handleInputChange('last_name', value)}
              autoCapitalize="words"
              returnKeyType="next"
              blurOnSubmit={false}
            />
            {errors.last_name && <Text style={styles.errorText}>{errors.last_name}</Text>}
          </View>
        </View>

        {/* Email */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Email Address *</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.email && styles.textInputError
            ]}
            placeholder="customer@example.com"
            placeholderTextColor={colors.text.secondary}
            value={formData.email}
            onChangeText={(value) => handleInputChange('email', value)}
            keyboardType="email-address"
            autoCapitalize="none"
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
        </View>

        {/* NIC */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>NIC Number *</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.nic && styles.textInputError
            ]}
            placeholder="123456789V or 123456789012"
            placeholderTextColor={colors.text.secondary}
            value={formData.nic}
            onChangeText={(value) => handleInputChange('nic', value)}
            autoCapitalize="characters"
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.nic && <Text style={styles.errorText}>{errors.nic}</Text>}
          <Text style={styles.inputHint}>
            Enter NIC in format: 123456789V (old) or 123456789012 (new)
          </Text>
        </View>

        {/* Phone Number */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Phone Number</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.phone_number && styles.textInputError
            ]}
            placeholder="0771234567 or +94771234567"
            placeholderTextColor={colors.text.secondary}
            value={formData.phone_number}
            onChangeText={(value) => handleInputChange('phone_number', value)}
            keyboardType="phone-pad"
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.phone_number && <Text style={styles.errorText}>{errors.phone_number}</Text>}
        </View>

        {/* Address */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Address</Text>
          <TextInput
            style={[
              styles.textInput,
              styles.textArea,
              errors.address && styles.textInputError
            ]}
            placeholder="Customer address (optional)"
            placeholderTextColor={colors.text.secondary}
            value={formData.address}
            onChangeText={(value) => handleInputChange('address', value)}
            multiline
            numberOfLines={3}
            returnKeyType="done"
            blurOnSubmit={false}
          />
          {errors.address && <Text style={styles.errorText}>{errors.address}</Text>}
        </View>

        {/* Status Toggles */}
        <View style={styles.rowContainer}>
          <View style={styles.halfInput}>
            <Text style={styles.inputLabel}>Verification Status</Text>
            <View style={styles.toggleContainer}>
              <TouchableOpacity
                style={[
                  styles.toggleButton,
                  formData.is_verified ? styles.toggleActive : styles.toggleInactive
                ]}
                onPress={() => handleInputChange('is_verified', !formData.is_verified)}
              >
                <Text style={[
                  styles.toggleText,
                  formData.is_verified ? styles.toggleTextActive : styles.toggleTextInactive
                ]}>
                  {formData.is_verified ? 'Verified' : 'Unverified'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.halfInput}>
            <Text style={styles.inputLabel}>Account Status</Text>
            <View style={styles.toggleContainer}>
              <TouchableOpacity
                style={[
                  styles.toggleButton,
                  formData.is_active ? styles.toggleActive : styles.toggleInactive
                ]}
                onPress={() => handleInputChange('is_active', !formData.is_active)}
              >
                <Text style={[
                  styles.toggleText,
                  formData.is_active ? styles.toggleTextActive : styles.toggleTextInactive
                ]}>
                  {formData.is_active ? 'Active' : 'Inactive'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Bottom spacing for submit button */}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Submit Button */}
      <View style={styles.submitContainer}>
        <TouchableOpacity
          style={[
            styles.submitButton,
            (!isFormValid || loading) && styles.submitButtonDisabled
          ]}
          onPress={handleSubmit}
          disabled={!isFormValid || loading}
        >
          {loading ? (
            <ActivityIndicator color={colors.white} size="small" />
          ) : (
            <Text style={styles.submitButtonText}>
              {isEditMode ? 'Update Customer' : 'Create Customer'}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingTop: Platform.OS === 'ios' ? 60 : 20,
  },
  backButton: {
    marginRight: 16,
    padding: 4,
  },
  headerContent: {
    flex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text.primary,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: colors.text.secondary,
  },
  form: {
    flex: 1,
    paddingHorizontal: 20,
  },
  formContent: {
    paddingTop: 24,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text.primary,
    marginBottom: 8,
  },
  inputHint: {
    fontSize: 14,
    color: colors.text.secondary,
    marginTop: 4,
    fontStyle: 'italic',
  },
  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    backgroundColor: colors.surface,
    color: colors.text.primary,
  },
  textInputError: {
    borderColor: colors.danger,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
    paddingTop: 14,
  },
  errorText: {
    color: colors.danger,
    fontSize: 14,
    marginTop: 4,
    marginLeft: 4,
  },
  rowContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: -10,
    marginBottom: 20,
  },
  halfInput: {
    flex: 1,
    marginHorizontal: 10,
  },
  toggleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  toggleButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    minWidth: 100,
    alignItems: 'center',
  },
  toggleActive: {
    backgroundColor: colors.primary,
  },
  toggleInactive: {
    backgroundColor: colors.text.secondary,
  },
  toggleText: {
    fontSize: 14,
    fontWeight: '600',
  },
  toggleTextActive: {
    color: colors.white,
  },
  toggleTextInactive: {
    color: colors.white,
  },
  submitContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 20,
    backgroundColor: colors.background,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  submitButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: colors.text.secondary,
  },
  submitButtonText: {
    color: colors.white,
    fontSize: 18,
    fontWeight: '600',
  },
});

export default CreateCustomerScreen;