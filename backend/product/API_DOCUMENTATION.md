# Product Management API Documentation

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

## Product Management Endpoints

### 1. List All Products
- **URL:** `GET /api/products/`
- **Permission:** Authenticated
- **Description:** Get list of all products with pagination and filtering

**Query Parameters:**
- `shop_id`: Filter by specific shop ID
- `customer_id`: Filter by specific customer ID
- `is_active`: Filter by active status (true/false)
- `in_stock`: Filter by stock availability (true/false)
- `min_price`: Filter by minimum price
- `max_price`: Filter by maximum price
- `search`: Search in product name, description, SKU, shop name, or customer details
- `page`: Page number for pagination
- `ordering`: Order by fields (name, price, stock_quantity, created_at)

**Response:**
```json
{
    "success": true,
    "message": "Products retrieved successfully",
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Smartphone XYZ",
            "shop": 1,
            "shop_name": "Tech Store",
            "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
            "customer_name": "John Doe",
            "customer_id": 1,
            "price": "299.99",
            "sku": "PHONE-XYZ-001",
            "is_active": true,
            "stock_quantity": 50,
            "product_code": "PRD-550E8400",
            "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
            "created_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

### 2. Create New Product
- **URL:** `POST /api/products/`
- **Permission:** Authenticated
- **Description:** Create a new product (QR code generated automatically)

**Request Body:**
```json
{
    "shop": 1,
    "name": "New Smartphone",
    "description": "Latest smartphone with advanced features",
    "price": "599.99",
    "sku": "PHONE-NEW-001",
    "stock_quantity": 25,
    "is_active": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Product created successfully",
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "shop": 1,
        "shop_name": "Tech Store",
        "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
        "customer_name": "John Doe",
        "customer_id": 1,
        "name": "New Smartphone",
        "description": "Latest smartphone with advanced features",
        "price": "599.99",
        "sku": "PHONE-NEW-001",
        "is_active": true,
        "stock_quantity": 25,
        "qr_code": "/media/product_qr_codes/product_660e8400-e29b-41d4-a716-446655440001_qr.png",
        "qr_code_url": "/media/product_qr_codes/product_660e8400-e29b-41d4-a716-446655440001_qr.png",
        "product_code": "PRD-660E8400",
        "shop_info": {
            "shop_id": 1,
            "shop_name": "Tech Store",
            "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
            "customer_name": "John Doe"
        },
        "created_at": "2025-09-25T11:00:00Z",
        "updated_at": "2025-09-25T11:00:00Z"
    }
}
```

### 3. Get Specific Product
- **URL:** `GET /api/products/{id}/`
- **Permission:** Authenticated
- **Description:** Get details of a specific product

**Response:**
```json
{
    "success": true,
    "message": "Product retrieved successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "shop": 1,
        "shop_name": "Tech Store",
        "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
        "customer_name": "John Doe",
        "customer_id": 1,
        "name": "Smartphone XYZ",
        "description": "High-quality smartphone with excellent camera",
        "price": "299.99",
        "sku": "PHONE-XYZ-001",
        "is_active": true,
        "stock_quantity": 50,
        "qr_code": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "product_code": "PRD-550E8400",
        "shop_info": {
            "shop_id": 1,
            "shop_name": "Tech Store",
            "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
            "customer_name": "John Doe"
        },
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:35:00Z"
    }
}
```

### 4. Update Product
- **URL:** `PUT /api/products/{id}/`
- **Permission:** Authenticated  
- **Description:** Update a product (cannot change shop)

**Request Body:**
```json
{
    "name": "Updated Smartphone XYZ",
    "description": "Updated description with new features",
    "price": "349.99",
    "sku": "PHONE-XYZ-002",
    "stock_quantity": 75,
    "is_active": true
}
```

### 5. Partial Update Product
- **URL:** `PATCH /api/products/{id}/`
- **Permission:** Authenticated
- **Description:** Partially update specific fields of a product

### 6. Delete Product
- **URL:** `DELETE /api/products/{id}/`
- **Permission:** Authenticated
- **Description:** Delete a product (also removes QR code file)

**Response:**
```json
{
    "success": true,
    "message": "Product deleted successfully"
}
```

### 7. Regenerate QR Code
- **URL:** `POST /api/products/{id}/regenerate_qr_code/`
- **Permission:** Authenticated
- **Description:** Regenerate QR code for a specific product

**Response:**
```json
{
    "success": true,
    "message": "QR code regenerated successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Smartphone XYZ",
        "qr_code": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "product_code": "PRD-550E8400"
    }
}
```

### 8. Get QR Code Information
- **URL:** `GET /api/products/{id}/qr_code_info/`
- **Permission:** Authenticated
- **Description:** Get QR code information for a product

**Response:**
```json
{
    "success": true,
    "message": "QR code information retrieved successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Smartphone XYZ",
        "qr_code": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "product_code": "PRD-550E8400"
    }
}
```

### 9. Toggle Product Status
- **URL:** `POST /api/products/{id}/toggle_status/`
- **Permission:** Authenticated
- **Description:** Toggle active/inactive status of a product

**Response:**
```json
{
    "success": true,
    "message": "Product activated successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Smartphone XYZ",
        "is_active": true,
        // ... other product fields
    }
}
```

### 10. Get Products by Shop
- **URL:** `GET /api/products/by_shop/`
- **Permission:** Authenticated
- **Description:** Get all products for a specific shop

**Query Parameters:**
- `shop_id`: Shop ID (required)
- `is_active`: Filter by active status (optional)

**Response:**
```json
{
    "success": true,
    "message": "Products for shop \"Tech Store\" retrieved successfully",
    "data": {
        "shop": {
            "id": 1,
            "name": "Tech Store",
            "customer_name": "John Doe",
            "full_address": "123 Main Street, Suite 101, Colombo, 10001"
        },
        "products": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Smartphone XYZ",
                "shop": 1,
                "shop_name": "Tech Store",
                "customer_name": "John Doe",
                "price": "299.99",
                "sku": "PHONE-XYZ-001",
                "is_active": true,
                "stock_quantity": 50,
                "product_code": "PRD-550E8400",
                "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
                "created_at": "2025-09-25T10:30:00Z"
            }
        ],
        "product_count": 1
    }
}
```

### 11. Get Products by Customer
- **URL:** `GET /api/products/by_customer/`
- **Permission:** Authenticated
- **Description:** Get all products for a specific customer (across all their shops)

**Query Parameters:**
- `customer_id`: Customer ID (required)
- `is_active`: Filter by active status (optional)

**Response:**
```json
{
    "success": true,
    "message": "Products for customer retrieved successfully",
    "data": {
        "shops": [
            {
                "shop_id": 1,
                "shop_name": "Tech Store",
                "products": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Smartphone XYZ",
                        "shop": 1,
                        "shop_name": "Tech Store",
                        "customer_name": "John Doe",
                        "price": "299.99",
                        "sku": "PHONE-XYZ-001",
                        "is_active": true,
                        "stock_quantity": 50,
                        "product_code": "PRD-550E8400",
                        "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
                        "created_at": "2025-09-25T10:30:00Z"
                    }
                ]
            }
        ],
        "total_products": 1
    }
}
```

### 12. Bulk Create Products
- **URL:** `POST /api/products/bulk_create/`
- **Permission:** Authenticated
- **Description:** Create multiple products at once (max 100)

**Request Body:**
```json
{
    "products": [
        {
            "shop": 1,
            "name": "Product 1",
            "price": "99.99",
            "stock_quantity": 10
        },
        {
            "shop": 1,
            "name": "Product 2",
            "price": "149.99",
            "stock_quantity": 5
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "message": "2 products created successfully",
    "data": [
        {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "name": "Product 1",
            "shop": 1,
            "shop_name": "Tech Store",
            "customer_name": "John Doe",
            "price": "99.99",
            "sku": null,
            "is_active": true,
            "stock_quantity": 10,
            "product_code": "PRD-770E8400",
            "qr_code_url": "/media/product_qr_codes/product_770e8400-e29b-41d4-a716-446655440002_qr.png",
            "created_at": "2025-09-25T12:00:00Z"
        }
        // ... more products
    ]
}
```

### 13. Product Statistics
- **URL:** `GET /api/products/stats/`
- **Permission:** Authenticated
- **Description:** Get comprehensive product statistics

**Response:**
```json
{
    "success": true,
    "message": "Product statistics retrieved successfully",
    "data": {
        "total_products": 150,
        "active_products": 140,
        "inactive_products": 10,
        "products_with_price": 130,
        "products_without_price": 20,
        "products_in_stock": 120,
        "products_out_of_stock": 30,
        "shops_with_products": 45,
        "shops_without_products": 5,
        "average_price": "249.99",
        "total_stock_value": "125000.00"
    }
}
```

### 14. Search Products by QR Code
- **URL:** `GET /api/products/search_by_qr/`
- **Permission:** Authenticated
- **Description:** Search for products using QR code data

**Query Parameters:**
- `qr_data`: QR code data string (required)

**Example QR Data Format:**
```
PRODUCT_ID:550e8400-e29b-41d4-a716-446655440000|NAME:Smartphone XYZ|SHOP:Tech Store|SHOP_ID:1
```

**Response:**
```json
{
    "success": true,
    "message": "Product found by QR code",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "shop": 1,
        "shop_name": "Tech Store",
        "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
        "customer_name": "John Doe",
        "customer_id": 1,
        "name": "Smartphone XYZ",
        "description": "High-quality smartphone with excellent camera",
        "price": "299.99",
        "sku": "PHONE-XYZ-001",
        "is_active": true,
        "stock_quantity": 50,
        "qr_code": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
        "product_code": "PRD-550E8400",
        "shop_info": {
            "shop_id": 1,
            "shop_name": "Tech Store",
            "shop_address": "123 Main Street, Suite 101, Colombo, 10001",
            "customer_name": "John Doe"
        },
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:35:00Z"
    }
}
```

### 15. Get Shop Products (Alternative endpoint)
- **URL:** `GET /api/shops/{shop_id}/products/`
- **Permission:** Authenticated
- **Description:** Get all products for a specific shop with detailed shop information

**Response:**
```json
{
    "success": true,
    "message": "Shop products retrieved successfully",
    "data": {
        "id": 1,
        "name": "Tech Store",
        "full_address": "123 Main Street, Suite 101, Colombo, 10001",
        "customer": 1,
        "products": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Smartphone XYZ",
                "shop": 1,
                "shop_name": "Tech Store",
                "customer_name": "John Doe",
                "price": "299.99",
                "sku": "PHONE-XYZ-001",
                "is_active": true,
                "stock_quantity": 50,
                "product_code": "PRD-550E8400",
                "qr_code_url": "/media/product_qr_codes/product_550e8400-e29b-41d4-a716-446655440000_qr.png",
                "created_at": "2025-09-25T10:30:00Z"
            }
        ],
        "product_count": 1
    }
}
```

---

## Data Models

### Product Model Fields
- **Required Fields:**
  - `shop`: Foreign key to Shop (cannot be changed after creation)
  - `name`: Product name (max 255 chars, unique per shop)

- **Optional Fields:**
  - `description`: Product description (text field)
  - `price`: Product price (decimal, 2 decimal places)
  - `sku`: Stock Keeping Unit (max 50 chars)
  - `stock_quantity`: Available stock (integer, default: 0)
  - `is_active`: Active status (boolean, default: true)

- **Auto-generated Fields:**
  - `id`: UUID primary key
  - `qr_code`: Auto-generated QR code image
  - `created_at`: Creation timestamp
  - `updated_at`: Last update timestamp

### Product Computed Properties
- `product_code`: Human-readable code (PRD-{first8chars})
- `qr_code_url`: URL to QR code image
- `shop_info`: Dictionary with shop and customer information

---

## QR Code Format

Products automatically generate QR codes with the following data format:
```
PRODUCT_ID:{uuid}|NAME:{product_name}|SHOP:{shop_name}|SHOP_ID:{shop_id}
```

Example:
```
PRODUCT_ID:550e8400-e29b-41d4-a716-446655440000|NAME:Smartphone XYZ|SHOP:Tech Store|SHOP_ID:1
```

---

## Data Validation

### Product Validation Rules
- Product name must be at least 2 characters
- Product name must be unique per shop
- Price cannot be negative (if provided)
- Stock quantity cannot be negative
- Shop must be active to create products
- SKU is optional but must be unique if provided
- Name can only contain: letters, numbers, spaces, hyphens, underscores, periods, parentheses, ampersands

### Business Rules
- Cannot change shop after product creation
- QR code automatically regenerates when product details change significantly
- Deleting a product also removes its QR code file
- Only one product with the same name per shop

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

Common error scenarios:
- **400 Bad Request**: Invalid data, validation errors
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Product or related resource not found
- **500 Internal Server Error**: Server error (e.g., QR code generation failure)

---

## File Uploads

### QR Code Storage
- **Path:** `/media/product_qr_codes/`
- **Format:** PNG images
- **Naming:** `product_{product_id}_qr.png`
- **Size:** Optimized for scanning (300x300px typical)

### Media Configuration
Ensure your Django settings include:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Relationships

### Database Relationships
- **Product → Shop:** Many-to-One (FK with CASCADE delete)
- **Shop → Product:** One-to-Many (related_name='products')
- **Customer → Product:** One-to-Many (through Shop)

### API Relationships
- Products include shop information and customer details
- Shop endpoints can include product counts and lists
- Customer endpoints can include products across all their shops

---

## Performance Considerations

### Optimizations
- Uses `select_related()` for shop and customer data
- Database indexes on frequently filtered fields
- Pagination for large result sets
- Separate serializers for list vs detail views

### Bulk Operations
- Bulk create supports up to 100 products per request
- Bulk operations include validation and error reporting
- QR codes generated asynchronously for bulk operations

---

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Product created successfully
- `204 No Content` - Product deleted successfully
- `207 Multi-Status` - Bulk operation with some errors
- `400 Bad Request` - Invalid request data or validation errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Product, shop, or related resource not found
- `500 Internal Server Error` - Server error (e.g., QR generation failure)