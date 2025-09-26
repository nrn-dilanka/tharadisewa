# Customer Contact Management API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Customer Contact Endpoints

### 1. List All Contacts
- **URL:** `GET /api/contacts/`
- **Permission:** Authenticated
- **Description:** Get list of all customer contacts with pagination and filtering

**Query Parameters:**
- `customer_id`: Filter by specific customer ID
- `is_active`: Filter by active status (true/false)
- `is_primary`: Filter by primary status (true/false)
- `search`: Search in email, phone numbers, or customer details
- `page`: Page number for pagination

**Response:**
```json
{
    "success": true,
    "message": "Contacts retrieved successfully",
    "data": {
        "count": 50,
        "next": "http://localhost:8000/api/contacts/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "customer": 1,
                "customer_name": "John Doe",
                "customer_username": "johndoe",
                "email": "john.contact@example.com",
                "wa_number": "+94771234567",
                "tp_number": "+94112345678",
                "is_primary": true,
                "is_active": true,
                "contact_info": {
                    "email": "john.contact@example.com",
                    "whatsapp": "+94771234567",
                    "telephone": "+94112345678",
                    "is_primary": true
                },
                "created_at": "2025-09-25T10:30:00Z",
                "updated_at": "2025-09-25T10:30:00Z"
            }
        ]
    }
}
```

### 2. Create New Contact
- **URL:** `POST /api/contacts/`
- **Permission:** Authenticated
- **Description:** Create a new customer contact

**Request Body:**
```json
{
    "customer": 1,
    "email": "contact@example.com",
    "wa_number": "+94771234567",
    "tp_number": "+94112345678",
    "is_primary": true,
    "is_active": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Customer contact created successfully",
    "data": {
        "id": 2,
        "customer": 1,
        "customer_name": "John Doe",
        "customer_username": "johndoe",
        "email": "contact@example.com",
        "wa_number": "+94771234567",
        "tp_number": "+94112345678",
        "is_primary": true,
        "is_active": true,
        "contact_info": {
            "email": "contact@example.com",
            "whatsapp": "+94771234567",
            "telephone": "+94112345678",
            "is_primary": true
        },
        "created_at": "2025-09-25T11:00:00Z",
        "updated_at": "2025-09-25T11:00:00Z"
    }
}
```

### 3. Get Specific Contact
- **URL:** `GET /api/contacts/{id}/`
- **Permission:** Authenticated
- **Description:** Get details of a specific contact

**Response:**
```json
{
    "success": true,
    "message": "Contact retrieved successfully",
    "data": {
        "id": 1,
        "customer": 1,
        "customer_name": "John Doe",
        "customer_username": "johndoe",
        "email": "john.contact@example.com",
        "wa_number": "+94771234567",
        "tp_number": "+94112345678",
        "is_primary": true,
        "is_active": true,
        "contact_info": {
            "email": "john.contact@example.com",
            "whatsapp": "+94771234567",
            "telephone": "+94112345678",
            "is_primary": true
        },
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z"
    }
}
```

### 4. Update Contact
- **URL:** `PUT /api/contacts/{id}/`
- **Permission:** Authenticated
- **Description:** Update a specific contact (cannot change customer)

**Request Body:**
```json
{
    "email": "updated.contact@example.com",
    "wa_number": "+94771234568",
    "tp_number": "+94112345679",
    "is_primary": false,
    "is_active": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Contact updated successfully",
    "data": {
        "id": 1,
        "customer": 1,
        "customer_name": "John Doe",
        "customer_username": "johndoe",
        "email": "updated.contact@example.com",
        "wa_number": "+94771234568",
        "tp_number": "+94112345679",
        "is_primary": false,
        "is_active": true,
        "contact_info": {
            "email": "updated.contact@example.com",
            "whatsapp": "+94771234568",
            "telephone": "+94112345679",
            "is_primary": false
        },
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T11:30:00Z"
    }
}
```

### 5. Delete Contact
- **URL:** `DELETE /api/contacts/{id}/`
- **Permission:** Authenticated
- **Description:** Delete a specific contact

**Response:**
```json
{
    "success": true,
    "message": "Contact deleted successfully"
}
```

### 6. Get Customer's Contacts
- **URL:** `GET /api/customers/{customer_id}/contacts/`
- **Permission:** Authenticated
- **Description:** Get all contacts for a specific customer

**Response:**
```json
{
    "success": true,
    "message": "Customer contacts retrieved successfully",
    "data": {
        "customer": {
            "id": 1,
            "customer_id": "CUST000001",
            "full_name": "John Doe",
            "username": "johndoe"
        },
        "contacts": [
            {
                "id": 1,
                "customer": 1,
                "customer_name": "John Doe",
                "customer_username": "johndoe",
                "email": "primary@example.com",
                "wa_number": "+94771234567",
                "tp_number": "+94112345678",
                "is_primary": true,
                "is_active": true,
                "contact_info": {
                    "email": "primary@example.com",
                    "whatsapp": "+94771234567",
                    "telephone": "+94112345678",
                    "is_primary": true
                },
                "created_at": "2025-09-25T10:30:00Z",
                "updated_at": "2025-09-25T10:30:00Z"
            }
        ]
    }
}
```

### 7. List Customers with Contacts
- **URL:** `GET /api/customers-with-contacts/`
- **Permission:** Authenticated
- **Description:** Get list of all customers with their contacts

**Response:**
```json
{
    "success": true,
    "message": "Customers with contacts retrieved successfully",
    "data": [
        {
            "id": 1,
            "customer_id": "CUST000001",
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "nic": "123456789V",
            "is_verified": true,
            "contacts": [
                {
                    "id": 1,
                    "customer": 1,
                    "customer_name": "John Doe",
                    "customer_username": "johndoe",
                    "email": "primary@example.com",
                    "wa_number": "+94771234567",
                    "tp_number": "+94112345678",
                    "is_primary": true,
                    "is_active": true,
                    "contact_info": {
                        "email": "primary@example.com",
                        "whatsapp": "+94771234567",
                        "telephone": "+94112345678",
                        "is_primary": true
                    },
                    "created_at": "2025-09-25T10:30:00Z",
                    "updated_at": "2025-09-25T10:30:00Z"
                }
            ],
            "primary_contact": {
                "id": 1,
                "customer": 1,
                "customer_name": "John Doe",
                "customer_username": "johndoe",
                "email": "primary@example.com",
                "wa_number": "+94771234567",
                "tp_number": "+94112345678",
                "is_primary": true,
                "is_active": true,
                "contact_info": {
                    "email": "primary@example.com",
                    "whatsapp": "+94771234567",
                    "telephone": "+94112345678",
                    "is_primary": true
                },
                "created_at": "2025-09-25T10:30:00Z",
                "updated_at": "2025-09-25T10:30:00Z"
            }
        }
    ]
}
```

### 8. Set Primary Contact
- **URL:** `POST /api/contacts/{contact_id}/set-primary/`
- **Permission:** Authenticated
- **Description:** Set a contact as primary (automatically unsets other primary contacts for the same customer)

**Response:**
```json
{
    "success": true,
    "message": "Contact set as primary successfully",
    "data": {
        "id": 1,
        "customer": 1,
        "customer_name": "John Doe",
        "customer_username": "johndoe",
        "email": "primary@example.com",
        "wa_number": "+94771234567",
        "tp_number": "+94112345678",
        "is_primary": true,
        "is_active": true,
        "contact_info": {
            "email": "primary@example.com",
            "whatsapp": "+94771234567",
            "telephone": "+94112345678",
            "is_primary": true
        },
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T11:45:00Z"
    }
}
```

### 9. Toggle Contact Status
- **URL:** `POST /api/contacts/{contact_id}/toggle-status/`
- **Permission:** Authenticated
- **Description:** Toggle active/inactive status of a contact

**Response:**
```json
{
    "success": true,
    "message": "Contact activated successfully",
    "data": {
        "id": 1,
        "customer": 1,
        "customer_name": "John Doe",
        "customer_username": "johndoe",
        "email": "contact@example.com",
        "wa_number": "+94771234567",
        "tp_number": "+94112345678",
        "is_primary": false,
        "is_active": true,
        "contact_info": {
            "email": "contact@example.com",
            "whatsapp": "+94771234567",
            "telephone": "+94112345678",
            "is_primary": false
        },
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T12:00:00Z"
    }
}
```

### 10. Bulk Create Contacts
- **URL:** `POST /api/contacts/bulk-create/`
- **Permission:** Authenticated
- **Description:** Create multiple contacts at once

**Request Body:**
```json
{
    "contacts": [
        {
            "customer": 1,
            "email": "contact1@example.com",
            "wa_number": "+94771234567",
            "tp_number": "+94112345678",
            "is_primary": true,
            "is_active": true
        },
        {
            "customer": 2,
            "email": "contact2@example.com",
            "wa_number": "+94771234568",
            "tp_number": "+94112345679",
            "is_primary": false,
            "is_active": true
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Created 2 contacts successfully",
    "data": {
        "created_contacts": [
            {
                "id": 3,
                "customer": 1,
                "customer_name": "John Doe",
                "customer_username": "johndoe",
                "email": "contact1@example.com",
                "wa_number": "+94771234567",
                "tp_number": "+94112345678",
                "is_primary": true,
                "is_active": true,
                "contact_info": {
                    "email": "contact1@example.com",
                    "whatsapp": "+94771234567",
                    "telephone": "+94112345678",
                    "is_primary": true
                },
                "created_at": "2025-09-25T12:15:00Z",
                "updated_at": "2025-09-25T12:15:00Z"
            }
        ],
        "errors": []
    }
}
```

### 11. Contact Statistics
- **URL:** `GET /api/contacts/stats/`
- **Permission:** Authenticated
- **Description:** Get contact statistics

**Response:**
```json
{
    "success": true,
    "data": {
        "total_contacts": 150,
        "active_contacts": 140,
        "inactive_contacts": 10,
        "primary_contacts": 85,
        "customers_with_contacts": 85,
        "customers_without_contacts": 15
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
- `204 No Content` - Resource deleted successfully
- `207 Multi-Status` - Bulk operation with some errors
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Data Validation

### Phone Number Format
- WhatsApp Number: Must be in format '+94771234567' or '0771234567'
- Telephone Number: Must be in format '+94112345678' or '0112345678'
- Both support international formats

### Unique Constraints
- Each customer can have only one contact with the same email
- Each customer can have only one contact with the same WhatsApp number
- Each customer can have only one contact with the same telephone number
- Only one contact per customer can be set as primary

### Required Fields
- customer (ID reference)
- email
- wa_number (WhatsApp number)
- tp_number (Telephone number)

### Optional Fields
- is_primary (default: false)
- is_active (default: true)