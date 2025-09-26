# Customer Management API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Authentication Endpoints

#### 1. Customer Registration
- **URL:** `POST /api/auth/register/`
- **Permission:** Public
- **Description:** Register a new customer

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "nic": "123456789V"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Customer registered successfully",
    "data": {
        "user": {
            "id": 1,
            "customer_id": "CUST000001",
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "nic": "123456789V",
            "is_verified": false,
            "date_joined": "2025-09-25T10:30:00Z",
            "last_login": null
        },
        "tokens": {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    }
}
```

#### 2. Customer Login
- **URL:** `POST /api/auth/login/`
- **Permission:** Public
- **Description:** Authenticate customer and get JWT tokens

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "customer_id": "CUST000001",
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "nic": "123456789V",
            "is_verified": false,
            "date_joined": "2025-09-25T10:30:00Z",
            "last_login": "2025-09-25T11:00:00Z"
        },
        "tokens": {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    }
}
```

#### 3. Customer Logout
- **URL:** `POST /api/auth/logout/`
- **Permission:** Authenticated
- **Description:** Logout customer and blacklist refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

#### 4. Refresh Token
- **URL:** `POST /api/auth/refresh/`
- **Permission:** Public
- **Description:** Get new access token using refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 5. Change Password
- **URL:** `POST /api/auth/change-password/`
- **Permission:** Authenticated
- **Description:** Change customer password

**Request Body:**
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Password changed successfully"
}
```

### Profile Endpoints

#### 6. Get Customer Profile
- **URL:** `GET /api/profile/`
- **Permission:** Authenticated
- **Description:** Get current customer's profile

**Response:**
```json
{
    "success": true,
    "message": "Profile retrieved successfully",
    "data": {
        "id": 1,
        "customer_id": "CUST000001",
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "nic": "123456789V",
        "is_verified": false,
        "date_joined": "2025-09-25T10:30:00Z",
        "last_login": "2025-09-25T11:00:00Z"
    }
}
```

#### 7. Update Customer Profile
- **URL:** `PUT /api/profile/`
- **Permission:** Authenticated
- **Description:** Update current customer's profile

**Request Body:**
```json
{
    "first_name": "John Updated",
    "last_name": "Doe Updated",
    "email": "john.updated@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "id": 1,
        "customer_id": "CUST000001",
        "username": "johndoe",
        "email": "john.updated@example.com",
        "first_name": "John Updated",
        "last_name": "Doe Updated",
        "full_name": "John Updated Doe Updated",
        "nic": "123456789V",
        "is_verified": false,
        "date_joined": "2025-09-25T10:30:00Z",
        "last_login": "2025-09-25T11:00:00Z"
    }
}
```

#### 8. Deactivate Account
- **URL:** `DELETE /api/profile/`
- **Permission:** Authenticated
- **Description:** Deactivate current customer's account

**Response:**
```json
{
    "success": true,
    "message": "Account deactivated successfully"
}
```

### Customer Management Endpoints (Admin)

#### 9. List All Customers
- **URL:** `GET /api/customers/`
- **Permission:** Authenticated
- **Description:** Get list of all customers with pagination and filtering

**Query Parameters:**
- `search`: Search in username, first_name, last_name, email, or nic
- `is_verified`: Filter by verification status (true/false)
- `page`: Page number for pagination

**Response:**
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/customers/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "customer_id": "CUST000001",
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "nic": "123456789V",
            "is_verified": false,
            "date_joined": "2025-09-25T10:30:00Z",
            "last_login": "2025-09-25T11:00:00Z"
        }
    ]
}
```

#### 10. Get Specific Customer
- **URL:** `GET /api/customers/{id}/`
- **Permission:** Authenticated
- **Description:** Get details of a specific customer

#### 11. Update Specific Customer
- **URL:** `PUT /api/customers/{id}/`
- **Permission:** Authenticated
- **Description:** Update a specific customer

#### 12. Delete Specific Customer
- **URL:** `DELETE /api/customers/{id}/`
- **Permission:** Authenticated
- **Description:** Delete a specific customer

#### 13. Verify/Unverify Customer
- **URL:** `POST /api/customers/{id}/verify/`
- **Permission:** Authenticated
- **Description:** Toggle verification status of a customer

**Response:**
```json
{
    "success": true,
    "message": "Customer verified successfully",
    "data": {
        "id": 1,
        "customer_id": "CUST000001",
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "nic": "123456789V",
        "is_verified": true,
        "date_joined": "2025-09-25T10:30:00Z",
        "last_login": "2025-09-25T11:00:00Z"
    }
}
```

#### 14. Customer Statistics
- **URL:** `GET /api/stats/`
- **Permission:** Authenticated
- **Description:** Get customer statistics

**Response:**
```json
{
    "success": true,
    "data": {
        "total_customers": 100,
        "verified_customers": 75,
        "active_customers": 95,
        "unverified_customers": 25,
        "inactive_customers": 5
    }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error message for this field"]
    }
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Data Validation

### NIC Format
- Old format: 9 digits followed by V/v/X/x (e.g., "123456789V")
- New format: 12 digits (e.g., "123456789012")

### Required Fields for Registration
- username
- email
- password
- first_name
- last_name
- nic