import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Modal,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import CustomTextInput from './CustomTextInput';
import CustomButton from './CustomButton';
import { colors } from '../constants/colors';
import customerService from '../services/customerService';

// Validation schemas
const customerSchema = yup.object().shape({
  first_name: yup
    .string()
    .required('First name is required')
    .min(1, 'First name is required')
    .max(30, 'First name must be less than 30 characters'),
  
  last_name: yup
    .string()
    .required('Last name is required')
    .min(1, 'Last name is required')
    .max(30, 'Last name must be less than 30 characters'),
  
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address'),
  
  phone_number: yup
    .string()
    .matches(
      /^(\+94|0)?[0-9]{9}$/,
      'Please enter a valid phone number'
    ),
  
  nic: yup
    .string()
    .required('NIC is required')
    .matches(
      /^(?:\d{9}[vVxX]|\d{12})$/,
      'NIC must be in format: 123456789V or 123456789012'
    ),
  
  address: yup
    .string()
    .max(500, 'Address must be less than 500 characters'),
  
  date_of_birth: yup
    .date()
    .max(new Date(), 'Date of birth cannot be in the future')
    .nullable(),
});

const productSchema = yup.object().shape({
  name: yup
    .string()
    .required('Product name is required')
    .min(2, 'Product name must be at least 2 characters')
    .max(100, 'Product name must be less than 100 characters'),
  
  description: yup
    .string()
    .max(1000, 'Description must be less than 1000 characters'),
  
  price: yup
    .number()
    .required('Price is required')
    .positive('Price must be positive')
    .max(999999.99, 'Price is too high'),
  
  stock_quantity: yup
    .number()
    .required('Stock quantity is required')
    .integer('Stock quantity must be a whole number')
    .min(0, 'Stock quantity cannot be negative'),
  
  category: yup
    .string()
    .max(50, 'Category must be less than 50 characters'),
  
  brand: yup
    .string()
    .max(50, 'Brand must be less than 50 characters'),
  
  model: yup
    .string()
    .max(50, 'Model must be less than 50 characters'),
});

const shopSchema = yup.object().shape({
  name: yup
    .string()
    .required('Shop name is required')
    .min(2, 'Shop name must be at least 2 characters')
    .max(100, 'Shop name must be less than 100 characters'),
  
  description: yup
    .string()
    .max(500, 'Description must be less than 500 characters'),
  
  address_line_1: yup
    .string()
    .required('Address is required')
    .min(5, 'Address must be at least 5 characters')
    .max(200, 'Address must be less than 200 characters'),
  
  city: yup
    .string()
    .required('City is required')
    .max(50, 'City must be less than 50 characters'),
  
  postal_code: yup
    .string()
    .required('Postal code is required')
    .matches(/^[0-9]{5}$/, 'Postal code must be 5 digits'),
  
  phone_number: yup
    .string()
    .matches(
      /^(\+94|0)?[0-9]{9}$/,
      'Please enter a valid phone number'
    ),
  
  email: yup
    .string()
    .email('Please enter a valid email address'),
    
  customer: yup
    .number()
    .required('Customer is required')
    .positive('Please select a customer'),
});

const CrudModalForm = ({ 
  visible, 
  type, // 'customer', 'product', 'shop'
  mode, // 'create' or 'edit'
  initialData = null,
  onSave,
  onCancel,
  loading = false 
}) => {
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [customersLoading, setCustomersLoading] = useState(false);
  const [customerPickerVisible, setCustomerPickerVisible] = useState(false);

  // Get appropriate schema based on type
  const getValidationSchema = () => {
    switch (type) {
      case 'customer': return customerSchema;
      case 'product': return productSchema;
      case 'shop': return shopSchema;
      default: return yup.object().shape({});
    }
  };

  // Get default values based on type
  const getDefaultValues = () => {
    const baseDefaults = {
      customer: {
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        nic: '',
        address: '',
        date_of_birth: '',
      },
      product: {
        name: '',
        description: '',
        price: '',
        stock_quantity: '',
        category: '',
        brand: '',
        model: '',
      },
      shop: {
        name: '',
        description: '',
        address_line_1: '',
        address_line_2: '',
        address_line_3: '',
        city: '',
        postal_code: '',
        phone_number: '',
        email: '',
        customer: '',
      },
    };

    return initialData ? { ...baseDefaults[type], ...initialData } : baseDefaults[type];
  };

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    watch,
    trigger,
    setValue,
  } = useForm({
    resolver: yupResolver(getValidationSchema()),
    mode: 'onChange',
    defaultValues: getDefaultValues(),
  });

  const formValues = watch();

  useEffect(() => {
    if (visible) {
      reset(getDefaultValues());
      if (type === 'shop') {
        loadCustomers();
      }
    }
  }, [visible, initialData, type]);

  const loadCustomers = async () => {
    setCustomersLoading(true);
    try {
      const result = await customerService.getAllCustomers();
      if (result.success) {
        const customersData = result.data.results || result.data || [];
        setCustomers(customersData.filter(customer => customer.is_active));
      }
    } catch (error) {
      console.error('Load customers error:', error);
      Alert.alert('Error', 'Failed to load customers');
    } finally {
      setCustomersLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      console.log('CrudModalForm onSubmit - Raw data:', data);
      
      // Clean up data before sending
      const cleanedData = {};
      Object.keys(data).forEach(key => {
        if (data[key] !== '' && data[key] !== null && data[key] !== undefined) {
          cleanedData[key] = data[key];
        }
      });

      console.log('CrudModalForm onSubmit - Cleaned data:', cleanedData);
      
      await onSave(cleanedData);
    } catch (error) {
      console.error('CrudModalForm onSubmit error:', error);
      Alert.alert('Error', 'Failed to save. Please try again.');
    }
  };

  const renderCustomerFields = () => (
    <>
      <View style={styles.nameContainer}>
        <View style={styles.nameField}>
          <Controller
            control={control}
            name="first_name"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="First Name *"
                placeholder="Enter first name"
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
                placeholder="Enter last name"
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
            placeholder="customer@example.com"
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
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="phone_number"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Phone Number"
            placeholder="0771234567"
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
          />
        )}
      />

      <Controller
        control={control}
        name="nic"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="NIC *"
            placeholder="123456789V or 123456789012"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('nic');
            }}
            onBlur={onBlur}
            error={errors.nic?.message}
            touched={!!errors.nic}
            autoCapitalize="characters"
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="address"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Address"
            placeholder="Enter full address"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('address');
            }}
            onBlur={onBlur}
            error={errors.address?.message}
            touched={!!errors.address}
            multiline
            numberOfLines={3}
            returnKeyType="done"
          />
        )}
      />
    </>
  );

  const renderProductFields = () => (
    <>
      <Controller
        control={control}
        name="name"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Product Name *"
            placeholder="Enter product name"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('name');
            }}
            onBlur={onBlur}
            error={errors.name?.message}
            touched={!!errors.name}
            autoCapitalize="words"
            returnKeyType="next"
            blurOnSubmit={false}
          />
        )}
      />

      <Controller
        control={control}
        name="description"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Description"
            placeholder="Product description"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('description');
            }}
            onBlur={onBlur}
            error={errors.description?.message}
            touched={!!errors.description}
            multiline
            numberOfLines={3}
            returnKeyType="next"
            blurOnSubmit={false}
          />
        )}
      />

      <View style={styles.priceContainer}>
        <View style={styles.priceField}>
          <Controller
            control={control}
            name="price"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Price *"
                placeholder="0.00"
                value={value ? value.toString() : ''}
                onChangeText={(text) => {
                  if (text === '') {
                    onChange('');
                  } else {
                    const numericValue = parseFloat(text);
                    onChange(isNaN(numericValue) ? '' : numericValue);
                  }
                  trigger('price');
                }}
                onBlur={onBlur}
                error={errors.price?.message}
                touched={!!errors.price}
                keyboardType="numeric"
                returnKeyType="next"
                blurOnSubmit={false}
              />
            )}
          />
        </View>
        <View style={styles.priceField}>
          <Controller
            control={control}
            name="stock_quantity"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Stock Quantity *"
                placeholder="0"
                value={value ? value.toString() : ''}
                onChangeText={(text) => {
                  if (text === '') {
                    onChange('');
                  } else {
                    const numericValue = parseInt(text, 10);
                    onChange(isNaN(numericValue) ? '' : numericValue);
                  }
                  trigger('stock_quantity');
                }}
                onBlur={onBlur}
                error={errors.stock_quantity?.message}
                touched={!!errors.stock_quantity}
                keyboardType="numeric"
                returnKeyType="next"
                blurOnSubmit={false}
              />
            )}
          />
        </View>
      </View>

      <View style={styles.nameContainer}>
        <View style={styles.nameField}>
          <Controller
            control={control}
            name="category"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Category"
                placeholder="Product category"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('category');
                }}
                onBlur={onBlur}
                error={errors.category?.message}
                touched={!!errors.category}
                autoCapitalize="words"
                returnKeyType="next"
              />
            )}
          />
        </View>
        <View style={styles.nameField}>
          <Controller
            control={control}
            name="brand"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Brand"
                placeholder="Product brand"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('brand');
                }}
                onBlur={onBlur}
                error={errors.brand?.message}
                touched={!!errors.brand}
                autoCapitalize="words"
                returnKeyType="next"
              />
            )}
          />
        </View>
      </View>

      <Controller
        control={control}
        name="model"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Model"
            placeholder="Product model"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('model');
            }}
            onBlur={onBlur}
            error={errors.model?.message}
            touched={!!errors.model}
            returnKeyType="done"
          />
        )}
      />
    </>
  );

  const renderShopFields = () => (
    <>
      <Controller
        control={control}
        name="name"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Shop Name *"
            placeholder="Enter shop name"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('name');
            }}
            onBlur={onBlur}
            error={errors.name?.message}
            touched={!!errors.name}
            autoCapitalize="words"
            returnKeyType="next"
          />
        )}
      />

      {/* Customer Selection */}
      <View style={styles.customerPickerContainer}>
        <Text style={styles.inputLabel}>Customer *</Text>
        <Controller
          control={control}
          name="customer"
          render={({ field: { onChange, value } }) => (
            <>
              <TouchableOpacity
                style={[styles.customerPicker, errors.customer && styles.customerPickerError]}
                onPress={() => setCustomerPickerVisible(true)}
                disabled={customersLoading}
              >
                {customersLoading ? (
                  <ActivityIndicator size="small" color={colors.primary} />
                ) : (
                  <Text style={[
                    styles.customerPickerText,
                    !value && styles.customerPickerPlaceholder
                  ]}>
                    {value
                      ? customers.find(c => c.id === value)?.full_name || 'Unknown Customer'
                      : 'Select a customer'
                    }
                  </Text>
                )}
              </TouchableOpacity>
              {errors.customer && (
                <Text style={styles.customerPickerErrorText}>{errors.customer.message}</Text>
              )}
            </>
          )}
        />
      </View>

      <Controller
        control={control}
        name="description"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Description"
            placeholder="Shop description"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('description');
            }}
            onBlur={onBlur}
            error={errors.description?.message}
            touched={!!errors.description}
            multiline
            numberOfLines={2}
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="address_line_1"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Address Line 1 *"
            placeholder="Street address, building number"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('address_line_1');
            }}
            onBlur={onBlur}
            error={errors.address_line_1?.message}
            touched={!!errors.address_line_1}
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="address_line_2"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Address Line 2"
            placeholder="Apartment, suite, etc. (optional)"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('address_line_2');
            }}
            onBlur={onBlur}
            error={errors.address_line_2?.message}
            touched={!!errors.address_line_2}
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="address_line_3"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Address Line 3"
            placeholder="Additional address info (optional)"
            value={value}
            onChangeText={(text) => {
              onChange(text);
              trigger('address_line_3');
            }}
            onBlur={onBlur}
            error={errors.address_line_3?.message}
            touched={!!errors.address_line_3}
            returnKeyType="next"
          />
        )}
      />

      <View style={styles.nameContainer}>
        <View style={styles.nameField}>
          <Controller
            control={control}
            name="city"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="City *"
                placeholder="City"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('city');
                }}
                onBlur={onBlur}
                error={errors.city?.message}
                touched={!!errors.city}
                autoCapitalize="words"
                returnKeyType="next"
              />
            )}
          />
        </View>
        <View style={styles.nameField}>
          <Controller
            control={control}
            name="postal_code"
            render={({ field: { onChange, onBlur, value } }) => (
              <CustomTextInput
                label="Postal Code *"
                placeholder="12345"
                value={value}
                onChangeText={(text) => {
                  onChange(text);
                  trigger('postal_code');
                }}
                onBlur={onBlur}
                error={errors.postal_code?.message}
                touched={!!errors.postal_code}
                keyboardType="numeric"
                returnKeyType="next"
              />
            )}
          />
        </View>
      </View>

      <Controller
        control={control}
        name="phone_number"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Phone Number"
            placeholder="0771234567"
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
          />
        )}
      />

      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, onBlur, value } }) => (
          <CustomTextInput
            label="Email"
            placeholder="shop@example.com"
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
            returnKeyType="done"
          />
        )}
      />
    </>
  );

  const renderFields = () => {
    switch (type) {
      case 'customer':
        return renderCustomerFields();
      case 'product':
        return renderProductFields();
      case 'shop':
        return renderShopFields();
      default:
        return <Text>Invalid form type</Text>;
    }
  };

  const getTitle = () => {
    const typeNames = {
      customer: 'Customer',
      product: 'Product',
      shop: 'Shop',
    };
    return `${mode === 'create' ? 'Add' : 'Edit'} ${typeNames[type] || 'Item'}`;
  };

  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.modal}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>{getTitle()}</Text>
            <TouchableOpacity onPress={onCancel} style={styles.closeButton}>
              <Text style={styles.closeText}>✕</Text>
            </TouchableOpacity>
          </View>

          {/* Form */}
          <ScrollView
            style={styles.formContainer}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {renderFields()}
          </ScrollView>

          {/* Actions */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onCancel}
              disabled={loading}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
            
            <CustomButton
              title={loading ? 'Saving...' : 'Save'}
              onPress={handleSubmit(onSubmit)}
              loading={loading}
              disabled={!isValid || loading}
              variant="primary"
              style={styles.saveButton}
            />
          </View>
        </View>
      </KeyboardAvoidingView>

      {/* Customer Picker Modal */}
      <Modal
        visible={customerPickerVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setCustomerPickerVisible(false)}
      >
        <View style={styles.pickerOverlay}>
          <View style={styles.pickerModal}>
            <View style={styles.pickerHeader}>
              <Text style={styles.pickerTitle}>Select Customer</Text>
              <TouchableOpacity
                style={styles.pickerCloseButton}
                onPress={() => setCustomerPickerVisible(false)}
              >
                <Text style={styles.pickerCloseText}>✕</Text>
              </TouchableOpacity>
            </View>
            
            <FlatList
              data={customers}
              keyExtractor={(item) => item.id.toString()}
              style={styles.customerList}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.customerItem}
                  onPress={() => {
                    setValue('customer', item.id);
                    trigger('customer');
                    setCustomerPickerVisible(false);
                  }}
                >
                  <Text style={styles.customerItemName}>{item.full_name}</Text>
                  <Text style={styles.customerItemDetails}>
                    {item.email} • {item.phone_number || 'No phone'}
                  </Text>
                </TouchableOpacity>
              )}
              ListEmptyComponent={
                <Text style={styles.emptyCustomerText}>
                  No customers available
                </Text>
              }
            />
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    zIndex: 1000,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modal: {
    backgroundColor: colors.surface || '#ffffff',
    borderRadius: 12,
    width: '100%',
    maxWidth: 500,
    maxHeight: '90%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border || '#e0e0e0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text?.primary || '#333',
  },
  closeButton: {
    padding: 4,
  },
  closeText: {
    fontSize: 20,
    color: colors.text?.secondary || '#666',
  },
  formContainer: {
    flex: 1,
    padding: 20,
  },
  nameContainer: {
    flexDirection: 'row',
    marginHorizontal: -8,
  },
  nameField: {
    flex: 1,
    marginHorizontal: 8,
  },
  priceContainer: {
    flexDirection: 'row',
    marginHorizontal: -8,
  },
  priceField: {
    flex: 1,
    marginHorizontal: 8,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: colors.border || '#e0e0e0',
  },
  button: {
    flex: 1,
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 8,
  },
  cancelButton: {
    backgroundColor: colors.text?.secondary || '#666',
  },
  cancelButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  saveButton: {
    flex: 1,
    marginHorizontal: 8,
  },
  
  // Customer Picker Styles
  customerPickerContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text?.primary || '#333',
    marginBottom: 8,
  },
  customerPicker: {
    borderWidth: 1,
    borderColor: colors.border || '#e0e0e0',
    borderRadius: 8,
    padding: 16,
    backgroundColor: colors.surface || '#ffffff',
    minHeight: 48,
    justifyContent: 'center',
  },
  customerPickerError: {
    borderColor: colors.danger || '#dc3545',
  },
  customerPickerText: {
    fontSize: 16,
    color: colors.text?.primary || '#333',
  },
  customerPickerPlaceholder: {
    color: colors.text?.secondary || '#666',
  },
  customerPickerErrorText: {
    color: colors.danger || '#dc3545',
    fontSize: 14,
    marginTop: 4,
    marginLeft: 4,
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
    backgroundColor: colors.surface || '#ffffff',
    borderRadius: 12,
    width: '100%',
    maxWidth: 400,
    maxHeight: '70%',
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
    borderBottomColor: colors.border || '#e0e0e0',
  },
  pickerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text?.primary || '#333',
  },
  pickerCloseButton: {
    padding: 4,
  },
  pickerCloseText: {
    fontSize: 18,
    color: colors.text?.secondary || '#666',
  },
  customerList: {
    flex: 1,
  },
  customerItem: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border || '#e0e0e0',
  },
  customerItemName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text?.primary || '#333',
    marginBottom: 4,
  },
  customerItemDetails: {
    fontSize: 14,
    color: colors.text?.secondary || '#666',
  },
  emptyCustomerText: {
    textAlign: 'center',
    fontSize: 16,
    color: colors.text?.secondary || '#666',
    padding: 40,
  },
});

export default CrudModalForm;