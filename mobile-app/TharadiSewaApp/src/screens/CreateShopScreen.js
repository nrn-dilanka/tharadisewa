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
  Modal,
  FlatList,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import * as Location from 'expo-location';

import { colors } from '../constants/colors';
import shopService from '../services/shopService';
import customerService from '../services/customerService';

const CreateShopScreen = ({ navigation, route }) => {
  // Check if we're in edit mode and have shop data
  const isEditMode = route?.params?.shop ? true : false;
  const existingShop = route?.params?.shop || null;

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    address_line_1: '',
    address_line_2: '',
    address_line_3: '',
    city: '',
    postal_code: '',
    phone_number: '',
    email: '',
    customer: null,
    is_active: true,
  });

  // UI state
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [customersLoading, setCustomersLoading] = useState(false);
  const [customerPickerVisible, setCustomerPickerVisible] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [locationPermission, setLocationPermission] = useState(null);

  // Initialize form data and load customers on component mount
  useEffect(() => {
    loadCustomers();
    requestLocationPermission();
    
    if (isEditMode && existingShop) {
      setFormData({
        name: existingShop.name || '',
        description: existingShop.description || '',
        address_line_1: existingShop.address_line_1 || '',
        address_line_2: existingShop.address_line_2 || '',
        address_line_3: existingShop.address_line_3 || '',
        city: existingShop.city || '',
        postal_code: existingShop.postal_code || '',
        phone_number: existingShop.phone_number || '',
        email: existingShop.email || '',
        customer: existingShop.customer || null,
        is_active: existingShop.is_active !== undefined ? existingShop.is_active : true,
      });
    }
  }, [isEditMode, existingShop]);

  // Load customers for selection
  const loadCustomers = async () => {
    setCustomersLoading(true);
    try {
      const result = await customerService.getAllCustomers();
      console.log('Load customers result:', result);
      console.log('Load customers data:', result.data);
      console.log('Load customers results:', result.data?.results);
      
      if (result.success && result.data) {
        // Handle paginated response structure
        let customersData = [];
        if (result.data.results && Array.isArray(result.data.results)) {
          // Paginated response
          customersData = result.data.results;
        } else if (Array.isArray(result.data)) {
          // Direct array response
          customersData = result.data;
        }
        
        console.log('Processed customers data:', customersData);
        const activeCustomers = customersData.filter(customer => customer.is_active);
        console.log('Active customers:', activeCustomers);
        setCustomers(activeCustomers);
      } else {
        console.error('Invalid response structure:', result);
        Alert.alert('Error', 'Invalid customer data received');
      }
    } catch (error) {
      console.error('Load customers error:', error);
      Alert.alert('Error', 'Failed to load customers');
    } finally {
      setCustomersLoading(false);
    }
  };

  // Request location permissions
  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      setLocationPermission(status);
      
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Location permission is required to automatically set shop location. You can still create shops manually without location.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('Location permission error:', error);
      setLocationPermission('denied');
    }
  };

  // Get current GPS location
  const getCurrentLocation = async () => {
    if (locationPermission !== 'granted') {
      Alert.alert(
        'Location Permission Required',
        'Please grant location permission to automatically capture shop location.',
        [
          { text: 'Cancel' },
          { 
            text: 'Settings', 
            onPress: async () => {
              const { status } = await Location.requestForegroundPermissionsAsync();
              setLocationPermission(status);
            }
          }
        ]
      );
      return;
    }

    setLocationLoading(true);
    try {
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
        maximumAge: 10000, // 10 seconds
        timeout: 15000,    // 15 seconds
      });

      const { latitude, longitude, accuracy } = location.coords;
      setCurrentLocation({
        latitude: latitude.toFixed(8),
        longitude: longitude.toFixed(8),
        accuracy: Math.round(accuracy) || null,
      });

      Alert.alert(
        'Location Captured',
        `Location successfully captured!\nLatitude: ${latitude.toFixed(6)}\nLongitude: ${longitude.toFixed(6)}${accuracy ? `\nAccuracy: ±${Math.round(accuracy)}m` : ''}`,
        [{ text: 'OK' }]
      );

    } catch (error) {
      console.error('Get location error:', error);
      Alert.alert(
        'Location Error',
        'Failed to get current location. Please ensure GPS is enabled and try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setLocationLoading(false);
    }
  };

  // Clear captured location
  const clearLocation = () => {
    setCurrentLocation(null);
    Alert.alert('Location Cleared', 'GPS location has been cleared.');
  };

  // Memoized validation function
  const validateForm = useCallback((data) => {
    const newErrors = {};

    // Name validation
    if (!data.name || data.name.trim().length === 0) {
      newErrors.name = 'Shop name is required';
    } else if (data.name.trim().length < 2) {
      newErrors.name = 'Shop name must be at least 2 characters';
    } else if (data.name.trim().length > 255) {
      newErrors.name = 'Shop name must be less than 255 characters';
    }

    // Customer validation
    if (!data.customer) {
      newErrors.customer = 'Customer is required';
    }

    // Address validation
    if (!data.address_line_1 || data.address_line_1.trim().length === 0) {
      newErrors.address_line_1 = 'Address is required';
    } else if (data.address_line_1.trim().length < 5) {
      newErrors.address_line_1 = 'Address must be at least 5 characters';
    } else if (data.address_line_1.trim().length > 255) {
      newErrors.address_line_1 = 'Address must be less than 255 characters';
    }

    // City validation
    if (!data.city || data.city.trim().length === 0) {
      newErrors.city = 'City is required';
    } else if (data.city.trim().length > 100) {
      newErrors.city = 'City must be less than 100 characters';
    }

    // Postal code validation
    if (!data.postal_code || data.postal_code.trim().length === 0) {
      newErrors.postal_code = 'Postal code is required';
    } else if (!/^[0-9]{5}$/.test(data.postal_code.trim())) {
      newErrors.postal_code = 'Postal code must be exactly 5 digits';
    }

    // Phone number validation (optional but if provided must be valid)
    if (data.phone_number && data.phone_number.trim() !== '') {
      if (!/^(\+94|0)?[0-9]{9}$/.test(data.phone_number.replace(/\s/g, ''))) {
        newErrors.phone_number = 'Please enter a valid phone number';
      }
    }

    // Email validation (optional but if provided must be valid)
    if (data.email && data.email.trim() !== '') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.email.trim())) {
        newErrors.email = 'Please enter a valid email address';
      }
    }

    // Description validation
    if (data.description && data.description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters';
    }

    // Optional address line validations
    if (data.address_line_2 && data.address_line_2.length > 255) {
      newErrors.address_line_2 = 'Address line 2 must be less than 255 characters';
    }

    if (data.address_line_3 && data.address_line_3.length > 255) {
      newErrors.address_line_3 = 'Address line 3 must be less than 255 characters';
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
    console.log('CreateShopScreen handleSubmit - Form data:', formData);
    
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
      const shopData = {
        name: formData.name.trim(),
        customer: formData.customer,
        address_line_1: formData.address_line_1.trim(),
        city: formData.city.trim(),
        postal_code: formData.postal_code.trim(),
        is_active: formData.is_active,
      };

      // Add optional fields only if they have values
      if (formData.description && formData.description.trim()) {
        shopData.description = formData.description.trim();
      }

      if (formData.address_line_2 && formData.address_line_2.trim()) {
        shopData.address_line_2 = formData.address_line_2.trim();
      }

      if (formData.address_line_3 && formData.address_line_3.trim()) {
        shopData.address_line_3 = formData.address_line_3.trim();
      }

      if (formData.phone_number && formData.phone_number.trim()) {
        shopData.phone_number = formData.phone_number.trim();
      }

      if (formData.email && formData.email.trim()) {
        shopData.email = formData.email.trim();
      }

      // Add GPS location data if available (only for new shops)
      if (!isEditMode && currentLocation) {
        shopData.latitude = currentLocation.latitude;
        shopData.longitude = currentLocation.longitude;
        shopData.location_accuracy = currentLocation.accuracy;
        shopData.location_name = `${formData.name.trim()} Location`;
        shopData.location_description = `GPS location for ${formData.name.trim()}`;
      }

      console.log('CreateShopScreen - Sending shop data:', shopData);

      let result;
      if (isEditMode) {
        result = await shopService.updateShop(existingShop.id, shopData);
      } else {
        result = await shopService.createShop(shopData);
      }

      console.log('CreateShopScreen - API result:', result);

      if (result.success) {
        Alert.alert(
          'Success', 
          isEditMode ? 'Shop updated successfully!' : 'Shop created successfully!',
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
      console.error('Submit shop error:', error);
      Alert.alert('Error', 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [formData, validateForm, errors, isEditMode, existingShop, navigation]);

  // Memoized customer selection
  const selectedCustomer = useMemo(() => {
    return formData.customer ? customers.find(c => c.id === formData.customer) : null;
  }, [formData.customer, customers]);

  // Memoized form validity check
  const isFormValid = useMemo(() => {
    const validationErrors = validateForm(formData);
    return Object.keys(validationErrors).length === 0 && formData.name.trim() !== '' && formData.customer;
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
            {isEditMode ? 'Edit Shop' : 'Create New Shop'}
          </Text>
          <Text style={styles.subtitle}>
            {isEditMode ? 'Update shop information' : 'Add a new shop to your system'}
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
        {/* Shop Name */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Shop Name *</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.name && styles.textInputError
            ]}
            placeholder="Enter shop name"
            placeholderTextColor={colors.text.secondary}
            value={formData.name}
            onChangeText={(value) => handleInputChange('name', value)}
            autoCapitalize="words"
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.name && <Text style={styles.errorText}>{errors.name}</Text>}
        </View>

        {/* Customer Selection */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Customer *</Text>
          <TouchableOpacity
            style={[
              styles.customerPicker,
              errors.customer && styles.customerPickerError
            ]}
            onPress={() => setCustomerPickerVisible(true)}
            disabled={customersLoading}
          >
            {customersLoading ? (
              <ActivityIndicator size="small" color={colors.primary} />
            ) : (
              <Text style={[
                styles.customerPickerText,
                !selectedCustomer && styles.customerPickerPlaceholder
              ]}>
                {selectedCustomer ? selectedCustomer.full_name : 'Select a customer'}
              </Text>
            )}
            <MaterialIcons name="arrow-drop-down" size={24} color={colors.text.secondary} />
          </TouchableOpacity>
          {errors.customer && <Text style={styles.errorText}>{errors.customer}</Text>}
        </View>

        {/* Description */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Description</Text>
          <TextInput
            style={[
              styles.textInput,
              styles.textArea,
              errors.description && styles.textInputError
            ]}
            placeholder="Shop description (optional)"
            placeholderTextColor={colors.text.secondary}
            value={formData.description}
            onChangeText={(value) => handleInputChange('description', value)}
            multiline
            numberOfLines={3}
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.description && <Text style={styles.errorText}>{errors.description}</Text>}
        </View>

        {/* Address Line 1 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Address Line 1 *</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.address_line_1 && styles.textInputError
            ]}
            placeholder="Street address, building number"
            placeholderTextColor={colors.text.secondary}
            value={formData.address_line_1}
            onChangeText={(value) => handleInputChange('address_line_1', value)}
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.address_line_1 && <Text style={styles.errorText}>{errors.address_line_1}</Text>}
        </View>

        {/* Address Line 2 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Address Line 2</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.address_line_2 && styles.textInputError
            ]}
            placeholder="Apartment, suite, etc. (optional)"
            placeholderTextColor={colors.text.secondary}
            value={formData.address_line_2}
            onChangeText={(value) => handleInputChange('address_line_2', value)}
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.address_line_2 && <Text style={styles.errorText}>{errors.address_line_2}</Text>}
        </View>

        {/* Address Line 3 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Address Line 3</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.address_line_3 && styles.textInputError
            ]}
            placeholder="Additional address info (optional)"
            placeholderTextColor={colors.text.secondary}
            value={formData.address_line_3}
            onChangeText={(value) => handleInputChange('address_line_3', value)}
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.address_line_3 && <Text style={styles.errorText}>{errors.address_line_3}</Text>}
        </View>

        {/* City and Postal Code */}
        <View style={styles.rowContainer}>
          <View style={styles.halfInput}>
            <Text style={styles.inputLabel}>City *</Text>
            <TextInput
              style={[
                styles.textInput,
                errors.city && styles.textInputError
              ]}
              placeholder="City"
              placeholderTextColor={colors.text.secondary}
              value={formData.city}
              onChangeText={(value) => handleInputChange('city', value)}
              autoCapitalize="words"
              returnKeyType="next"
              blurOnSubmit={false}
            />
            {errors.city && <Text style={styles.errorText}>{errors.city}</Text>}
          </View>

          <View style={styles.halfInput}>
            <Text style={styles.inputLabel}>Postal Code *</Text>
            <TextInput
              style={[
                styles.textInput,
                errors.postal_code && styles.textInputError
              ]}
              placeholder="12345"
              placeholderTextColor={colors.text.secondary}
              value={formData.postal_code}
              onChangeText={(value) => handleInputChange('postal_code', value)}
              keyboardType="numeric"
              maxLength={5}
              returnKeyType="next"
              blurOnSubmit={false}
            />
            {errors.postal_code && <Text style={styles.errorText}>{errors.postal_code}</Text>}
          </View>
        </View>

        {/* Phone Number */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Phone Number</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.phone_number && styles.textInputError
            ]}
            placeholder="0771234567"
            placeholderTextColor={colors.text.secondary}
            value={formData.phone_number}
            onChangeText={(value) => handleInputChange('phone_number', value)}
            keyboardType="phone-pad"
            returnKeyType="next"
            blurOnSubmit={false}
          />
          {errors.phone_number && <Text style={styles.errorText}>{errors.phone_number}</Text>}
        </View>

        {/* Email */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Email</Text>
          <TextInput
            style={[
              styles.textInput,
              errors.email && styles.textInputError
            ]}
            placeholder="shop@example.com"
            placeholderTextColor={colors.text.secondary}
            value={formData.email}
            onChangeText={(value) => handleInputChange('email', value)}
            keyboardType="email-address"
            autoCapitalize="none"
            returnKeyType="done"
            blurOnSubmit={false}
          />
          {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
        </View>

        {/* Status Toggle */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Shop Status</Text>
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

        {/* GPS Location Section (only for new shops) */}
        {!isEditMode && (
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>GPS Location (Optional)</Text>
            <Text style={styles.inputHint}>
              Capture your current location to automatically set shop coordinates
            </Text>
            
            {currentLocation ? (
              <View style={styles.locationCaptured}>
                <View style={styles.locationInfo}>
                  <MaterialIcons name="location-on" size={24} color={colors.success} />
                  <View style={styles.locationDetails}>
                    <Text style={styles.locationText}>
                      Latitude: {currentLocation.latitude}
                    </Text>
                    <Text style={styles.locationText}>
                      Longitude: {currentLocation.longitude}
                    </Text>
                    {currentLocation.accuracy && (
                      <Text style={styles.locationAccuracy}>
                        Accuracy: ±{currentLocation.accuracy}m
                      </Text>
                    )}
                  </View>
                </View>
                <View style={styles.locationButtons}>
                  <TouchableOpacity
                    style={styles.locationButtonSecondary}
                    onPress={clearLocation}
                  >
                    <MaterialIcons name="clear" size={16} color={colors.danger} />
                    <Text style={styles.locationButtonSecondaryText}>Clear</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.locationButtonPrimary}
                    onPress={getCurrentLocation}
                    disabled={locationLoading}
                  >
                    {locationLoading ? (
                      <ActivityIndicator size="small" color={colors.white} />
                    ) : (
                      <>
                        <MaterialIcons name="refresh" size={16} color={colors.white} />
                        <Text style={styles.locationButtonText}>Update</Text>
                      </>
                    )}
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <TouchableOpacity
                style={[
                  styles.locationCaptureButton,
                  (locationLoading || locationPermission !== 'granted') && styles.locationCaptureButtonDisabled
                ]}
                onPress={getCurrentLocation}
                disabled={locationLoading || locationPermission !== 'granted'}
              >
                {locationLoading ? (
                  <ActivityIndicator size="small" color={colors.primary} />
                ) : (
                  <MaterialIcons name="my-location" size={24} color={
                    locationPermission === 'granted' ? colors.primary : colors.text.secondary
                  } />
                )}
                <Text style={[
                  styles.locationCaptureText,
                  locationPermission !== 'granted' && styles.locationCaptureTextDisabled
                ]}>
                  {locationLoading ? 'Getting Location...' : 
                   locationPermission !== 'granted' ? 'Location Permission Required' :
                   'Capture Current Location'}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}

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
              {isEditMode ? 'Update Shop' : 'Create Shop'}
            </Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Customer Picker Modal */}
      <Modal
        visible={customerPickerVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setCustomerPickerVisible(false)}
        onShow={() => {
          console.log('Modal shown, customers array length:', customers.length);
          console.log('Modal shown, customers data:', customers);
        }}
      >
        <View style={styles.pickerOverlay}>
          <View style={styles.pickerModal}>
            <View style={styles.pickerHeader}>
              <Text style={styles.pickerTitle}>Select Customer</Text>
              <TouchableOpacity
                style={styles.pickerCloseButton}
                onPress={() => setCustomerPickerVisible(false)}
              >
                <MaterialIcons name="close" size={24} color={colors.text.secondary} />
              </TouchableOpacity>
            </View>
            
            {/* Debug info */}
            <View style={{ padding: 10, backgroundColor: '#f0f0f0' }}>
              <Text style={{ fontSize: 12, color: '#333' }}>
                DEBUG: {customers.length} customers loaded
              </Text>
            </View>
            
            <FlatList
              data={customers}
              keyExtractor={(item) => item.id.toString()}
              style={styles.customerList}
              showsVerticalScrollIndicator={true}
              nestedScrollEnabled={true}
              onLayout={(event) => {
                const { height } = event.nativeEvent.layout;
                console.log('FlatList layout height:', height);
              }}
              getItemLayout={(data, index) => {
                console.log('FlatList getItemLayout called for index:', index);
                return { length: 60, offset: 60 * index, index };
              }}
              renderItem={({ item, index }) => {
                console.log('Rendering customer item at index:', index, item);
                return (
                  <TouchableOpacity
                    style={styles.customerItem}
                    onPress={() => {
                      console.log('Selected customer:', item);
                      handleInputChange('customer', item.id);
                      setCustomerPickerVisible(false);
                    }}
                  >
                    <Text style={styles.customerItemName}>{item.full_name}</Text>
                    <Text style={styles.customerItemDetails}>
                      {item.email} • {item.phone_number || 'No phone'}
                    </Text>
                  </TouchableOpacity>
                );
              }}
              ListEmptyComponent={() => {
                console.log('Customer list is empty, customers array:', customers);
                return (
                  <View style={styles.emptyCustomerContainer}>
                    <Text style={styles.emptyCustomerText}>
                      {customersLoading ? 'Loading customers...' : 'No customers available'}
                    </Text>
                    {!customersLoading && customers.length === 0 && (
                      <Text style={styles.emptyCustomerSubtext}>
                        Please add customers first before creating a shop.
                      </Text>
                    )}
                  </View>
                );
              }}
            />
          </View>
        </View>
      </Modal>
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
    fontSize: 16,
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
  
  // Customer Picker Styles
  customerPicker: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 16,
    backgroundColor: colors.surface,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 50,
  },
  customerPickerError: {
    borderColor: colors.danger,
  },
  customerPickerText: {
    fontSize: 16,
    color: colors.text.primary,
    flex: 1,
  },
  customerPickerPlaceholder: {
    color: colors.text.secondary,
  },
  
  // Picker Modal Styles
  pickerOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  pickerModal: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    width: '100%',
    maxWidth: 400,
    height: '70%',
    minHeight: 300,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  pickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  pickerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text.primary,
  },
  pickerCloseButton: {
    padding: 4,
  },
  customerList: {
    flex: 1,
    minHeight: 200,
  },
  customerItem: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.surface,
    minHeight: 60,
  },
  customerItemName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text.primary,
    marginBottom: 4,
  },
  customerItemDetails: {
    fontSize: 14,
    color: colors.text.secondary,
  },
  emptyCustomerContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyCustomerText: {
    textAlign: 'center',
    fontSize: 16,
    color: colors.text.secondary,
    marginBottom: 8,
  },
  emptyCustomerSubtext: {
    textAlign: 'center',
    fontSize: 14,
    color: colors.text.secondary,
    fontStyle: 'italic',
  },

  // GPS Location Styles
  inputHint: {
    fontSize: 14,
    color: colors.text.secondary,
    marginBottom: 12,
    fontStyle: 'italic',
  },
  locationCaptureButton: {
    borderWidth: 2,
    borderColor: colors.primary,
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
  },
  locationCaptureButtonDisabled: {
    borderColor: colors.text.secondary,
    opacity: 0.6,
  },
  locationCaptureText: {
    fontSize: 16,
    color: colors.primary,
    marginTop: 8,
    fontWeight: '600',
  },
  locationCaptureTextDisabled: {
    color: colors.text.secondary,
  },
  locationCaptured: {
    borderWidth: 1,
    borderColor: colors.success,
    borderRadius: 12,
    padding: 16,
    backgroundColor: '#f0fff0',
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  locationDetails: {
    flex: 1,
    marginLeft: 12,
  },
  locationText: {
    fontSize: 14,
    color: colors.text.primary,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 2,
  },
  locationAccuracy: {
    fontSize: 12,
    color: colors.text.secondary,
    marginTop: 4,
  },
  locationButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  locationButtonPrimary: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 4,
  },
  locationButtonSecondary: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'transparent',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.danger,
    gap: 4,
  },
  locationButtonText: {
    color: colors.white,
    fontSize: 14,
    fontWeight: '600',
  },
  locationButtonSecondaryText: {
    color: colors.danger,
    fontSize: 14,
    fontWeight: '600',
  },
});

export default CreateShopScreen;