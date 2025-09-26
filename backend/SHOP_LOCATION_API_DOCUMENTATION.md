# Shop & Customer Location Management API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## Shop Management Endpoints

### 1. List All Shops
- **URL:** `GET /api/shops/`
- **Permission:** Authenticated
- **Description:** Get list of all shops with pagination and filtering

**Query Parameters:**
- `customer_id`: Filter by specific customer ID
- `is_active`: Filter by active status (true/false)
- `city`: Filter by city name (case-insensitive)
- `postal_code`: Filter by exact postal code
- `search`: Search in shop name, address, or customer details
- `page`: Page number for pagination

**Response:**
```json
{
    "success": true,
    "message": "Shops retrieved successfully",
    "data": {
        "count": 50,
        "next": "http://localhost:8000/api/shops/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "name": "Tech Store",
                "postal_code": "10001",
                "address_line_1": "123 Main Street",
                "address_line_2": "Suite 101",
                "address_line_3": null,
                "city": "Colombo",
                "customer": 1,
                "customer_name": "John Doe",
                "customer_username": "johndoe",
                "is_active": true,
                "phone_number": "+94112345678",
                "email": "techstore@example.com",
                "description": "Electronics and gadgets store",
                "full_address": "123 Main Street, Suite 101, Colombo, 10001",
                "address_dict": {
                    "line_1": "123 Main Street",
                    "line_2": "Suite 101",
                    "line_3": null,
                    "city": "Colombo",
                    "postal_code": "10001",
                    "full_address": "123 Main Street, Suite 101, Colombo, 10001"
                },
                "location_count": 2,
                "created_at": "2025-09-25T10:30:00Z",
                "updated_at": "2025-09-25T10:30:00Z"
            }
        ]
    }
}
```

### 2. Create New Shop
- **URL:** `POST /api/shops/`
- **Permission:** Authenticated
- **Description:** Create a new shop

**Request Body:**
```json
{
    "name": "New Tech Store",
    "postal_code": "10002",
    "address_line_1": "456 Second Street",
    "address_line_2": "Floor 2",
    "address_line_3": null,
    "city": "Kandy",
    "customer": 1,
    "phone_number": "+94112345679",
    "email": "newstore@example.com",
    "description": "Latest electronics store",
    "is_active": true
}
```

### 3. Get Specific Shop
- **URL:** `GET /api/shops/{id}/`
- **Permission:** Authenticated
- **Description:** Get details of a specific shop

### 4. Update Shop
- **URL:** `PUT /api/shops/{id}/`
- **Permission:** Authenticated
- **Description:** Update a specific shop (cannot change customer)

### 5. Delete Shop
- **URL:** `DELETE /api/shops/{id}/`
- **Permission:** Authenticated
- **Description:** Delete a specific shop

### 6. Get Customer's Shops
- **URL:** `GET /api/customers/{customer_id}/shops/`
- **Permission:** Authenticated
- **Description:** Get all shops for a specific customer

### 7. List Customers with Shops
- **URL:** `GET /api/customers-with-shops/`
- **Permission:** Authenticated
- **Description:** Get list of all customers with their shops

### 8. List Shops with Locations
- **URL:** `GET /api/shops-with-locations/`
- **Permission:** Authenticated
- **Description:** Get list of all shops with their geographic locations

### 9. Toggle Shop Status
- **URL:** `POST /api/shops/{shop_id}/toggle-status/`
- **Permission:** Authenticated
- **Description:** Toggle active/inactive status of a shop

### 10. Get Shops by City
- **URL:** `GET /api/shops/city/{city_name}/`
- **Permission:** Authenticated
- **Description:** Get all active shops in a specific city

### 11. Get Shops by Postal Code
- **URL:** `GET /api/shops/postal-code/{postal_code}/`
- **Permission:** Authenticated
- **Description:** Get all active shops in a specific postal code area

### 12. Bulk Create Shops
- **URL:** `POST /api/shops/bulk-create/`
- **Permission:** Authenticated
- **Description:** Create multiple shops at once

**Request Body:**
```json
{
    "shops": [
        {
            "name": "Shop 1",
            "postal_code": "10001",
            "address_line_1": "Address 1",
            "city": "City 1",
            "customer": 1
        },
        {
            "name": "Shop 2",
            "postal_code": "10002",
            "address_line_1": "Address 2",
            "city": "City 2",
            "customer": 2
        }
    ]
}
```

### 13. Shop Statistics
- **URL:** `GET /api/shops/stats/`
- **Permission:** Authenticated
- **Description:** Get comprehensive shop statistics

**Response:**
```json
{
    "success": true,
    "data": {
        "total_shops": 150,
        "active_shops": 140,
        "inactive_shops": 10,
        "customers_with_shops": 85,
        "customers_without_shops": 15,
        "shops_by_city": [
            {
                "city": "Colombo",
                "count": 45
            },
            {
                "city": "Kandy",
                "count": 32
            }
        ]
    }
}
```

---

## Customer Location Management Endpoints

### 14. List All Locations
- **URL:** `GET /api/locations/`
- **Permission:** Authenticated
- **Description:** Get list of all customer locations with pagination and filtering

**Query Parameters:**
- `shop_id`: Filter by specific shop ID
- `customer_id`: Filter by specific customer ID (through shop)
- `is_active`: Filter by active status (true/false)
- `is_primary`: Filter by primary status (true/false)
- `search`: Search in location details, shop name, or customer details
- `page`: Page number for pagination

**Response:**
```json
{
    "success": true,
    "message": "Locations retrieved successfully",
    "data": [
        {
            "id": 1,
            "longitude": "79.85133000",
            "latitude": "6.92707000",
            "shop": 1,
            "shop_name": "Tech Store",
            "customer_name": "John Doe",
            "location_name": "Main Branch Location",
            "address_description": "Near the main bus station",
            "is_primary": true,
            "is_active": true,
            "accuracy_radius": 10,
            "coordinates": [6.92707, 79.85133],
            "google_maps_url": "https://www.google.com/maps?q=6.92707000,79.85133000",
            "location_info": {
                "coordinates": [6.92707, 79.85133],
                "longitude": 79.85133,
                "latitude": 6.92707,
                "location_name": "Main Branch Location",
                "address_description": "Near the main bus station",
                "is_primary": true,
                "accuracy_radius": 10,
                "google_maps_url": "https://www.google.com/maps?q=6.92707000,79.85133000"
            },
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

### 15. Create New Location
- **URL:** `POST /api/locations/`
- **Permission:** Authenticated
- **Description:** Create a new customer location

**Request Body:**
```json
{
    "longitude": "79.85133000",
    "latitude": "6.92707000",
    "shop": 1,
    "location_name": "Branch Location",
    "address_description": "Near the market area",
    "is_primary": false,
    "is_active": true,
    "accuracy_radius": 15
}
```

### 16. Get Specific Location
- **URL:** `GET /api/locations/{id}/`
- **Permission:** Authenticated
- **Description:** Get details of a specific location

### 17. Update Location
- **URL:** `PUT /api/locations/{id}/`
- **Permission:** Authenticated
- **Description:** Update a specific location (cannot change shop)

### 18. Delete Location
- **URL:** `DELETE /api/locations/{id}/`
- **Permission:** Authenticated
- **Description:** Delete a specific location

### 19. Get Shop's Locations
- **URL:** `GET /api/shops/{shop_id}/locations/`
- **Permission:** Authenticated
- **Description:** Get all locations for a specific shop

**Response:**
```json
{
    "success": true,
    "message": "Shop locations retrieved successfully",
    "data": {
        "shop": {
            "id": 1,
            "name": "Tech Store",
            "customer_name": "John Doe",
            "full_address": "123 Main Street, Suite 101, Colombo, 10001"
        },
        "locations": [
            {
                "id": 1,
                "longitude": "79.85133000",
                "latitude": "6.92707000",
                "shop": 1,
                "shop_name": "Tech Store",
                "customer_name": "John Doe",
                "location_name": "Main Branch",
                "address_description": "Near the main bus station",
                "is_primary": true,
                "is_active": true,
                "accuracy_radius": 10,
                "coordinates": [6.92707, 79.85133],
                "google_maps_url": "https://www.google.com/maps?q=6.92707000,79.85133000",
                "location_info": {
                    "coordinates": [6.92707, 79.85133],
                    "longitude": 79.85133,
                    "latitude": 6.92707,
                    "location_name": "Main Branch",
                    "address_description": "Near the main bus station",
                    "is_primary": true,
                    "accuracy_radius": 10,
                    "google_maps_url": "https://www.google.com/maps?q=6.92707000,79.85133000"
                },
                "created_at": "2025-09-25T10:30:00Z",
                "updated_at": "2025-09-25T10:30:00Z"
            }
        ],
        "location_count": 1
    }
}
```

### 20. Set Primary Location
- **URL:** `POST /api/locations/{location_id}/set-primary/`
- **Permission:** Authenticated
- **Description:** Set a location as primary for the shop (automatically unsets others)

### 21. Toggle Location Status
- **URL:** `POST /api/locations/{location_id}/toggle-status/`
- **Permission:** Authenticated
- **Description:** Toggle active/inactive status of a location

### 22. Find Nearby Locations
- **URL:** `GET /api/locations/nearby/`
- **Permission:** Authenticated
- **Description:** Find locations within a certain radius

**Query Parameters:**
- `latitude`: Center latitude for search (required)
- `longitude`: Center longitude for search (required)
- `radius_km`: Search radius in kilometers (default: 5)

**Response:**
```json
{
    "success": true,
    "message": "Found 3 locations within 5km",
    "data": {
        "search_coordinates": {
            "latitude": 6.9271,
            "longitude": 79.8612,
            "radius_km": 5
        },
        "locations": [
            {
                "id": 1,
                "longitude": "79.85133000",
                "latitude": "6.92707000",
                "shop": 1,
                "shop_name": "Tech Store",
                "customer_name": "John Doe",
                "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
                "location_name": "Main Branch",
                "address_description": "Near the main bus station",
                "coordinates": [6.92707, 79.85133],
                "google_maps_url": "https://www.google.com/maps?q=6.92707000,79.85133000",
                "distance_info": {
                    "approximate_distance_km": 1.05,
                    "note": "Approximate distance calculation"
                }
            }
        ],
        "location_count": 3
    }
}
```

### 23. Get Locations Within Bounds
- **URL:** `GET /api/locations/within-bounds/`
- **Permission:** Authenticated
- **Description:** Get locations within a geographic bounding box

**Query Parameters:**
- `min_latitude`: Minimum latitude (required)
- `max_latitude`: Maximum latitude (required)
- `min_longitude`: Minimum longitude (required)
- `max_longitude`: Maximum longitude (required)

### 24. Bulk Create Locations
- **URL:** `POST /api/locations/bulk-create/`
- **Permission:** Authenticated
- **Description:** Create multiple locations at once

### 25. Location Statistics
- **URL:** `GET /api/locations/stats/`
- **Permission:** Authenticated
- **Description:** Get comprehensive location statistics

**Response:**
```json
{
    "success": true,
    "data": {
        "total_locations": 200,
        "active_locations": 180,
        "inactive_locations": 20,
        "primary_locations": 85,
        "shops_with_locations": 85,
        "shops_without_locations": 15
    }
}
```

---

## Data Models

### Shop Model Fields
- **Required Fields:**
  - `name`: Shop name (max 255 chars)
  - `postal_code`: 5-digit postal code
  - `address_line_1`: Primary address line
  - `city`: City name
  - `customer`: Foreign key to Customer

- **Optional Fields:**
  - `address_line_2`: Secondary address line
  - `address_line_3`: Tertiary address line
  - `phone_number`: Shop phone number
  - `email`: Shop email address
  - `description`: Shop description
  - `is_active`: Active status (default: true)

### CustomerLocation Model Fields
- **Required Fields:**
  - `longitude`: Longitude (-180.0 to 180.0)
  - `latitude`: Latitude (-90.0 to 90.0)
  - `shop`: Foreign key to Shop

- **Optional Fields:**
  - `location_name`: Name for the location
  - `address_description`: Description of the location
  - `is_primary`: Primary location for shop (default: false)
  - `is_active`: Active status (default: true)
  - `accuracy_radius`: GPS accuracy in meters

---

## Data Validation

### Shop Validation
- Postal code must be exactly 5 digits
- Shop name must be unique per customer
- Customer must be active

### Location Validation
- Longitude: -180.0 to 180.0
- Latitude: -90.0 to 90.0
- Coordinates must be unique per shop
- Shop must be active
- Only one primary location per shop

---

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

---

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