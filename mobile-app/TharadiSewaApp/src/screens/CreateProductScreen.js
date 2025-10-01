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
  ActivityIndicator
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

import { colors } from '../constants/colors';
import productService from '../services/productService';

const CreateProductScreen = ({ navigation, route }) => {
  // Check if we're in edit mode and have product data
  const isEditMode = route?.params?.product ? true : false;
  const existingProduct = route?.params?.product || null;

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    stock_quantity: '',
    sku: '',
    is_active: true,
  });

  // UI state
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Initialize form data on component mount
  useEffect(() => {
    if (isEditMode && existingProduct) {
      setFormData({
        name: existingProduct.name || '',
        description: existingProduct.description || '',
        price: existingProduct.price ? existingProduct.price.toString() : '',
        stock_quantity: existingProduct.stock_quantity ? existingProduct.stock_quantity.toString() : '',
        sku: existingProduct.sku || '',
        is_active: existingProduct.is_active !== undefined ? existingProduct.is_active : true,
      });
    }
  }, [isEditMode, existingProduct]);

  // Memoized validation function
  const validateForm = useCallback((data) => {
    const newErrors = {};

    // Name validation
    if (!data.name || data.name.trim().length === 0) {
      newErrors.name = 'Product name is required';
    } else if (data.name.trim().length < 2) {
      newErrors.name = 'Product name must be at least 2 characters';
    } else if (data.name.trim().length > 255) {
      newErrors.name = 'Product name must be less than 255 characters';
    }

    // Price validation
    if (data.price && data.price.trim() !== '') {
      const price = parseFloat(data.price);
      if (isNaN(price) || price < 0) {
        newErrors.price = 'Price must be a valid positive number';
      } else if (price > 999999.99) {
        newErrors.price = 'Price is too high';
      }
    }

    // Stock quantity validation
    if (data.stock_quantity && data.stock_quantity.trim() !== '') {
      const stock = parseInt(data.stock_quantity, 10);
      if (isNaN(stock) || stock < 0) {
        newErrors.stock_quantity = 'Stock quantity must be a valid non-negative number';
      }
    }

    // Description validation
    if (data.description && data.description.length > 1000) {
      newErrors.description = 'Description must be less than 1000 characters';
    }

    // SKU validation
    if (data.sku && data.sku.length > 50) {
      newErrors.sku = 'SKU must be less than 50 characters';
    }

    return newErrors;
  }, []);

  // Memoized form change handler
  const handleInputChange = useCallback((field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  }, [errors]);

  // Memoized form submit handler
  const handleSubmit = useCallback(async () => {
    console.log('CreateProductScreen handleSubmit - Form data:', formData);
    
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
      const productData = {
        name: formData.name.trim(),
        is_active: formData.is_active,
      };

      // Add optional fields only if they have values
      if (formData.description && formData.description.trim()) {
        productData.description = formData.description.trim();
      }

      if (formData.price && formData.price.trim()) {
        const price = parseFloat(formData.price);
        if (!isNaN(price)) {
          productData.price = price;
        }
      }

      if (formData.stock_quantity && formData.stock_quantity.trim()) {
        const stock = parseInt(formData.stock_quantity, 10);
        if (!isNaN(stock)) {
          productData.stock_quantity = stock;
        }
      }

      if (formData.sku && formData.sku.trim()) {
        productData.sku = formData.sku.trim();
      }

      console.log('CreateProductScreen - Sending product data:', productData);

      let result;
      if (isEditMode) {
        result = await productService.updateProduct(existingProduct.id, productData);
      } else {
        result = await productService.createProduct(productData);
      }

      console.log('CreateProductScreen - API result:', result);

      if (result.success) {
        Alert.alert(
          'Success',
          result.message || `Product ${isEditMode ? 'updated' : 'created'} successfully`,
          [
            {
              text: 'OK',
              onPress: () => {
                // Navigate back or to product list
                navigation.goBack();
              }
            }
          ]
        );
      } else {
        // Handle API errors
        if (result.error && typeof result.error === 'object') {
          const apiErrors = {};
          Object.keys(result.error).forEach(key => {
            if (Array.isArray(result.error[key])) {
              apiErrors[key] = result.error[key][0];
            } else {
              apiErrors[key] = result.error[key];
            }
          });
          setErrors(apiErrors);
        }
        
        Alert.alert(
          'Error',
          result.message || `Failed to ${isEditMode ? 'update' : 'create'} product`
        );
      }
    } catch (error) {
      console.error('CreateProductScreen - Submit error:', error);
      Alert.alert('Error', 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [formData, validateForm, isEditMode, existingProduct, navigation]);

  // Get form title
  const getTitle = () => {
    return isEditMode ? 'Edit Product' : 'Add New Product';
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.goBack()}
        >
          <MaterialIcons name="arrow-back" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{getTitle()}</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.formContainer}>
          {/* Product Name */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Product Name *</Text>
            <TextInput
              style={[
                styles.input,
                errors.name ? styles.inputError : null
              ]}
              value={formData.name}
              onChangeText={(text) => handleInputChange('name', text)}
              placeholder="Enter product name"
              placeholderTextColor={colors.text.secondary}
              autoCapitalize="words"
              returnKeyType="next"
              blurOnSubmit={false}
              keyboardType="default"
              autoCorrect={false}
            />
            {errors.name && (
              <Text style={styles.errorText}>{errors.name}</Text>
            )}
          </View>

          {/* Description */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Description</Text>
            <TextInput
              style={[
                styles.input,
                styles.textArea,
                errors.description ? styles.inputError : null
              ]}
              value={formData.description}
              onChangeText={(text) => handleInputChange('description', text)}
              placeholder="Product description (optional)"
              placeholderTextColor={colors.text.secondary}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
              returnKeyType="next"
              blurOnSubmit={false}
            />
            {errors.description && (
              <Text style={styles.errorText}>{errors.description}</Text>
            )}
          </View>

          {/* Price and Stock in Row */}
          <View style={styles.rowContainer}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Price</Text>
              <TextInput
                style={[
                  styles.input,
                  errors.price ? styles.inputError : null
                ]}
                value={formData.price}
                onChangeText={(text) => handleInputChange('price', text)}
                placeholder="0.00"
                placeholderTextColor={colors.text.secondary}
                keyboardType="numeric"
                returnKeyType="next"
                blurOnSubmit={false}
              />
              {errors.price && (
                <Text style={styles.errorText}>{errors.price}</Text>
              )}
            </View>

            <View style={styles.halfInput}>
              <Text style={styles.label}>Stock Quantity</Text>
              <TextInput
                style={[
                  styles.input,
                  errors.stock_quantity ? styles.inputError : null
                ]}
                value={formData.stock_quantity}
                onChangeText={(text) => handleInputChange('stock_quantity', text)}
                placeholder="0"
                placeholderTextColor={colors.text.secondary}
                keyboardType="numeric"
                returnKeyType="next"
                blurOnSubmit={false}
              />
              {errors.stock_quantity && (
                <Text style={styles.errorText}>{errors.stock_quantity}</Text>
              )}
            </View>
          </View>

          {/* SKU */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>SKU (Stock Keeping Unit)</Text>
            <TextInput
              style={[
                styles.input,
                errors.sku ? styles.inputError : null
              ]}
              value={formData.sku}
              onChangeText={(text) => handleInputChange('sku', text)}
              placeholder="Product SKU (optional)"
              placeholderTextColor={colors.text.secondary}
              autoCapitalize="characters"
              returnKeyType="done"
              blurOnSubmit={true}
            />
            {errors.sku && (
              <Text style={styles.errorText}>{errors.sku}</Text>
            )}
          </View>

          {/* Active Status Toggle */}
          <View style={styles.inputContainer}>
            <View style={styles.toggleContainer}>
              <Text style={styles.label}>Product Status</Text>
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
      </ScrollView>

      {/* Submit Button */}
      <View style={styles.submitContainer}>
        <TouchableOpacity
          style={[
            styles.submitButton,
            loading ? styles.submitButtonDisabled : null
          ]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator size="small" color={colors.white} />
          ) : (
            <Text style={styles.submitButtonText}>
              {isEditMode ? 'Update Product' : 'Create Product'}
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
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    paddingTop: Platform.OS === 'ios' ? 60 : 16,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text.primary,
    flex: 1,
    textAlign: 'center',
    marginHorizontal: 16,
  },
  placeholder: {
    width: 32,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 100, // Space for submit button
  },
  formContainer: {
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
    backgroundColor: colors.surface,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: colors.text.primary,
    borderWidth: 1,
    borderColor: colors.border,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
    paddingTop: 14,
  },
  inputError: {
    borderColor: colors.danger,
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
  },
  halfInput: {
    flex: 1,
    marginHorizontal: 10,
  },
  toggleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    minWidth: 80,
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
});

export default CreateProductScreen;