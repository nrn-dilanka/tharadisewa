import * as yup from 'yup';

// Validation schemas for authentication forms

export const loginValidationSchema = yup.object().shape({
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters'),
  
  password: yup
    .string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

export const registrationValidationSchema = yup.object().shape({
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters')
    .max(150, 'Username must be less than 150 characters')
    .matches(
      /^[a-zA-Z0-9._-]+$/,
      'Username can only contain letters, numbers, dots, underscores and hyphens'
    ),
  
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address'),
  
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
  
  password: yup
    .string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters')
    .test(
      'password-strength',
      'Password should contain letters and numbers for better security',
      function(value) {
        if (!value) return false;
        // More lenient password requirements for initial setup
        const hasLetter = /[a-zA-Z]/.test(value);
        const hasNumber = /[0-9]/.test(value);
        return hasLetter && hasNumber;
      }
    ),
  
  password_confirm: yup
    .string()
    .required('Please confirm your password')
    .oneOf([yup.ref('password'), null], 'Passwords must match'),
  
  phone_number: yup
    .string()
    .test(
      'phone-format',
      'Please enter a valid phone number (optional)',
      function(value) {
        if (!value) return true; // Allow empty
        // More flexible phone validation
        return /^(\+94|0)?[0-9]{9}$/.test(value) || /^\+?[0-9]{10,15}$/.test(value);
      }
    )
    .nullable(),
  
  role: yup
    .string()
    .default('admin'),
});

export const changePasswordValidationSchema = yup.object().shape({
  old_password: yup
    .string()
    .required('Current password is required'),
  
  new_password: yup
    .string()
    .required('New password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  
  new_password_confirm: yup
    .string()
    .required('Please confirm your new password')
    .oneOf([yup.ref('new_password'), null], 'Passwords must match'),
});

export const profileUpdateValidationSchema = yup.object().shape({
  first_name: yup
    .string()
    .required('First name is required')
    .min(2, 'First name must be at least 2 characters')
    .max(30, 'First name must be less than 30 characters'),
  
  last_name: yup
    .string()
    .required('Last name is required')
    .min(2, 'Last name must be at least 2 characters')
    .max(30, 'Last name must be less than 30 characters'),
  
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address'),
  
  phone_number: yup
    .string()
    .matches(
      /^(\+94|0)?[0-9]{9}$/,
      'Please enter a valid Sri Lankan phone number'
    )
    .nullable(),
  
  address: yup
    .string()
    .max(500, 'Address must be less than 500 characters')
    .nullable(),
  
  date_of_birth: yup
    .date()
    .max(new Date(), 'Date of birth cannot be in the future')
    .nullable(),
});

// Helper function to get formatted error message from yup validation
export const getFormErrorMessage = (errors, fieldName) => {
  return errors[fieldName]?.message;
};

// Helper function to check if field has error
export const hasFieldError = (errors, fieldName) => {
  return !!errors[fieldName];
};